# LOGIN-PERFORMANCE
Rapository for benchmarking REST, GRPC and GRAPHQL

### Installation
First clone the repo: `git clone https://github.com/Mashbrow/LOGIN-PERFORMANCE`

To launch with docker-compose, get to the LOGIN-PERFORMANCE folder and type `docker-compose up` in your terminal.

### Use it

To use our work, once the docker command is done you can run benchmarker.py to get the results of an experimentation given the config specified in the `config.yaml` file. Results can be vizualized using the notebook that can be found in the benchmarker repository. We used Plotly to vizualize curves of the results.

Only the green version of the practical work was done.

We decided to study the performances of the three API based on the movie service previously created on the three previous practical work.

We decided to measure the performances on three different points:
- The time evolution to resolve a request in function of its size.
- The time evolution to resolve a partial request in function of its size.
- The time evolution of processing an increasing number of requests received in the same time, it could be compared to a measure of congestion.

The results obtained are functions of the hardware at our dispostion, i.e. our personal computer. Moreover, the results differs from one run to another, we thus decided to make several runs to obtain statistics instead of a single value. As time was lacking we decide to proceed as in the following:
- For each different request size, re-run the experiment 10 times. We do know that this number is relatively low and that it would require more runs for the statistics to be realy reliable.
- For every number of simultaneous different requests, re-run the experiment 10 times.
- Compute the mean, the max and the min (those are more relevant than the standard deviation when the number of experiments is low)
- Display results on a graph, showing the mean curve and its envelope corresponding to mean values + the max and mean values - the min
