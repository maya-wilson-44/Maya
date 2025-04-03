import requests
import json
import streamlit as st
from newsapi import NewsApiClient
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import pandas as pd
import seaborn as sns
import plotly.express as px
import time

# Initialize the News API client
api = NewsApiClient(api_key='d37311fba2474cbd9d2495610d91d547')

# Streamlit app title
st.title("News Dashboard")

# Sidebar for user input
st.sidebar.title("News Filters")
keyword = st.sidebar.text_input("Search Keyword", "stocks")
source = st.sidebar.selectbox("News Source", ["bbc-news", "cnn", "fox-news", "the-verge"])

# Function to fetch data with retry mechanism
def fetch_data(api_call, retries=3, delay=5):
    for i in range(retries):
        try:
            return api_call()
        except requests.exceptions.ConnectionError as e:
            st.warning(f"Connection error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    st.error("Failed to fetch data after multiple attempts.")
    return None

# Fetch and display top headlines
st.header("Top Headlines")
top_headlines = fetch_data(lambda: api.get_top_headlines(sources=source))
if top_headlines:
    st.json(top_headlines)

# Fetch and display news based on keyword
st.header(f"News Articles about {keyword}")
everything = fetch_data(lambda: api.get_everything(q=keyword))
if everything:
    st.json(everything)

# Fetch and display news sources
st.header("News Sources")
sources = fetch_data(api.get_sources)
if sources:
    st.json(sources)

# Visualization: Word Cloud of headlines
st.header("Word Cloud of Headlines")
if top_headlines and 'articles' in top_headlines:
    headlines = ' '.join([article['title'] for article in top_headlines['articles']])
    if headlines:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(headlines)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)
    else:
        st.write("No headlines to display in the word cloud.")
else:
    st.write("No articles found for the selected source.")

# Visualization: Bar Chart of article counts by source
st.header("Bar Chart of Article Counts by Source")
if everything and 'articles' in everything:
    articles_df = pd.DataFrame(everything['articles'])
    source_counts = articles_df['source'].apply(lambda x: x['name']).value_counts()
    fig, ax = plt.subplots()
    sns.barplot(x=source_counts.index, y=source_counts.values, ax=ax)
    ax.set_title("Number of Articles by Source")
    ax.set_xlabel("Source")
    ax.set_ylabel("Number of Articles")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)  # Rotate the x-axis labels
    st.pyplot(fig)
else:
    st.write("No articles found for the keyword.")

# Visualization: Line Chart of article counts over time
st.header("Line Chart of Article Counts Over Time")
if everything and 'articles' in everything:
    articles_df['publishedAt'] = pd.to_datetime(articles_df['publishedAt'])
    articles_df.set_index('publishedAt', inplace=True)
    articles_df = articles_df.resample('D').size()
    fig = px.line(articles_df, x=articles_df.index, y=articles_df.values, title="Article Counts Over Time")
    st.plotly_chart(fig)
else:
    st.write("No articles found for the keyword.")
