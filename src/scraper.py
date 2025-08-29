from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ProcessPoolExecutor
from selenium.webdriver.chrome.options import Options
import time
import random
import pandas as pd
import os

def driver_initialization():
    
    options = Options()
    options.headless = True    
    options.add_argument("--log-level=3")  
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  
    
    return(webdriver.Chrome( options=options))

def get_all_urls(driver):
    web_url="https://www.metacritic.com/browse/movie/?releaseYearMin=2000&releaseYearMax=2025&page=1"

    driver.get(web_url)
    urls=[]
    while True:
        time.sleep(2)
        cards=driver.find_elements(By.CSS_SELECTOR, '[data-testid="filter-results"]')       

        for card in cards: 
            try:           
                movie_url=card.find_element(By.TAG_NAME, "a").get_attribute("href")
                urls.append(movie_url)                
            except NoSuchElementException:
                movie_url=None

        #Traverse Next Page Cards
        try:
            next_page=driver.find_element(By.CSS_SELECTOR,"span.c-navigationPagination_item--next.enabled")
            next_page.click()
            time.sleep(2)
        except:            
            break
    return [url for url in urls if "/movie/" in url] #Just return valid movie urls

def navigate_url(url):

    driver=driver_initialization()
    
    try:
        movie_details = scrape_details(driver, url)
        critic_reviews = scrape_metascore_details(driver, url)
        user_reviews = scrape_userscore_details(driver, url)        

        #Skip movies where either of the scores missing
        if not critic_reviews or not user_reviews or not movie_details:
            return None
        merged_dict={**movie_details, **critic_reviews, **user_reviews}        

        time.sleep(random.uniform(1, 2))
        return merged_dict
    except Exception as e:
        print(f"Error in processing URL: {e}")
        
    finally:
        driver.quit()


def scrape_details(driver,url):
    
    movie_info={}

    driver.get(url)
    time.sleep(1)

    #Scrape Title of the Movie
    try:
        title_container=driver.find_element(By.CSS_SELECTOR, '[data-testid="hero-title"]')
        movie_info['Title']=title_container.find_element(By.TAG_NAME, 'h1').text       

    except NoSuchElementException:
       movie_info['Title']=None

    #Scrape Streaming Platform for the Movie
    try:
        platform_container=driver.find_element(By.CSS_SELECTOR, '[data-testid="hero-metadata"]')
        ul_items=platform_container.find_element(By.TAG_NAME, 'ul')
        list_items=ul_items.find_elements(By.CLASS_NAME, 'c-heroMetadata_item')        

        platform_item = None
        #Check if li item has <a> tag 
        for li in list_items:
            a_tag = li.find_elements(By.TAG_NAME, 'a')
            if a_tag:
                platform_item = li
                break                  

        if platform_item:
            link = platform_item.find_element(By.TAG_NAME, 'a')
            #Extract the text from <a> tag to get Platform Name
            movie_info['Streaming Platform'] = link.get_attribute("textContent").strip()
        else:
            movie_info['Streaming Platform'] = None

    except NoSuchElementException:
        movie_info['Streaming Platform'] = []    

    #Scrape details card
    ##Find details section
    detail_section = driver.find_elements(By.CSS_SELECTOR, "div.c-movieDetails_sectionContainer") 

    if not detail_section:
        return None

    for sec in detail_section: 
            try:       
                label_span = sec.find_element(By.TAG_NAME, "span")
                label = label_span.text.strip()

            except NoSuchElementException:
                continue

            if label == "Release Date":                
                spans = sec.find_elements(By.TAG_NAME, "span")
                movie_info['Release Date'] = spans[1].text.strip()

            elif label == "Duration":                
                spans = sec.find_elements(By.TAG_NAME, "span")
                movie_info['Duration'] = spans[1].text.strip()      

        
            elif label == "Genres":
                try:
                    ul = sec.find_element(By.TAG_NAME, "ul")      
                    li_items = ul.find_elements(By.TAG_NAME, "li")
                    movie_info['Genres'] = [li.find_element(By.TAG_NAME, "span").text.strip() for li in li_items]
                except:
                    movie_info['Genres']=[]            

    #Scrape Award details
    try:
        award_cont=driver.find_element(By.CLASS_NAME, "c-productionAwardSummary_awards")
        award_part = award_cont.find_elements(By.CSS_SELECTOR, ".c-productionAwardSummary_award")
        total_wins=0
        total_nom_wins=0
        for award in award_part:          
            win_nom=award.find_elements(By.CSS_SELECTOR, "div")[1].text.strip()            

            #Extract wins and nominations in numbers from .1 Wins & 1 Nominations
            award_summary=win_nom.split("&")
            numbers=0
            for item in award_summary:
                values=item.strip().split()
                numbers=0
                for i in values:
                    if i.isdigit():
                        numbers=int(i)
                    elif "Win" in i:
                        total_wins+=numbers
                    elif "Nominations" in i or "Nomination" in i:
                        total_nom_wins+=numbers
        movie_info["Award Wins"]=total_wins
        movie_info["Award Nominations"]=total_nom_wins

    except NoSuchElementException:        
        movie_info["Award Wins"]=0
        movie_info["Award Nominations"]=0

    return movie_info

def scrape_metascore_details(driver,url):

    driver.get(url)
    time.sleep(1)

    critic_rev_details = {}        
    try:
        critic_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="critic-score-info"]')        
        cont_div=driver.find_element(By.CLASS_NAME, "c-siteReviewScore_background-critic_medium")
        score_span = cont_div.find_element(By.TAG_NAME, "span")
        critic_rev_details['Metascore'] = score_span.text        

    except NoSuchElementException:
        critic_rev_details['Metascore'] = None    

    #Critic Category
    try:        
        critic_category_cls=critic_container.find_element(By.CLASS_NAME, "c-productScoreInfo_scoreSentiment")
        critic_rev_details['Critic Category'] = critic_category_cls.text

    except NoSuchElementException:
        critic_rev_details['Critic Category']=None

    #Getting review url
    try:
        critic_rev_url=driver.find_element(By.CSS_SELECTOR,"span.c-productScoreInfo_reviewsTotal a").get_attribute("href")

    except NoSuchElementException:        
        print("No user review URL found. Skipping critic season scraping.")
        return None           

    #Navigate to the Critic Review page
    driver.get(critic_rev_url)
    time.sleep(1)   

    try:
        critic_score_containers = driver.find_element(By.CSS_SELECTOR, "div.c-scoreCount_container.u-grid")
        labels = critic_score_containers.find_elements(By.CSS_SELECTOR, "div.c-scoreCount_text")
        counts = critic_score_containers.find_elements(By.CSS_SELECTOR, "div.c-scoreCount_count")        
        
    except NoSuchElementException:
        critic_score_containers=None


    for label, count in zip(labels, counts):
        sentiments = label.text.strip().lower() # Will give positive,mixed,negative           
        spans = count.find_elements(By.TAG_NAME, "span")
        
        # Default values if spans are missing
        rev_count = spans[0].text 
        rev_pct = spans[1].text.strip("()%") 
        
        critic_rev_details[f"Critic {sentiments} counts"] = rev_count
        critic_rev_details[f"Critic {sentiments} percentage"] = rev_pct 
    

    return critic_rev_details

def scrape_userscore_details(driver,url):
    driver.get(url)
    time.sleep(1)

    user_rev_details = {}

    try:
    # Select the main container
        user_container = driver.find_element(By.CSS_SELECTOR, "div.c-productScoreInfo[data-testid='user-score-info']")
        try:            
            user_rev_details["User Score Category"] = user_container.find_element(By.CSS_SELECTOR, "div.c-productScoreInfo_text span.c-productScoreInfo_scoreSentiment").text

        except NoSuchElementException:
            user_rev_details["User Score Category"]=None

        try:
            user_rev_details["User Score"] = user_container.find_element(By.CSS_SELECTOR, "div.c-productScoreInfo_scoreNumber span").text

        except NoSuchElementException:
             user_rev_details["User Score"]=None

    except NoSuchElementException:
        pass

          
    # Getting review url 
    try:
        user_rev_url=user_container.find_element(By.CSS_SELECTOR,"span.c-productScoreInfo_reviewsTotal a").get_attribute("href")        

    except NoSuchElementException:
        print("No user review URL found")
        return None
    #Navigate to the User Review page
    driver.get(user_rev_url)
    time.sleep(1)        

    try:
        user_score_container = driver.find_element(By.CSS_SELECTOR, "div.c-scoreCount_container.u-grid")
        labels = user_score_container.find_elements(By.CSS_SELECTOR, "div.c-scoreCount_text")
        counts = user_score_container.find_elements(By.CSS_SELECTOR, "div.c-scoreCount_count")           
        
    except NoSuchElementException:
        user_score_container= None
    

    for label, count in zip(labels, counts):
        sentiments = label.text.strip().lower()             
        spans = count.find_elements(By.TAG_NAME, "span")
        
        rev_count = spans[0].text 
        rev_pct = spans[1].text.strip("()%") 

        user_rev_details[f"User {sentiments} counts"] = rev_count
        user_rev_details[f"User {sentiments} percentage"] = rev_pct   
        

    return user_rev_details

def save_chunks(data,chunk_id):
    df = pd.DataFrame(data)    
    # Save to CSV
    filename = f"chunk_{chunk_id}.csv"
    folder_path="data/dataset_chunks"
    os.makedirs(folder_path, exist_ok=True)    
    file_full_path=os.path.join(folder_path,filename)
    df.to_csv(file_full_path, index=False)
    print(f"Saved {len(df)} rows to {filename}")    

def chunk_dataset(url_list,size):
    for i in range(0,len(url_list),size):
        yield url_list[i: i+size]





def main():

    #Initialize the driver
    driver=driver_initialization()

    movie_all_urls=[]
    all_urls=get_all_urls(driver)   

    movie_all_urls=all_urls  
            
        
    
    with ProcessPoolExecutor(max_workers=5) as executor:        
        for index, url_chunk in enumerate(chunk_dataset(movie_all_urls, size=500), start=1):            
            results = executor.map(navigate_url, url_chunk)
            chunk_data=[]
            for url, movie in zip(url_chunk, results):
                if movie is None:
                    print(f"Skipped movie at {url}")
                else:
                    chunk_data.append(movie)

            #Save data for chunks
            save_chunks(chunk_data, index)              
    

if __name__ == "__main__":
    main()