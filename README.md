# Amazon Reviews Sentiment Analysis Dataset


## Description
This repository contains the code that was used to scrape Amazon for their product reviews in the Electronics department.

The dataset is available on [Kaggle](https://www.kaggle.com/datasets/laxman22/amazon-product-reviews-for-sentiment-analysis) and this repository can be used to extend the functionality of this dataset. Unit tests are also present in the ```unittests.py``` file.

In order to run this code successfully, you must download the dataset from Kaggle with the name ```ProductReviews.csv``` and create another empty file named ```links.csv``` in order for the scraper to keep track of the links traversed so the scraper can continue where it left off in case of any interruptions.

The ```exploratory_data_analysis.py``` can be used to visualize some of the data analysis performed on this dataset to get a sense of what the dataset consists of.

The ```webscraper.py``` file can then be used and adapted to run the web scraper and expand on the dataset if necessary. The code will need to be changed in order to run successfully.

## Executive Summary

### Motivation
The motivation for curating this dataset came from researching existing publicly available datasets for performing sentiment analysis on Amazon products as this is valuable information for sellers and buyers.

There was an existing dataset that had Amazon reviews for training NLP (Natural Language Processing) models and other datasets that just had star ratings.

This inspired the creation of a more comprehensive dataset that tracks not only the reviews and the ratings they gave, but also the products that correspond to the reviews as well as the overall rating of the product and the number of ratings for that product.

While there isn't a ton of data present in this dataset, it provides a solid foundation to build off of and continue expanding the dataset.

### Applications
There are some key ways that this dataset can be applicable, primarily in 2 of the following ways provided a model could be trained on this dataset successfully. This could provide buyers and sellers with detailed analytics on how certain products perform and common complaints.

1) Suppose a seller would like to analyze their store's performance (or a competitors' performance). This model could provide information for specific products that were successful. For example, maybe a seller that sells phone cases sees that their iPhone 15 cases sold the most in their store, they would be able to dig into that specific product and pinpoint what exactly customers liked about the case. It's possible a manufacturing process changed for the iPhone 15 cases that customers mention with "better quality" in their reviews which is a good sign to continue doing so for other products. Maybe customers complained of poor shipping time or quality, which tells the seller exactly what to change to improve customer satisfaction.

2) As a buyer, if I could run a browser extension that could show me what the most common complaints are for a product, it would streamline the purchasing process for me. Furthermore, if people who are not well-versed in technology come across a product they like, this model could tell this person that a certain feature was missing or poorly executed according to customer feedback.


## Power Analysis


## Exploratory Data Analysis


## Ethics Statement

## Instructions


## License

