import grequests
from flask import Flask, render_template, request, jsonify, make_response
import grpc
from concurrent import futures
import glob
import movie_pb2
import movie_pb2_grpc
import json
import time
import os
import requests
import yaml
import csv

### Loading config file

with open("./config.yaml", "r") as stream:
    try:
        cfg =yaml.safe_load(stream)
        # Number of simultaneous requests
        NB_REQ = cfg['NB_REQ']
        # True to save the results else False
        SAVE = cfg['SAVE']
        # Size of the request
        TESTINGSIZE = cfg['TESTINGSIZE']
    except yaml.YAMLError as exc:
        print(exc)

#Global variables to get time related to asynchronous requests
ASYNC_DONE_GRPC = 0
ASYNC_START_GRPC = 0
ASYNC_STOP_GRPC = 0

def save(results_list):
    """
        To be updated,
        Saving function, save in a directory named results
        Name of the result file is "resX.csv" where X is a number incrementing itself

        Arguments:
            - results_list: the list containing the results to be saved
    
    """

    existing_files = sorted(glob.glob(glob.escape("./results/") + "*.csv"), key=os.path.getmtime)
    existing_files = [os.path.basename(s) for s in existing_files]
    if existing_files != []:
        print(existing_files)
        i = str(int(existing_files[-1].split(".")[0][3:]) + 1)
    else:
        i = "0" 
    
    with open('./results/res'+i+'.csv', 'w') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerows(results_list)


def callback_grpc(call_future):
    """
        The function called when an asynchronous grpc request is completed
        ASYNC_DONE_GRPC is increased by one until it reaches the total number of
        simultaneous requests that were done. When done store the time in
        ASYNC_STOP_GRPC to get the elapsed time.
    """
    global ASYNC_DONE_GRPC, ASYNC_STOP_GRPC, NB_REQ
    ASYNC_DONE_GRPC +=1
    if ASYNC_DONE_GRPC == NB_REQ:
        ASYNC_STOP_GRPC = time.time()

def grpc_get_movie_by_id(stub,id):
    """
        Request service to get a movie specifying an id
    """
    movie = stub.GetMovieByID(id)
    print(movie)

def grpc_get_list_movies(stub):
    """
        Request service to get all movies

        Returns the elapsed time to resolve the request
    """
    start = time.time()
    empty = movie_pb2.Empty()
    allmovies = stub.GetListMovies(empty)
    stop = time.time()
    return stop-start

def grpc_async_get_movie_by_id(stub):
    """
        Create an asynchronous request to get the movie corresponding
        to the id in the function
    """
    id = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
    movies_future = stub.GetMovieByID.future(id)
    movies_future.add_done_callback(callback_grpc)

def rest_get_list_movies():
    """
        REST request to get all the movies in the database 

        Returns: the json data response and the elapsed time to resolve the
        request 
    """
    start = time.time()
    request_showtime = requests.get('http://127.0.0.1:3200'+'/json')
    stop = time.time()
    print("REST: ",stop-start)
    return request_showtime.json(), stop-start

def graphql_get_list_movies():
    """
        GRAPHQL request to get all the movies in the database

        Returns the time elapsed to resolve the request
    """
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
    return stop-start

def graphql_get_list_movies_partial():
    """
        GRAPHQL request to get partial informations of all the movies in
        the database
    """
    query = """query{
    movies {
        id
        title
    }
    }"""
    start = time.time()
    request_movie = requests.post('http://127.0.0.1:3001/graphql', json ={"query": query})
    stop=time.time()
    return stop-start

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.

    #List of results to be saved
    to_save = []
    #Store config
    to_save.append([TESTINGSIZE, NB_REQ])

    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)
        print("############## GRPC ##############")
        grpc_results = []
        print("-------------- GetListMovies --------------")
        e_time = grpc_get_list_movies(stub)
        grpc_results.append(e_time)
        print(e_time)
        print("-------------- Async Request  --------------")
        ASYNC_START_GRPC = time.time()
        for i in range(NB_REQ):
            grpc_async_get_movie_by_id(stub)
        
        #Wait until all the asynchronous requests are completed
        time.sleep(3)
        grpc_results.append(ASYNC_STOP_GRPC-ASYNC_START_GRPC)
        print(ASYNC_STOP_GRPC-ASYNC_START_GRPC)

    channel.close()

    print("############## REST ##############")
    rest_results = []

    print("-------------- GetListMovies --------------")
    movies, f_time = rest_get_list_movies()
    print(f_time)
    rest_results.append(f_time)

    print("-------------- Async Request  --------------")
    req_rest = [grequests.get('http://127.0.0.1:3200'+'/movies/a8034f44-aee4-44cf-b32c-74cf452aaaae') for i in range(NB_REQ)]
    time_map_start = time.time()
    grequests.map(req_rest)
    time_map_stop = time.time()
    print(time_map_stop-time_map_start)
    rest_results.append(time_map_stop-time_map_start)

    print("-------------- Partial Information request  --------------")
    ##Simulating post processing after the request of the full list of movies
    p_time_st = time.time()
    movies2 = []
    for movie in movies['movies']:
        dict = {"title": movie['title'],"rating": movie['rating'],"id":movie['id'], "director":movie['director']}
    movies2.append(dict)
    p_time_stp = time.time()
    ## Print complete simulated time and store it to be saved 
    print(f_time + (p_time_stp-p_time_st))
    rest_results.append(f_time + (p_time_stp-p_time_st))


    print("############## GRAPHQL ##############")
    gql_results = []
    print("-------------- GetListMovies --------------")
    e_time = graphql_get_list_movies()
    print(e_time)
    gql_results.append(e_time)

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
    gql_results.append(gql_stop - gql_start)

    print("-------------- Partial Information request  --------------")
    e_time = graphql_get_list_movies_partial()
    print(e_time)
    gql_results.append(e_time)


    if SAVE:
        to_save.append(grpc_results)
        to_save.append(rest_results)
        to_save.append(gql_results)
        save(to_save)

if __name__ == '__main__':
    run()
