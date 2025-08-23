# Analyzing-Critic-and-User-Scores-in-Movies
Every wondered why critics and users sometimes see movies so differently?This project analyzes critic and user scores in movies visualizing trends,score gaps and key insights to uncover interesting patterns.

## Problem Statement
This project aims to scrape movie details from this [website](https://www.metacritic.com/browse/movie/?releaseYearMin=2000&releaseYearMax=2025&page=1) for movies released between 2000 and 2025.After collecting the data, the goal is to identify gaps in the dataset and analyze the factors that may influence them.Approximately 9,000 entries have been scraped.

## Goals and Objective
**Goal:**
Understand the disparity between critic and user reviews in movies

**Objectives:**
- Scrape data about movies using Selenium
- Preprocess, Transform and Manipulate the data using Python
- Visualize insights in Tableau Dashboard for clear interpretation

**Key Questions**
- Is the critic-audience gap increasing or decreasing over time?
- Which genres consistently favor critics vs audiences?
- To what extent do critic and audience ratings align across streaming platforms, and how can this inform platform-specific content strategies?
- How do award-winning films perform in terms of audience alignment?

You can visit the dashboard [here](https://public.tableau.com/app/profile/atquiya.labiba.oni/viz/AnalyzingCriticandUserScoresinMovies/MovieReceptionTrendsGenreAnalysis)
 ## Findings and Observations from the [Dashboard](https://public.tableau.com/app/profile/atquiya.labiba.oni/viz/AnalyzingCriticandUserScoresinMovies/MovieReceptionTrendsGenreAnalysis)
 - There is a convergence trend among critics and users over the 25 years
 - User tend to score higher than critics as almost all genres have negative score gap
 - The largest negative gaps are in Action, Adventure, Family
 - The smaller gap in Horror and Mystery suggest user and critic have positive alignment
 - Gaps decreases as awards increases
 - Hulu platform leans towards critic favored while mainstream platforms align closer to user preferences
 - The data suggests that users are more polarized than critics

## Build From Sources and Run the Selenium Scraper
1. Clone the repo
```bash
git clone https://github.com/Atquiya-Labiba/Analyzing-Critic-and-User-Scores-in-Movies.git
```
2. Intialize and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run the scraper
```bash
python src/scraper.py
```
5. Run the preprocessing file
```bash
python src/preprocessing.py
```
6. You will get movie_details.csv and genre.csv inside data folder. To check our scraped data you can visit [movie_details.csv](https://github.com/Atquiya-Labiba/Analyzing-Critic-and-User-Scores-in-Movies/blob/main/data/movie_details.csv) and [genre.csv](https://github.com/Atquiya-Labiba/Analyzing-Critic-and-User-Scores-in-Movies/blob/main/data/genre.csv)

## Contact
If you have any queries you can contact me here: atquiyaoni@gmail.com
