import streamlit as st
from joblib import load

# Load pre-trained models
movies = load('./ML Model/Extracted_Files/movies.joblib')
similarity = load('./ML Model/Extracted_Files/similarity.joblib')

# Ensure proper data types
movies['year'] = movies['year'].astype(int)
movies['genres'] = movies['genres'].apply(lambda x: x.split(", ") if isinstance(x, str) else x)
movies['director'] = movies['director'].apply(lambda x: x.split(", ") if isinstance(x, str) else x)

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    recommended_indices = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:11]

    recommendations = []
    for idx, score in recommended_indices:
        recommendations.append({
            "title": movies.iloc[idx]['title'],
            "year": movies.iloc[idx]['year'],
            "genres": movies.iloc[idx]['genres'],
            "director": movies.iloc[idx]['director'],
            "percentage": score * 100,
        })
    return recommendations

# Streamlit App
st.set_page_config(page_title="MovieMentor", layout="wide")

# Custom CSS for professional styling with dark and light mode support
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
        }
        .app-header {
            text-align: center;
            padding: 20px;
            background-color: #6200ea;
            color: white;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 15px;
        }
        .movie-title {
            font-size: 20px;
            color: #333;
        }
        .movie-details {
            font-size: 14px;
            color: #666;
        }
        .filters {
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 20px;
        }
        .recommended-movies {
            margin-top: 20px;
        }
        /* Dark mode adjustments */
        @media (prefers-color-scheme: dark) {
            body {
                background-color: #121212;
                color: #fff;
            }
            .app-header {
                background-color: #6200ea;
                color: white;
            }
            .card {
                background: #333;
                border-color: #555;
            }
            .movie-title {
                color: #f0f0f0;
            }
            .movie-details {
                color: #ccc;
            }
            .filters {
                background: #333;
                border-color: #444;
            }
            .recommended-movies {
                color: #fff;
            }
            .similarity-green {
                color: #4caf50; /* Green for dark mode */
            }
            .similarity-red {
                color: #f44336; /* Red for dark mode */
            }
        }
        /* Light mode adjustments */
        @media (prefers-color-scheme: light) {
            .similarity-green {
                color: #388e3c; /* Green for light mode */
            }
            .similarity-red {
                color: #d32f2f; /* Red for light mode */
            }
        }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("<div class='app-header'><h1>🎥 MovieMentor 🎥</h1><p style='text-align: centre;'>🍿 Explore Movies Like Never Before! 🍿</p></div>", unsafe_allow_html=True)

# Search Box for Movie Selection
movie_lists = list(movies['title'].values)
movie_lists = sorted(movie_lists)
selected_movie = st.selectbox("🔎 Search for a Movie", [""] + movie_lists, index=0)

# If a movie is selected
if selected_movie and selected_movie != "":
    st.markdown("<hr>", unsafe_allow_html=True)

    # Display Selected Movie
    movie_details = movies[movies['title'] == selected_movie].iloc[0]
    st.markdown(f"""
    <div class='card'>
        <h3 class='movie-title'>🎬 {movie_details['title']}</h3>
        <p class='movie-details'><strong>📅 Release Year:</strong> {movie_details['year']}</p>
        <p class='movie-details'><strong>🎞 Genres:</strong> {', '.join(movie_details['genres'])}</p>
        <p class='movie-details'><strong>👨‍💼 Director:</strong> {', '.join(movie_details['director']) if movie_details['director'] else 'N/A'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Get Recommendations
    recommendations = recommend(selected_movie)

    # Sidebar Filters
    st.sidebar.header("🎯 Filter Recommendations")
    selected_genres = st.sidebar.multiselect(
        "Select Genres",
        sorted(set(genre for sublist in movies['genres'] for genre in sublist)),
    )
    selected_year_range = st.sidebar.slider(
        "Year Range",
        int(movies['year'].min()),
        int(movies['year'].max()),
        (1990, 2023),
    )

    # Apply Filters to Recommendations
    filtered_recommendations = recommendations
    if selected_genres:
        filtered_recommendations = [
            rec for rec in filtered_recommendations if any(genre in rec['genres'] for genre in selected_genres)
        ]
    filtered_recommendations = [
        rec for rec in filtered_recommendations if selected_year_range[0] <= rec['year'] <= selected_year_range[1]
    ]

    # Display Recommendations
    st.markdown("<div class='recommended-movies'><h2>🎦 Recommended Movies 🎦</h2></div>", unsafe_allow_html=True)

    if filtered_recommendations:
        for rec in filtered_recommendations:
            # Conditional styling for similarity score
            similarity_class = "similarity-green" if rec['percentage'] >= 35 else "similarity-red"
            st.markdown(f"""
            <div class='card'>
                <h4 class='movie-title'>🎬{rec['title']} ({rec['year']})</h4>
                <p class='movie-details'><strong>🎞 Genres:</strong> {', '.join(rec['genres'])}</p>
                <p class='movie-details'><strong>👨‍💼 Director:</strong> {', '.join(rec['director']) if rec['director'] else 'N/A'}</p>
                <p class='movie-details {similarity_class}' style="font-weight: bold;">Similarity Score: {rec['percentage']:.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: red;'>No recommendations match the selected filters.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color: gray;'>Please select a movie to see recommendations.</p>", unsafe_allow_html=True)
