#!/usr/bin/env python
# coding: utf-8

# In[482]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import re


# In[483]:


apollo_tag = 'x03gq'.upper()


# In[484]:


def get_theaters(movie):
    return [theater['th'] for theater in movie['theaters']]

def at_apollo(movie):
    return apollo_tag in get_theaters(movie)

def apollo_start_date(movie):
    for theater in movie['theaters']:
        if theater['th'] == apollo_tag:
            return theater['startDate']

def simplify_trailer(trailers):
    options = [link for link in trailers.values() if link is not None]
    if len(options) >= 1:
        return options[0]
    else:
        return None


# In[485]:


def get_screenings(movies):
    movies = ['"' + movie + '"' for movie in movies]
    headers = {
        'content-type': 'text/plain;charset=UTF-8'
    }

    front_cutoff = '2000-01-01'
    back_cutoff = '2050-01-01'

    front_cutoff = datetime.datetime.strptime(front_cutoff, '%Y-%m-%d')
    back_cutoff = datetime.datetime.strptime(back_cutoff, '%Y-%m-%d')

    data = '{"theaters":[{"id":"' + apollo_tag + '"}],"movieIds":[' + ','.join(movies) + '],"from":"' + front_cutoff.strftime("%Y-%m-%dT%H:%M:%S") + '","to":"' + back_cutoff.strftime("%Y-%m-%dT%H:%M:%S") + '"}'

    response = requests.post(
        'https://www.clevelandcinemas.com/api/gatsby-source-boxofficeapi/schedule',
        cookies=cookies,
        headers=headers,
        data=data,
    )

    showtimes = response.json()
    screenings = []
    showtimes = showtimes[apollo_tag]['schedule']
    for film_id in showtimes:
        for date in showtimes[film_id].values():
            for time in date:
                screenings.append({
                    'filmId': film_id,
                    'datetime': time['startsAt']
                })
    return pd.DataFrame(screenings)


# In[486]:


def screening_time(dt):
    return dt.strftime('%-I:%M%p').lower()

def showtimes_on_date(screenings, date):
    screenings = screenings[screenings['datetime'].apply(lambda x: x.strftime('%Y-%m-%d') == date)]
    return {
        film: ', '.join(screenings[screenings['title'] == film]['datetime'].apply(screening_time))
    for film in screenings['title']}


# In[487]:


def get_movie_headers():
    headers = {
        'referer': 'https://www.clevelandcinemas.com/our-locations/x03gq-apollo-theatre/'
    }

    response = requests.get('https://www.clevelandcinemas.com/page-data/sq/d/4263366313.json', headers=headers)

    data = response.json()
    data = data['data']
    movies = data['allMovie']['nodes']

    for movie in movies:
        movie['at_apollo'] = at_apollo(movie)
        if movie['at_apollo']:
            movie['apolloStart'] = apollo_start_date(movie)
            movie['trailer'] = simplify_trailer(movie['trailer'])
    movies = [movie for movie in movies if movie['at_apollo']]

    df = pd.DataFrame([{k: movie[k] for k in ['title', 'apolloStart', 'path', 'poster', 'trailer', 'at_apollo']} for movie in movies])

    df['filmId'] = df['path'].apply(lambda url: re.search(r'movies/([0-9]+)-', url).group(1))
    df = df[['title', 'apolloStart', 'trailer', 'filmId']]
    return df


# In[488]:


def showtimes_in_range(start, end):
    dates = [date.strftime('%Y-%m-%d') for date in pd.date_range(start, end)]
    headers = get_movie_headers()
    all_movies = headers['filmId'].unique()

    screenings = get_screenings(all_movies)
    screenings['datetime'] = screenings['datetime'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'))

    screenings = screenings.merge(headers[['title', 'trailer', 'filmId']], on='filmId')
    return {date: showtimes_on_date(screenings, date) for date in dates}


# In[445]:


def format_response(screenings):
    response = ''
    for day, showtimes in screenings.items():
        if len(showtimes) > 0:
            day = datetime.datetime.strptime(day, '%Y-%m-%d')
            response += f"-- {day.strftime('%a, %b. %-d')} --\n"
            for film, times in showtimes.items():
                response += f'**{film}**: {times}\n'
            response += '\n'
    return response.strip()

