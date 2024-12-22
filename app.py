import streamlit as st
from joblib import load
import requests

# Load pre-trained models
with open('./ML Model/Extracted_Files/movies.joblib', 'rb') as file:
    movies = load(file)

with open('./ML Model/Extracted_Files/similarity.joblib', 'rb') as file:
    similarity = load(file)

# Ensure the year is in integer format
movies['year'] = movies['year'].astype(int)

# Prepare movie list
movie_list = movies['title'].values
movie_list.sort()

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[:11]
    
    recommended_movies_list = []
    for i in movies_list:
        recommend_movie_dict = dict()
        recommend_movie_dict['title'] = movies.iloc[i[0]].title
        recommend_movie_dict['year'] = movies.iloc[i[0]].year
        recommend_movie_dict['genres'] = movies.iloc[i[0]].genres
        recommend_movie_dict['director'] = movies.iloc[i[0]].director
        recommend_movie_dict['percentage'] = i[1] * 100
        recommended_movies_list.append(recommend_movie_dict)
    
    return recommended_movies_list

# Streamlit title and layout
st.set_page_config(page_title="MovieMentor", layout="wide")

# Apply dark theme and custom colors
st.markdown("""
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .block-container {
            padding: 30px;
        }
        .stButton>button {
            background-color: #6200ea;
            color: white;
            font-size: 16px;
            border-radius: 8px;
            padding: 10px 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #3700b3;
        }
        .stSelectbox>div>div>div>input {
            background-color: #333;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        .stSelectbox>div>div>div>input:focus {
            border-color: #6200ea;
        }
        .stHeader {
            color: #6200ea;
        }
        hr {
            border: 1px solid #6200ea;
        }
        .movie-card {
            background-color: #333;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: box-shadow 0.3s ease;
        }
        .movie-card:hover {
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2);
        }
        .movie-title {
            color: white;
            font-size: 1.5em;
            font-weight: 600;
        }
        .movie-details {
            color: white;
            font-size: 1.1em;
        }
        .similarity {
            font-weight: bold;
            font-size: 1.2em;
        }
        .high-similarity {
            color: yellow;
        }
        .low-similarity {
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<br>
<div style="text-align: center; color: #ffffff; padding: 15px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; border-radius: 10px;">
    <h2 style="font-size: 2em; color: #e2d12a;">MovieMentor</h2>
    <h2 style="font-size: 2em; color: #6200ea;">🎬 Welcome to Your Movie Guide! 🎬</h2>
    <p style="font-size: 1.1em;">
        Select a movie and let our <strong style="color: #ff9800;">AI system</strong> recommend films you'll love.
    </p>
    <p style="font-size: 1.2em; color: #37d67a; font-weight: bold;">
       🌟 Your next favorite movie awaits! 🌟
    </p>
</div>
""", unsafe_allow_html=True)


# Filters
st.sidebar.header("Filter Movies")
selected_genre = st.sidebar.multiselect(
    "Select Genres",
    options=sorted(set([genre for genres in movies['genres'] for genre in genres]))  # Extract unique genres
)

selected_year = st.sidebar.slider(
    "Select Release Year Range",
    min_value=int(movies['year'].min()),
    max_value=int(movies['year'].max()),
    value=(int(movies['year'].min()), int(movies['year'].max())),
)

# Filter movies based on the selected genre and year
filtered_movies = movies
if selected_genre:
    filtered_movies = filtered_movies[filtered_movies['genres'].apply(
        lambda genres: any(genre in genres for genre in selected_genre))]

filtered_movies = filtered_movies[filtered_movies['year'].between(selected_year[0], selected_year[1])]

# Movie selection dropdown with smooth interaction
selected_movie = st.selectbox(
    label="Choose a Movie to Get Recommendations:",
    options=filtered_movies['title'].values,
    index=None,
    help="Choose a movie from the list to get similar movie suggestions."
)

# If a movie is selected
if selected_movie:
    # Get recommendations for the selected movie
    recommended_movies = recommend(selected_movie)

    # If no filters are applied, show all recommendations
    if not selected_genre and not selected_year:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🎬 Your Selected Movie 🎬")
        st.markdown(f"**Title:** {recommended_movies[0]['title']}")
        st.markdown(f"**Release Year:** {recommended_movies[0]['year']}")
        st.markdown(f"**Genres:** {', '.join(recommended_movies[0]['genres'])}")
        st.markdown(f"**Director:** {recommended_movies[0]['director'][0]}")
        st.markdown(f"**Similarity:** {recommended_movies[0]['percentage']:.2f}%")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🔍 Movie Recommendations 🔍")

        for i in range(1, len(recommended_movies)):
            percentage = recommended_movies[i]['percentage']

            card_class = 'high-similarity' if percentage >= 35 else 'low-similarity'

            movie_card = f"""
            <div class="movie-card">
                <h4 class="movie-title">{recommended_movies[i]['title']} ({recommended_movies[i]['year']})</h4>
                <p class="movie-details"><strong>Genres:</strong> {', '.join(recommended_movies[i]['genres'])}</p>
                <p class="movie-details"><strong>Director:</strong> {recommended_movies[i]['director'][0]}</p>
                <p class="similarity {card_class}">Similarity: {percentage:.2f}%</p>
            </div>
            """
            st.markdown(movie_card, unsafe_allow_html=True)

    # If filters are applied, show filtered recommendations
    else:
        filtered_recommended_movies = []
        for movie in recommended_movies:
            # Check if the movie meets the genre and year filter criteria
            if (not selected_genre or any(genre in movie['genres'] for genre in selected_genre)) and \
               (selected_year[0] <= movie['year'] <= selected_year[1]):
                filtered_recommended_movies.append(movie)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🎬 Your Selected Movie 🎬")
        st.markdown(f"**Title:** {recommended_movies[0]['title']}")
        st.markdown(f"**Release Year:** {recommended_movies[0]['year']}")
        st.markdown(f"**Genres:** {', '.join(recommended_movies[0]['genres'])}")
        director = recommended_movies[0]['director'][0] if len(recommended_movies[0]['director']) != 0 else "Not Available"
        st.markdown(f"**Director:** {director}")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            """
            <style>
            .responsive-subheader {
                font-size: calc(1.5rem + 1vw);
                text-align: center;
            }
            </style>
            <h2 class="responsive-subheader">🔍 Movie Recommendations 🔍</h2>
            """,
            unsafe_allow_html=True
        )

        for i in range(1, len(filtered_recommended_movies)):
            percentage = filtered_recommended_movies[i]['percentage']

            card_class = 'high-similarity' if percentage >= 35 else 'low-similarity'

            movie_card = f"""
            <div class="movie-card">
                <h4 class="movie-title" style="color:#5793CD;">{filtered_recommended_movies[i]['title']} ({filtered_recommended_movies[i]['year']})</h4>
                <p class="movie-details"><strong>Genres:</strong> {', '.join(filtered_recommended_movies[i]['genres'])}</p>
                <p class="movie-details"><strong>Director:</strong> {recommended_movies[i]['director'][0] if len(recommended_movies[i]['director']) != 0 else "Not Available"}</p>
                <p class="similarity {card_class}">Similarity: {percentage:.2f}%</p>
            </div>
            """
            st.markdown(movie_card, unsafe_allow_html=True)
