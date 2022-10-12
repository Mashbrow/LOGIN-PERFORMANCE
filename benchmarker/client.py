import grpc

import movie_pb2
import movie_pb2_grpc

### Client for the movie API
def get_movie_by_id(stub,id):
    """
        Request service to get a movie specifying an id
    """
    movie = stub.GetMovieByID(id)
    print(movie)

def get_list_movies(stub):
    """
        Request service to get all movies
    """
    allmovies = stub.GetListMovies(movie_pb2.Empty())
    for movie in allmovies:
        print("Movie called %s" % (movie.title))

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)

        print("-------------- GetMovieByID --------------")
        movieid = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
        get_movie_by_id(stub, movieid)
        
        print("-------------- GetListMovies --------------")
        get_list_movies(stub)

    channel.close()

if __name__ == '__main__':
    run()
