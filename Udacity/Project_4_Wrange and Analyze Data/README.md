# Project 5: Wrangle and Analyze Data

## Description
In this project, I will analyze the data from [WeRateDogs](https://twitter.com/dog_rates "WeRateDogs Twitter"). 

The dataset contains information about @dog_rates tweets (tweet ID, timestamp, text,etc.) for all 5000+ of their tweets since August1, 2017. Ratings come in a special format: they almost always have a denominator of 10. The numerators are usually are higher than 10. 11/10, 12/10, 13/10, etc.

The goal is to wrangle WeRateDogs Twitter data to create interest analyses and visualizations.

## Procedures

### Data
The WeRateDogs Twitter archive contains basic tweet data for all 5000+ of their tweets, but not everything. This data is not high quality data. I will need to assess it and clean it to use it for analysis and visualization.

A lot of the missing data will be gathered from Twitter's API.

A file of image predictions is also included. This file includes a jpg image of the predicted dog, the predicted breed and the confidence of the prediction.

* This data will be gathered in a Juptyter Notebook titled _wranle_act.ipynb_.
* The WeRateDogs Twitter archive is stored in a file called _twitter-archive-enhanced.csv_.
* The tweet image predictions are hosted on Udacity's server under the name _image_predictions.tsv_ and should be retrieved programatically.
* All data related to tweets will be stored in a  file called _tweet_json.txt_.
* Cleaned dataframes will be stored in a file named _twitter_archive_master.csv_.

### Libraries and software used
The whole project will be developed in a Jupyter Notebook with the following libraries:
* pandas
* NumPy
* requests
* tweepy
* json

The edition of text will be done with Notepad++. In case of needing something more powerful, MS Word will be the tool chosen.

### Keypoints
* I will only work with the original ratings (no retweets).
* In order to pass the project, I will only need to assess and clean 8 quality issues and 2 tidiness issues.
* Cleaning includes merging individual pieces of data.
* The fact that the rating numerators are greater than the denominators does not need to be cleaned.
* I do not need to gather tweets beyond August 1st, 2017.