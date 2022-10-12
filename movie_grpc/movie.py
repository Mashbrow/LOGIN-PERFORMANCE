import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
import json
import yaml

with open("../benchmarker/config.yaml", "r") as stream:
    try:
        TESTINGSIZE =yaml.safe_load(stream)['TESTINGSIZE']
    except yaml.YAMLError as exc:
        print(exc)
## Movie GRPC Service
class MovieServicer(movie_pb2_grpc.MovieServicer):

    def __init__(self):
        """
            Load database
        """
        with open('{}/data/movies.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["movies"]

        db2 = []

        for i in range(TESTINGSIZE):
            db2 += self.db
        self.db = db2

        print(len(self.db))
    
    def GetMovieByID(self, request, context):
        """
            Get movie by specifying an id
        """
        for movie in self.db:
            if movie['id'] == request.id:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'], rating=movie['rating'], director=movie['director'], id=movie['id'])
        return movie_pb2.MovieData(title="", rating=0.0, director="", id="")
    
    def GetListMovies(self, request, context):
        """
            Get all movies
        """
        for movie in self.db:
            yield movie_pb2.MovieData(title=movie['title'], rating=movie['rating'], director=movie['director'], id=movie['id'])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServicer_to_server(MovieServicer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
