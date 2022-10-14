import json
import yaml

with open("config.yaml", "r") as stream:
    try:
        TESTINGSIZE =yaml.safe_load(stream)['TESTINGSIZE']
    except yaml.YAMLError as exc:
        print(exc)
#Resolver for movie service
def movies(_,info):
    """
        Get all movies in database
    """
    db = []
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)['movies']

    for i in range(TESTINGSIZE):
        db += movies

    movies = db
    return db
    
def movie_with_id(_,info,_id):
    """
        Get movie by specifying its id
        Argument:
            _id : id of the movie (in the query)
    """
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie

def update_movie_rate(_,info,_id,_rate):
    """
        Update rating of a movie
        Arguments:
            _id: id of the movie (in the query)
            _rate: new rating of the movie (in the query)
    """
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def resolve_actors_in_movie(movie, info):
    """
        Get actors of a movie
        Argument: 
            movie: movie (in the query)
    """
    with open('{}/data/actors.json'.format("."), "r") as file:
        data = json.load(file)
        actors = [actor for actor in data['actors'] if movie['id'] in actor['films']]
        return actors