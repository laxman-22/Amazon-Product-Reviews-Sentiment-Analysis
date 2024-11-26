import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

path = "./generated_plots"

os.makedirs(path, exist_ok=True)

data = pd.read_csv('ProductReviews.csv')

review_counts = data.groupby('product_name').size()
review_counts_df = review_counts.reset_index(name='review_count')
ax = sns.histplot(review_counts_df['review_count'])
ax.set_title("Number of Reviews per Product")
ax.set_xlabel("Review Count")
ax.set_ylabel("Count")

plt.savefig('./generated_plots/num_reviews_per_product.png')

plt.clf()
ax = sns.histplot(data['product_rating'])
ax.set_title("Distribution of Product Ratings")
ax.set_xlabel("Product Rating")
ax.set_ylabel("Count")

plt.savefig('./generated_plots/distribution_of_product_ratings.png')

plt.clf()
sia = SentimentIntensityAnalyzer()

data['vader_sentiment'] = data['description'].apply(lambda x: sia.polarity_scores(str(x))['compound'])

data['vader_sentiment_category'] = data['vader_sentiment'].apply(lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral'))

plt.figure(figsize=(8,7))
ax = sns.countplot(data=data, x='vader_sentiment_category')

for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2, height+50, f'{height}', ha='center', va='center', fontsize=10)

plt.title('Sentiment Distribution using VADER')
plt.savefig('./generated_plots/sentiment_distribution_VADER.png')

plt.clf()
data['review_length'] = data['description'].apply(lambda x: len(str(x).split()))

plt.figure(figsize=(10, 6))
sns.scatterplot(x='review_length', y='vader_sentiment', data=data, hue='vader_sentiment_category', palette=['green', 'red', 'gray'], alpha=0.7)

plt.title('Sentiment vs. Review Length')
plt.xlabel('Review Length (words)')
plt.ylabel('Sentiment Score')
plt.savefig('./generated_plots/sentiment_vs_review_len.png')
