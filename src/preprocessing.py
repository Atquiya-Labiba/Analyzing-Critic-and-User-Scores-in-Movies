import pandas as pd
import datetime
import os
import ast

def main():
    merged_df=merge_chunks()
    cleaned_df=eda(merged_df)    
    genre_df=seperate_genre(cleaned_df) 

    #Drop genre from movie_df
    cleaned_df=cleaned_df.drop(columns=["Genres"])

    #Convert both df to csv
    genre_df.to_csv("data/genre.csv",index=False)
    cleaned_df.to_csv("data/movie_details.csv",index=False)

    print("plat",cleaned_df["Award Nominations"].value_counts())



def merge_chunks():
    file_path="data/dataset_chunks"
    
    files=os.listdir(file_path)

    #Sort the file number wise
    file_number=[]
    all_files=[]

    for file_name in files:
        #Remove chunk and .csv
        num=int(file_name.replace("chunk_",'').replace(".csv",''))
        file_number.append((num,file_name))
        
    file_number.sort()
    
    sorted_files=[file for num, file in file_number]
    print(sorted_files)
    for f in sorted_files:
        file_dir=os.path.join(file_path,f)
        df_chunks=pd.read_csv(file_dir)        
        all_files.append(df_chunks)  
    return pd.concat(all_files,ignore_index=True) 



#=============Data Analysis====================
def eda(movie_df):

    #Print first 5 rows
    print(movie_df.head())

    #Print info()
    print(movie_df.info())

    #Print describe()to show descriptive statistics
    print(movie_df.describe())

    #Missing Rows
    missing_rows=movie_df.isnull().sum().sum()

    #Handle missing rows
    if missing_rows > 0:
        print("Dropping missing rows")
        movie_df=movie_df.dropna()
        print(movie_df.isnull().sum())

    #Check if any duplicate value
    print("Duplicate Value Count:", movie_df.duplicated().sum())
    if movie_df.duplicated().sum() > 0:
        print("Duplicate rows:")
        print(movie_df[movie_df.duplicated(keep=False)])
        movie_df=movie_df.drop_duplicates()   

    print("Dataset after removing duplicates")
    print(movie_df.duplicated().sum())
    
    #Convert Release date to correct date format
    movie_df["Release Date"]=pd.to_datetime(movie_df["Release Date"])

    #Convert Duration to correct format
    movie_df["Duration"]=movie_df["Duration"].apply(convert_duration)
    print(movie_df["Duration"])

    #Convert columns having k to numbers
    cols=["User positive counts","User mixed counts","User negative counts"]
    for col in cols:
        movie_df[col]=movie_df[col].apply(convert_to_thousand)
    
    
    ##Convert Metascore columns to int
    movie_df["Metascore"]=movie_df["Metascore"].astype(int)

    print(movie_df.dtypes)

    #Generate Movie ID sequentially
    movie_df.insert(0,"Movie ID",range(1,len(movie_df)+1))
    print(movie_df)

    return movie_df

def convert_duration(duration):
    duration_text = duration.strip() 
    duration_list=duration_text.split()  #[3,h,50,m]
    total_mins=0

    for item in range(0,len(duration_list),2):
        num=int(duration_list[item]) 
        time_unit=duration_list[item+1] #[first index before unit is number part]  

        if time_unit=="h":
            total_mins+=num*60

        elif time_unit=="m":
            total_mins+=num
    return total_mins

def convert_to_thousand(value):
    if pd.isna(value):
        return None
    val = str(value).strip().lower()
    if val.endswith("k"):
        return int(float(val[:-1]) * 1000) #for cases like 3.5k
    else:
        return int(float(val))

def seperate_genre(movie_df):
    genre_df=pd.DataFrame({"Movie ID":movie_df["Movie ID"],"Genres":movie_df["Genres"]})
    genre_df["Genres"]=genre_df["Genres"].apply(ast.literal_eval)

    #Exploding genre
    genre_df=genre_df.explode("Genres")

    print(genre_df)   

    return genre_df

    













if __name__ == "__main__":
    main()


