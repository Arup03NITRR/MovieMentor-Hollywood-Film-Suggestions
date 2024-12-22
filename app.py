import streamlit as st
from joblib import load
import requests

with open('./ML Model/Extracted_Files/movies.joblib', 'rb') as file:
    movies = load(file)

with open('./ML Model/Extracted_Files/similarity.joblib', 'rb') as file:
    similarity = load(file)

movie_list = movies['title'].values
movie_list.sort()



def recommend(movie):
    movie_index=movies[movies['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x: x[1])[:11]
    recommended_movies_list=list()
    for i in movies_list:
        recommend_movie_dict = dict()
        recommend_movie_dict['title'] = movies.iloc[i[0]].title
        recommend_movie_dict['year'] = movies.iloc[i[0]].year
        recommend_movie_dict['genres'] = movies.iloc[i[0]].genres
        recommend_movie_dict['director'] = movies.iloc[i[0]].director
        recommend_movie_dict['percentage'] = i[1]*100
        recommended_movies_list.append(recommend_movie_dict)
    return recommended_movies_list

st.title("Hollywood Movie Recommend System")

selected_movie = st.selectbox(label = "Select Movie", options = movie_list, index=None)

if selected_movie != None:
    recommended_movies = recommend(selected_movie)
    #st.write(f"{recommended_movies[0]['percentage']:.2f}% Similar")
    st.header("Selected movies")
    st.write("<hr>", unsafe_allow_html=True)
    st.write(f"**Title:** {recommended_movies[0]['title']}")
    st.write(f"**Released:** {recommended_movies[0]['year']}")
    genre = ', '.join(recommended_movies[0]['genres'])
    st.write(f"**Genre:** {genre}")

    st.header("Recommended movies")
    st.write("<hr>", unsafe_allow_html=True)
    for i in range(1, len(recommended_movies)):
        if(recommended_movies[i]['percentage']<35):
            st.write(f"<p style='color: red;'>{recommended_movies[i]['percentage']:.2f}% Similar</p>", unsafe_allow_html=True)
        else:
            st.write(f"<p style='color: green;'>{recommended_movies[i]['percentage']:.2f}% Similar</p>", unsafe_allow_html=True)
        st.write(f"**Title:** {recommended_movies[i]['title']}")
        st.write(f"**Released:** {recommended_movies[i]['year']}")
        genre = ', '.join(recommended_movies[i]['genres'])
        st.write(f"**Genre:** {genre}")
        st.write("<hr>", unsafe_allow_html=True)



