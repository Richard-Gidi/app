import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

def load_data():
    raw_data = pd.read_csv('Anime.csv').fillna('')
    return raw_data

def preprocess_data(data):
    features = data['Producers'] + ' ' + data['Genres'] + ' ' + data['Studios'] + ' ' + \
               data['Themes'] + ' ' + data['Synopsis'] + ' ' + data['Rating'] + ' ' + \
               data['Demographics'] + data['Japanese'] + ' ' + data['English']
    return features

def get_recommendations(anime_title, data, vectorized_features):
    close_match = data['Title'].apply(lambda x: x.lower()).str.contains(anime_title.lower())
    if not close_match.any():
        return pd.Series(dtype=str)
    anime_ID = close_match.idxmax()
    scores = cosine_similarity(vectorized_features[anime_ID], vectorized_features)
    ranked_indices = np.argsort(scores)[0][::-1]
    recommendations = data.loc[ranked_indices[:50], 'Title']
    return recommendations

data = load_data()
vectorizer = TfidfVectorizer()
vectorized_features = vectorizer.fit_transform(preprocess_data(data))

st.title("Gidi's Anime Recommendation System")
anime_title = st.text_input('Enter an anime title:')
if anime_title:
    recommendations = get_recommendations(anime_title, data, vectorized_features)
    st.write('Anime Recommendations:')
    if not recommendations.empty:
        for i, anime in enumerate(recommendations, start=1):
            st.write(i, '.', anime)
    else:
        st.write('No recommendations found.')
