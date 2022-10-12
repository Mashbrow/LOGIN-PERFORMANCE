import grequests
from flask import Flask, render_template, request, jsonify, make_response
import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
import json
import time
import requests

NB_REQ = 100
ASYNC_DONE_GRPC = 0
ASYNC_START_GRPC = 0
ASYNC_STOP_GRPC = 0

### Client for the movie API

def callback_grpc(call_future):
    global ASYNC_DONE_GRPC, ASYNC_STOP_GRPC, NB_REQ
    ASYNC_DONE_GRPC +=1
    if ASYNC_DONE_GRPC == NB_REQ:
        ASYNC_STOP_GRPC = time.time()

def callback_rest(call_future):
    global ASYNC_DONE_REST, ASYNC_STOP_REST, NB_REQ
    ASYNC_DONE_REST +=1
    if ASYNC_DONE_REST == NB_REQ:
        ASYNC_STOP_REST = time.time()

def grpc_get_movie_by_id(stub,id):
    """
        Request service to get a movie specifying an id
    """
    movie = stub.GetMovieByID(id)
    print(movie)

def grpc_get_list_movies(stub):
    """
        Request service to get all movies
    """
    start = time.time()
    empty = movie_pb2.Empty()
    allmovies = stub.GetListMovies(empty)
    stop = time.time()
    print("GRPC: ",stop-start)

def grpc_async_get_movie_by_id(stub):
    id = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
    movies_future = stub.GetMovieByID.future(id)
    movies_future.add_done_callback(callback_grpc)

def rest_get_list_movies():
    start = time.time()
    request_showtime = requests.get('http://127.0.0.1:3200'+'/json')
    stop = time.time()
    print("REST: ",stop-start)
    return request_showtime.json(), stop-start

def graphql_get_list_movies():
    query = """query{
    movies {
        id
        rating
        title
        director
    }
    }"""
    #Perform the request

    start = time.time()
    request_movie = requests.post('http://127.0.0.1:3001/graphql', json ={"query": query})
    stop=time.time()
    print("GRAPHQL: ", stop-start)

def graphql_get_list_movies_partial():
    query = """query{
    movies {
        id
        title
    }
    }"""
    start = time.time()
    request_movie = requests.post('http://127.0.0.1:3001/graphql', json ={"query": query})
    stop=time.time()
    print("GRAPHQL: ", stop-start)

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)

        ##print("-------------- GetMovieByID --------------")
        ##movieid = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
        ##get_movie_by_id(stub, movieid)
        print("############## GRPC ##############")
        print("-------------- GetListMovies --------------")
        grpc_get_list_movies(stub)
        print("-------------- Async Request  --------------")
        ASYNC_START_GRPC = time.time()
        for i in range(NB_REQ):
            grpc_async_get_movie_by_id(stub)
        
        time.sleep(3)
        print(ASYNC_STOP_GRPC-ASYNC_START_GRPC)

    channel.close()
    print("############## REST ##############")
    print("-------------- GetListMovies --------------")
    movies, f_time = rest_get_list_movies()
    print("-------------- Async Request  --------------")
    req_rest = [grequests.get('http://127.0.0.1:3200'+'/movies/a8034f44-aee4-44cf-b32c-74cf452aaaae') for i in range(NB_REQ)]
    time_map_start = time.time()
    grequests.map(req_rest)
    time_map_stop = time.time()
    print(time_map_stop-time_map_start)

    print("-------------- Partial Information request  --------------")
    p_time_st = time.time()
    movies2 = []
    for movie in movies['movies']:
        dict = {"title": movie['title'],"rating": movie['rating'],"id":movie['id'], "director":movie['director']}
    movies2.append(dict)
    p_time_stp = time.time()
    print(f_time + (p_time_stp-p_time_st))
    print("############## GRAPHQL ##############")
    print("-------------- GetListMovies --------------")
    graphql_get_list_movies()
    print("-------------- Async Request  --------------")
    query = """query{
    movie_with_id(_id: "a8034f44-aee4-44cf-b32c-74cf452aaaae" ) {
        id
        rating
        title
        director
    }
    }"""

    req_gql = [grequests.post('http://127.0.0.1:3001/graphql', json ={"query": query}) for i in range(NB_REQ)]
    gql_start = time.time()
    grequests.map(req_gql)
    gql_stop = time.time()
    print(gql_stop - gql_start)

    print("-------------- Partial Information request  --------------")
    graphql_get_list_movies_partial()

if __name__ == '__main__':
    run()
