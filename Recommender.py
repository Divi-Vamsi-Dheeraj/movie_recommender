import streamlit as st
import pickle
import pandas as pd
import requests

# very imp this is to set the page in full screen wide
st.set_page_config(layout="wide")
def fetch_extras(movie_ids):
    recommended_movie_budgets = []
    recommended_movie_revenues = []
    recommended_movie_links = []

    for id in movie_ids:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=e3fa2e663af675c73ca11e5f71223360')
        data = response.json()
        recommended_movie_links.append(data.get('homepage', '#'))
        recommended_movie_budgets.append(data.get('budget'))
        recommended_movie_revenues.append(data.get('revenue'))
    return (recommended_movie_budgets,
            recommended_movie_revenues,
            recommended_movie_links)

def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=e3fa2e663af675c73ca11e5f71223360')
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path')

def recommend_by_name(movie,selected_genres,selected_release_dates):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]

    recommended_movie_ids = []
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movie_genres = []
    recommended_movie_dates = []
    recommended_movie_cast = []
    recommended_movie_director = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_genres = movies.iloc[i[0]].genres
        movie_release_date = movies.iloc[i[0]].release_date

        if (not selected_genres or all(genre in movie_genres for genre in selected_genres)) and \
           (not selected_release_dates or movie_release_date <= selected_release_dates):
            recommended_movie_ids.append(movie_id)
            recommended_movies_posters.append(fetch_poster(movie_id))  # Fetching poster from API
            recommended_movies.append(movies.iloc[i[0]].title) #For movie recommendation
            recommended_movie_genres.append(movie_genres) # For genres
            recommended_movie_dates.append(movie_release_date) # For release date
            recommended_movie_cast.append(movies.iloc[i[0]].cast)
            recommended_movie_director.append(movies.iloc[i[0]].director)

        if len(recommended_movies) >= 5:
            break

    return (recommended_movie_ids,
            recommended_movies,
            recommended_movies_posters,
            recommended_movie_genres,
            recommended_movie_dates,
            recommended_movie_cast,
            recommended_movie_director)

def recommend_by_popularity(selected_genres,selected_release_dates):
    movies_list = movies.sort_values(by='popularity',ascending=False)

    recommended_movie_ids = []
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movie_genres = []
    recommended_movie_dates = []
    recommended_movie_cast = []
    recommended_movie_director = []

    for index,row in movies_list.iterrows():
        movie_id = row['movie_id']
        movie_genres = row['genres']
        movie_release_date = row['release_date']

        if (not selected_genres or all(genre in movie_genres for genre in selected_genres)) and \
                (not selected_release_dates or movie_release_date <= max(selected_release_dates)):
            recommended_movie_ids.append(movie_id)
            recommended_movies_posters.append(fetch_poster(movie_id))  # Fetching poster from API
            recommended_movies.append(row['title'])  # For movie recommendation
            recommended_movie_genres.append(movie_genres)  # For genres
            recommended_movie_dates.append(movie_release_date)  # For release date
            recommended_movie_cast.append((row['cast']))
            recommended_movie_director.append(row['director'])

        if len(recommended_movies) >= 5:
            break

    return (recommended_movie_ids,
            recommended_movies,
            recommended_movies_posters,
            recommended_movie_genres,
            recommended_movie_dates,
            recommended_movie_cast,
            recommended_movie_director)

def get_recommendations(ids,names,posters,genres,dates,casts,directors):
    budgets, revenues, links = fetch_extras(ids)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.header("Movie:")
    with col2:
        st.header("Genres:")
    with col3:
        st.header("Release Date:")
    with col4:
        st.header("Box Office")
    with col5:
        st.header("Cast")
    with col6:
        st.header("Director")

    st.divider()
    for name, poster, genres, date, budget, cast, director, revenue, link in zip(names, posters, genres, dates, budgets, casts, directors, revenues,
                                                                 links):

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            if link and link != '#':
                st.markdown(f"### [{name}]({link})")
            else:
                st.markdown(f"### {name}")
            st.image(poster)

        with col2:
            st.text("")

        with col3:
            st.subheader(date)

        with col4:
            st.subheader("Budget")
            st.text(f"${budget:,}")
            st.subheader("Revenue")
            st.text(f"${revenue:,}")
            st.subheader("Total Box Office")
            st.text(f"${revenue - budget:,}")

        with col5:
            st.text("")

        with col6:
            st.text("")
            for i in director:
                st.text(i)

        with col2:
            for i in genres:
                st.text(i)
                st.text("")

        with col5:
            for actor in cast:
                st.text(actor)
                st.text("")
        st.divider()

# open all the imported files
movies_dict = pickle.load(open('movies_dict_genres_revised.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity_genres_revised.pkl','rb'))

# main content
st.title('🎬 Movie Recommender System')
st.divider()
st.subheader('Get movie recommendations based on your favorite movies, genres, and release dates')
st.text("")
col1,col2,col3 = st.columns(3)

with col1:
    selected_movie_name = st.selectbox(
    'Search by movie name:',
    movies['title'].values)

with col2:
    all_genres = movies['genres'].explode().unique()
    selected_genres = st.multiselect(
        'Select Your favorite genres:',
        all_genres)

with col3:
    release_dates = sorted(movies['release_date'].unique())
    selected_release_date = st.multiselect(
        'Select Release Date:',
        release_dates)

button_col1,button_col2 = st.columns(2)

with button_col1:
    st.subheader("Get movie recommendations on basis of movie")
    recommend_by_name_button = st.button('Recommend by Name')

with button_col2:
    st.subheader("Get movie recommendations on basis of popularity")
    recommend_by_popularity_button = st.button("Recommend by popularity")

if recommend_by_name_button:
    ids,names,posters,genres,dates,casts,directors = recommend_by_name(selected_movie_name,selected_genres,selected_release_date)
    get_recommendations(ids,names,posters,genres,dates,casts,directors)

if recommend_by_popularity_button:
    ids,names,posters,genres,dates,casts,directors= recommend_by_popularity(selected_genres, selected_release_date)
    get_recommendations(ids,names,posters,genres,dates,casts,directors)