import streamlit as st
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import tensorflow as tf
import pickle

file_path = 'D:/University/Sem 3/Algorithmic Digital Marketing/Final Project/Movies_EDA.csv'

# Read the CSV file into a DataFrame
Movies_EDA = pd.read_csv(file_path)

# Load the Tokenizer
with open('tokenizer.pickle', 'rb') as handle:
    loaded_tokenizer = pickle.load(handle)

# Load the Model
loaded_model = tf.keras.models.load_model('word_prediction_model.h5')

# Extract movie titles
titles = Movies_EDA['title'].tolist()

# Tokenize the titles
tokenizer = Tokenizer()
tokenizer.fit_on_texts(titles)
total_words = len(tokenizer.word_index) + 1

# Create input sequences and labels
input_sequences = []
for line in titles:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

max_sequence_length = max([len(x) for x in input_sequences])
input_sequences = pad_sequences(input_sequences, maxlen=max_sequence_length, padding='pre')



def generate_next_word(seed_text, n_words):
    for _ in range(n_words):
        token_list = loaded_tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_length-1, padding='pre')
        predicted_probabilities = loaded_model.predict(token_list, verbose=0)
        predicted = int(tf.argmax(predicted_probabilities, axis=-1))
        output_word = ""
        for word, index in loaded_tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += " " + output_word
    return seed_text

# Streamlit App
st.title("Movie Recommendation Wizard")

# User Input
seed_text = st.text_input("Enter a seed text:", "")
num_words = st.slider("Number of words to predict:", 1, 10, 3)

# Generate Predictions
if st.button("Generate Predictions"):
    predicted_text = generate_next_word(seed_text, num_words)
    st.markdown(f"**Predicted Text:** {predicted_text}")

predicted_text = generate_next_word(seed_text, num_words)

#Convert movie name to title case
def convert_to_title_case(text):
    return ' '.join(word.capitalize() for word in text.split())


text = predicted_text
title_case_text = convert_to_title_case(text)
print(title_case_text)

#Movie Predictor App


# Load processed_movies DataFrame
processed_movies = pd.read_pickle('D:/University/Sem 3/Algorithmic Digital Marketing/Final Project/movie_recommender_processed_data.pkl')

# Load CountVectorizer model
with open('D:/University/Sem 3/Algorithmic Digital Marketing/Final Project/count_vectorizer_model.pkl', 'rb') as file:
    cv = pickle.load(file)

# Load cosine similarity matrix
with open('D:/University/Sem 3/Algorithmic Digital Marketing/Final Project/cosine_similarity_matrix.pkl', 'rb') as file:
    similarity = pickle.load(file)

def recommend(movie):
    try:
        index = processed_movies[processed_movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies = [processed_movies.iloc[i[0]].title for i in distances[1:6]]
        return recommended_movies
    except IndexError:
        return f"Movie '{movie}' not found in the dataset. Unable to provide recommendations."

# Streamlit UI
#st.title("Movie Recommender System")

# User input for movie title
movie_input = title_case_text

if st.button("Get Recommendations"):
    if movie_input:
        recommendations = recommend(movie_input)
        if isinstance(recommendations, list):
            st.success("Top Recommendations:")
            for i, recommendation in enumerate(recommendations, start=1):
                st.write(f"{i}. {recommendation}")
        else:
            st.warning(recommendations)
    else:
        st.warning("Please enter a movie title.")



# Optional: Display the model summary
#st.subheader("Model Summary")
#st.text(loaded_model.summary())
