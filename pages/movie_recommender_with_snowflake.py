import streamlit as st
import pandas as pd
import json
from sqlalchemy import create_engine

# Streamlit page configuration - this must be the first Streamlit command
st.set_page_config(page_title="Movie Recommender System", layout="wide")

# Snowflake connection parameters
snowflake_username = 'admteamseven'
snowflake_password = 'Helloadmteamseven1'
snowflake_account = 'bvizhln-od41629'
snowflake_database = 'movies'
snowflake_schema = 'movie_schema'

# Create a Snowflake SQLAlchemy engine
snowflake_connection_string = f'snowflake://{snowflake_username}:{snowflake_password}@{snowflake_account}/{snowflake_database}/{snowflake_schema}'
engine = create_engine(snowflake_connection_string)

# Function to execute SQL queries
def execute_query(query):
    with engine.connect() as conn:
        result = conn.execute(query)
        data = result.fetchall()
    return data

# Load your movie data from Snowflake
query = "SELECT * FROM MOVIES.MOVIE_SCHEMA.MOVIES"
movies = pd.DataFrame(execute_query(query), columns=['budget', 'genres', 'homepage', 'id', 'keywords', 'original_language', 'original_title', 'overview', 'popularity', 'production_companies', 'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'status', 'tagline', 'title', 'vote_average', 'vote_count'])

# Function to parse genres and languages from JSON format
def parse_json_column(data, key):
    if pd.isnull(data):
        return []
    return [item[key] for item in json.loads(data)]

# Applying the parse_json_column function to genres and languages
movies['parsed_genres'] = movies['genres'].apply(lambda x: parse_json_column(x, 'name'))
movies['parsed_languages'] = movies['spoken_languages'].apply(lambda x: parse_json_column(x, 'name'))

# Compiling unique sets of genres and languages
all_genres = set()
all_languages = set()
for genres_list, languages_list in zip(movies['parsed_genres'], movies['parsed_languages']):
    all_genres.update(genres_list)
    all_languages.update(languages_list)

# Converting sets to sorted lists
final_genres_list = sorted(list(all_genres))
final_languages_list = sorted(list(all_languages))

# Sidebar for user inputs
st.sidebar.header("Customize Your Movie Selection")

# Genre dropdown
genre_choice = st.sidebar.selectbox("Genre", options=final_genres_list)

# Average vote slider
vote_range = st.sidebar.slider("Average Vote", 0.0, 10.0, (5.0, 10.0))

# Spoken language dropdown
language_choice = st.sidebar.selectbox("Spoken Language", options=final_languages_list)

# Main page display
st.markdown("<h1 style='color: blue;'>Welcome to the Movie Recommender System</h1>", unsafe_allow_html=True)

# Button to get recommendations
if st.sidebar.button("Discover Movies"):
    # Filter the movies based on the genre, language, and average vote selected by the user
    filtered_movies = movies[
        movies['parsed_genres'].apply(lambda genres: genre_choice in genres) &
        movies['parsed_languages'].apply(lambda languages: language_choice in languages) &
        (movies['vote_average'] >= vote_range[0]) &
        (movies['vote_average'] <= vote_range[1])
    ]
    
    # Display all filtered movies
    if not filtered_movies.empty:
        for index, row in filtered_movies.iterrows():
            st.subheader(row['title'])
            st.write(row['overview'])
    else:
        st.write("No movies found that match your preferences.")
