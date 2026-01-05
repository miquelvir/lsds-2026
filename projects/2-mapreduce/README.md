# Building MapReduce from scratch with Python

The goal of this lab is to build a distributed data processing system that allows the user to run MapReduce jobs, which we will call SSMapReduce (Super Simple MapReduce).

This lab is inspired by [MapReduce: Simplified Data Processing on Large Clusters (2008)](https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf).

# Grade

Requirements are divided into categories to help you prioritize.

| Weight               | Description                              | Symbol   |
|----------------------|------------------------------------------|----------|
| 60% | Essential, needed to get something working       | (^)      |
| 20% | Nice-to-haves, not required to get something working | (^^)     |
| 20% | Difficult, complex exercises             | (^^^)    |

# Submit for grading

When you have finished the project, follow these steps to submit it for grading:

1. In [submission.json](./submission.json), add a list of all exercises you have completed. If you don't add them, they won't be graded. For example:

    ```json
    [
        "1.1.1",
        "1.1.2",
        "1.1.3",
        "1.2.1",
        "1.2.6"
    ]
    ```
    
2. Make sure the basic tests are passing in the `Actions` tab in GitHub

4. Submit a link to the repository in the Aula Global task

# Work breakdown

## [2.1] Worker

> [!IMPORTANT]
> You will implement the `worker` service. The `worker` service is scaled horizontally and can perform map and reduce operations.

### [2.1.1] Healthcheck (^)

Create a folder `worker` with a FastAPI service and its Dockerfile. Create a Docker Compose file as well that brings up 5 `workers` in ports 8001, 8002, 8003, 8004 and 8005.

Add volumes for the [data](./data/), [apps](./apps/) and [results](./results/) folders.

Implement a basic `/healthcheck` endpoint that always returns this:

```json
{
    "status": "up"
}
```

<details>
<summary>Sanity check</summary>

**test**

```zsh
docker compose up --build
```

```zsh
curl "http://localhost:8001/healthcheck" -s | jq
curl "http://localhost:8002/healthcheck" -s | jq
curl "http://localhost:8003/healthcheck" -s | jq
curl "http://localhost:8004/healthcheck" -s | jq
curl "http://localhost:8005/healthcheck" -s | jq
```

**expected**
```json
{
    "status": "up"
}
{
    "status": "up"
}
{
    "status": "up"
}
{
    "status": "up"
}
{
    "status": "up"
}
```
</details>


### [2.1.2] Implementing map tasks (^)

Implement the [POST /map](#post-map) endpoint. This endpoint will be called by the master to start map tasks.

> [!TIP]
> Use [background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) to trigger the map logic in the background after responding to the master.

Test it with curl.

### [2.1.3] Reading map outputs (^)

Implement the [GET /map-output](#get-map-output) endpoint. This endpoint can be called by a worker doing a reduce to get the map results this worker computed.

Test it with curl.


### [2.1.4] Implementing reduce tasks (^)

Implement the [POST /reduce](#post-reduce) endpoint. This endpoint will be called by the master to start reduce tasks.

Test it with curl.

## [2.2] Master

During this lab, you will implement the `master` service.

### [2.2.1] Healtcheck (^)
Create a folder `master` with a FastAPI service and its Dockerfile. Add it to the Docker Compose file at port 8000.

Add volumes for the [data](./data/), [apps](./apps/) and [results](./results/) folders.

Implement a basic `/healthcheck` endpoint that always returns this:

```json
{
    "status": "up"
}
```

<details>
<summary>Sanity check</summary>

**test**

```zsh
docker compose up --build
```

```zsh
curl "http://localhost:8000/healthcheck" -s | jq
```

**expected**
```json
{
    "status": "up"
}
```
</details>

### [2.2.2] Posting jobs (^)

Implement the [POST /jobs](#post-jobs) endpoint. This endpoint will be called by the client to create new MapReduce jobs.

Test it with curl.

### [2.2.3] Getting jobs (^)

Implement the [GET /jobs/{job_id}](#get-jobsjob_id) endpoint. This endpoint will be called by the client to get the status of jobs.

Test it with curl.

### [2.2.4] Notifying finished map tasks (^)

Implement the [POST /jobs/{job_id}/map/{partition}/completed](#post-jobsjob_idmappartitioncompleted) endpoint to allow workers notifying the master when they have finished a Map task.

Then, extend the workers to call this endpoint when they finish a map task.

Finally, when the last map task of a job is completed, trigger the reduce tasks in the workers.

Test it works with curl.

### [2.2.5] Notifying finished reduce tasks (^)

Implement the [POST /jobs/{job_id}/reduce/{partition}/completed](#post-jobsjob_idreducepartitioncompleted) endpoint to allow workers notifying the master when they have finished a Reduce task.

Then, extend the workers to call this endpoint when they finish a reduce task.

Finally, when the last reduce task of a job is completed, change the status of the job to `completed`.

Test you can create jobs, and the map and reduce phases work, ending with the results being stored in the [results folder](./results/) and paste screenshots of the relevant logs and results.

### [2.2.6] Client (^^)

Create a folder `client` with a Python script: `run.py` and a `requirements.txt` file with any libraries it needs to run. 

`run.py` must receive as parameters:
- name of the input data folder, 
- number of (input) map partitions, 
- number of (output) reduce partitions, 
- and name of the MapReduce app

The command should use the master API to:
- create a job and print `job_id: <id>`
- refresh the job status every **250ms** until the job completes
- if the job status changes, print it to stdout using this format: `in-progress - mapping (7/10 partitions done)`, `in-progress - reducing (9/12 partitions done)` or `completed`.


> [!TIP]
> You can use [httpx](https://www.python-httpx.org/quickstart/) to make HTTP requests with Python. See `JSON Response Content`.

### [2.2.7] Handling failures (^^^)

Call the `healtcheck` endpoint of `workers` every 30 seconds.

If a `worker` does not respond to the `healthcheck`:
- Don't send any new tasks to that worker until it starts responding to the `/healthcheck`.
- Re-assign any map or reduce tasks it had `in-progress` to other workers.

Test it works with curl.


### [2.2.8] Balancing work (^^^)

Right now, we send tasks to workers immediately. If there are many tasks, the workers could be overwhelmed. Instead, have each worker work on at most 1 task at the same time. If all workers are full, wait until they become available to send more tasks to them.

## [2.3] Using MapReduce

### [2.3.1] Modified word count (^^)

Write a MapReduce program `modified_word_count.py` that counts how many words that start with the character `t` have a length greater than 3 characters.

Test it works with the `client/run.py`, the `medium-text` dataset and your MapReduce system.

```
python3 client/run.py medium-text 4 1 modified_word_count
```

### [2.3.2] Links (^^)

Write a MapReduce program `links.py` that counts how many requests there are per user agent. E.g. 10 from Mozilla, 2 from Postman, 3 from curl, 100 from Chrome, etc.

Test it works with the `client/run.py`, the `small-logs` dataset and your MapReduce system.

```
python3 client/run.py small-logs 1 1 links
```

### [2.3.3] Bigrams (^^)

Write a MapReduce program `bigrams.py` that counts how many times each bigram appears in the text, if they appear more than once. For example, in the text `a small cat is a cute animal even if is a small cat`, the bigrams are:

```
small cat 2
is a 2
```

Test it works with the `client/run.py`, the `medium-text` dataset and your MapReduce system.

```
python3 client/run.py medium-text 4 1 bigrams
```

# Design

> [!NOTE]
> This section outlines the requirements and design decisions of the SSMapReduce architecture. You must implement a system that matches this design using Python.

SSMapReduce is composed of 2 services and 1 client:
- The [**client**](#client) allows the user to trigger MapReduce jobs and see their status.
- The [**worker** service](#worker) performs map and reduce tasks.
- The [**master** service](#master) assigns map and reduce tasks to `workers`.

The following diagram represents the dependencies in the system. For example, `client --> master` indicates that `client` depends on `master` (`client` uses the API of `master`).

```mermaid
graph TD;
    client-->master;
    master<-->workers;
    workers-->workers;

    style client stroke:#f66,stroke-width:2px,stroke-dasharray: 5 5
```

### client

The client has a single command to create a job and track the job status until completion.

### worker

In SSMapReduce, there's many workers (the worker is horizontally scaled).

In order for the `master` to be able to assign tasks, the `worker` exposes three API endpoints:
- [Healthcheck](#get-healthcheck)
- [Run a map](#post-map)
- [Run a reduce](#post-reduce)

In order for the other `workers` to be able to read the output of a map task this `worker` completed, the `worker` exposes one additional API endpoint:
- [Get the map output](#get-map-output)

#### worker filesystem

The `worker` stores all its data in two folders: `outputs` and `results`.

The `outputs` folder is a folder in the local file system which only this worker can access and it stores the outputs of map tasks. The paths are: `/outputs/{job_id}/{map_partition}/{reduce_partition}`. For example:

```
/outputs
    /617d9970-9b4c-4025-beb8-16ff03afc8d2
        /1
            0
            1
            2
            6
            7
            8
            9
        /2
            1
            2
            3
            7
            8
            9
```

The `results` folder is part of a global file system (volume) shared amongst all workers to store the result of reduce tasks. The paths are: `/results/{job_id}/{reduce_partition}`. For example:

```
/results
    /617d9970-9b4c-4025-beb8-16ff03afc8d2
        0
        1
        2
        3
        4
        5
        6
        7
        8
        9
```

#### GET /healthcheck

The healthcheck endpoint always returns a healthy response.

For example:

```
GET /healthcheck
```

Response:
```json
{
    "status": "up"
}
```

#### POST /map

The map endpoint receives a body with the details of the map task and starts processing it in the background immediately after sending the response.

The body fields are:
- `job_id`: an id for the job
- `app_name`: the name of a MapReduce app from the [apps](./apps/) folder, without the `.py` extension.
- `data_path`: the path to a folder which contains one file for every split/partition of the input data
- `map_partition`: the number of the partition that must be read from the `data_path` folder for mapping
- `reduce_partitions`: the number of output partitions after mapping

For example:

```
POST /map
```

Body:
```json
{
    "job_id": "617d9970-9b4c-4025-beb8-16ff03afc8d2",
    "app_name": "word_count",
    "data_path": "./data/articles",
    "map_partition": 1,
    "reduce_partitions": 10
}
```

Response:
```json
{
    "status": "in-progress"
}
```

To run the map, you must:
- Dynamically import the `map` function from the client Python app
- Call the `map` function from the client with: key (name of the partition file) and value (content of the partition file)
- Store the list of `(key, value)` returned by the user's map function in the correct file of the `outputs` directory.

##### Dynamically importing the map, reduce and partitioner functions

To dynamically import the map, reduce and partitioner functions written by the user in an app located in the [apps directory](./apps/), use this code:

```python
from importlib import import_module
import sys
sys.path.append("./apps")

def load_app(app_name):
    module = import_module(app_name)
    return (
        getattr(module, "map"),
        getattr(module, "reduce"),
        getattr(module, "partitioner"),
    )

map_function, reduce_function, partition_function = load_app("word_count")
```

##### Deciding the reduce partition

For each key and value returned by the map, it must be appended to a file in `/outputs/{job_id}/{map_partition}/{reduce_partition}`.

To obtain the `reduce_partition`, call the client-defined `partition_function` and use the modulo operator with the `reduce_partitions` integer you received in the body. This will guarantee that:
- All values for the same key are in the same `reduce_partition`
- All keys end up in the same `reduce_partition` regardless of which worker is running it
- All keys are distributed in `reduce_partitions` partitions / files for the reducers to read.

##### The map output files

The result of the map is stored in many files, one per each output partition that has keys in this map task:

```
/outputs
    /617d9970-9b4c-4025-beb8-16ff03afc8d2
        /1
            0
            1
            2
            6
            7
            8
            9
```

Each of these files has the reduce partition number as its name.

The content of this file is one key and one value per line, separated with a space. For example:

```
granted 1
graphite 1
global 1
```

#### GET /map-output

The `map-output` endpoint allows other workers that need this worker's map output as input for their reduce to read it.

It receives as query parameters:
- `job_id`: the id of the job
- `map_partition`: the number of the map partition to read
- `reduce_partition`: inside that mapped partition, which of the output's reduce partition to read

The response consists of a dictionary of each key, and a list of the values produced by the map tasks.

For example:

```
GET /map-output?job_id=617d9970-9b4c-4025-beb8-16ff03afc8d2&map_partition=2&reduce_partition=1"
```

Response:
```json
{
    "offers": ["1", "1"],
    "easier": ["1", "1"],
    "effort": ["1", "1", "1"],
    "embrace": ["1"],
    "of": ["1", "1", "1", "1", "1", "1"]
}
```

#### POST /reduce

The reduce endpoint receives a body with the details of the reduce task and starts processing it in the background immediately after sending the response.

The body fields are:
- `job_id`: the id of the job
- `app_name`: the name of a MapReduce app from the [apps](./apps/) folder, without the `.py` extension.
- `reduce_partition`: an integer representing which partition of the map task's output must be processed by this worker
- `intermediate_partitions`: a list of URLs of workers which have the results of map tasks for this job

For example:

```
POST /reduce
```

Body:
```json
{
    "job_id": "617d9970-9b4c-4025-beb8-16ff03afc8d2",
    "app_name": "word_count",
    "reduce_partition": 1,
    "intermediate_partitions": ["http://worker1:80/map-output?job_id=617d9970-9b4c-4025-beb8-16ff03afc8d2&map_partition=0&reduce_partition=1", "http://worker2:80/map-output?jobId=617d9970-9b4c-4025-beb8-16ff03afc8d2&map_partition=1&reduce_partition=1", "http://worker2:80/map-output?jobId=617d9970-9b4c-4025-beb8-16ff03afc8d2&map_partition=2&reduce_partition=1"]
}
```

Response:
```json
{
    "status": "in-progress"
}
```

To run the reduce, you must:
- For every `map_worker` of this job (the ones in the body), fetch their outputs using the [GET /map-output](#get-map-output) endpoint.
- Aggregate all values for each key across all the map outputs'.
- Dynamically import the `reduce` function from the client Python app [similar to the map](#dynamically-importing-the-map-reduce-and-partitioner-functions)
- Call the `reduce` function from the client with: key (produced by the previous maps) and values list (list of all string values for that key)
- Store the value returned by the user's reduce function in the correct file of the `results` directory.


##### The reduce results files

The result of the map is stored in many files, one per reduce task:

```
/results
    /617d9970-9b4c-4025-beb8-16ff03afc8d2
        0
        1
        2
        6
        7
        8
        9
```

Each of these files has the reduce partition number as its name. Each reduce worker writes a single reduce output file for any given reduce task.

The content of this file is one key and one value per line, separated with a space. The value (if not empty) is the one returned by the user's reduce function. For example:

```
developers 1
not 2
deep 1
derived 1
network 1
doubt 1
neural 1
new 2
discomfort 1
```


### master

In SSMapReduce, there's one master (the master is vertically scaled).

The `master` exposes two endpoints for the client to create jobs and check its status:
- [Create a job](#post-jobs)
- [Read a job by id](#get-jobsjob_id)

In order for the `workers` to notify the master when they finish a task, the master exposes two additional endpoints:
- [Map completed](#post-jobsjob_idmappartitioncompleted)
- [Reduce completed](#post-jobsjob_idreducepartitioncompleted)

The master stores all of its state in memory. Namely, it has a `jobs` dictionary in a variable where it stores and update the state of all jobs.

The master should read a `config.json` file with the URLs of all the workers in the system:

```json
{
    "workers": ["http://worker1:80", "http://worker2:80", "http://worker3:80", "http://worker4:80", "http://worker5:80"]
}
```

#### POST /jobs

This endpoint allows the caller to trigger a new MapReduce job. It takes the following body parameters:
- `app_name`: the name of a MapReduce app from the [apps](./apps/) folder, without the `.py` extension.
- `data_path`:  the path to a folder which contains one file for every split/partition of the input data
- `map_partitions`: an integer representing how many files/partitions are in the folder in the `data_path`
- `reduce_partitions`: an integer representing how many files/partitions the output should be divided in after reducing

When a new job is received:
- The master generates a new id using [uuid4](https://www.uuidgenerator.net/dev-corner/python).
- Selects a worker using modulo and [sends the worker a map task using the API](#post-map)
- Stores the job, as well as all the workers that have been assigned to its in-memory dictionary

For example:

```
POST /jobs
```

Body:
```json
{
    "app_name": "word_count",
    "data_path": "./data/articles",
    "map_partitions": 3,
    "reduce_partitions": 10
}
```

Response:
```json
{
    "job_id":"617d9970-9b4c-4025-beb8-16ff03afc8d2",
    "app_name":"word_count",
    "data_path":"./data/articles",
    "map_partitions":3,
    "reduce_partitions":10,
    "mappers":[
        {"worker":"worker3:80","status":"in-progress","partition":0},
        {"worker":"worker1:80","status":"in-progress","partition":1},
        {"worker":"worker2:80","status":"in-progress","partition":2}
    ],
    "reducers":[
        {"worker":null,"status":"idle","partition":0},
        {"worker":null,"status":"idle","partition":1},
        {"worker":null,"status":"idle","partition":2},
        {"worker":null,"status":"idle","partition":3},
        {"worker":null,"status":"idle","partition":4},
        {"worker":null,"status":"idle","partition":5},
        {"worker":null,"status":"idle","partition":6},
        {"worker":null,"status":"idle","partition":7},
        {"worker":null,"status":"idle","partition":8},
        {"worker":null,"status":"idle","partition":9}
    ],
    "status":"in-progress"
}
```

#### GET /jobs/{job_id}

This endpoint reads the job status from the in-memory dictionary and returns it.

```
GET /jobs/617d9970-9b4c-4025-beb8-16ff03afc8d2
```

Response:
```json
{
    "job_id":"617d9970-9b4c-4025-beb8-16ff03afc8d2",
    "app_name":"word_count",
    "data_path":"./data/articles",
    "map_partitions":3,
    "reduce_partitions":10,
    "mappers":[
        {"worker":"worker3:80","status":"in-progress","partition":0},
        {"worker":"worker1:80","status":"in-progress","partition":1},
        {"worker":"worker2:80","status":"in-progress","partition":2}
    ],
    "reducers":[
        {"worker":null,"status":"idle","partition":0},
        {"worker":null,"status":"idle","partition":1},
        {"worker":null,"status":"idle","partition":2},
        {"worker":null,"status":"idle","partition":3},
        {"worker":null,"status":"idle","partition":4},
        {"worker":null,"status":"idle","partition":5},
        {"worker":null,"status":"idle","partition":6},
        {"worker":null,"status":"idle","partition":7},
        {"worker":null,"status":"idle","partition":8},
        {"worker":null,"status":"idle","partition":9}
    ],
    "status":"in-progress"
}
```

It must return a 404 if the job is not found.

#### POST /jobs/{job_id}/map/{partition}/completed

This endpoint allows a `worker` to let the `master` know that it has finished the map task for partition `{partition}`.

When the `master` receives a map task completion notification, it must update the task status in the in-memory dictionary. Then, if there are no mapping tasks pending completion, it must start sending the reduce tasks to the workers.

For example:

```
POST /jobs/617d9970-9b4c-4025-beb8-16ff03afc8d2/map/2/completed
```


Response:
```json
{
    "message": "Status updated"
}
```

If the task is already completed by another worker, return a 409.


#### POST /jobs/{job_id}/reduce/{partition}/completed

This endpoint allows a `worker` to let the `master` know that it has finished the reduce task for partition `{partition}`.

When the `master` receives a reduce task completion notification, it must update the task status in the in-memory dictionary. Then, if there are no reduce tasks pending completion, it must mark the overall job status as `completed`.


For example:

```
POST /jobs/617d9970-9b4c-4025-beb8-16ff03afc8d2/reduce/2/completed
```

Response:
```json
{
    "message": "Status updated"
}
```

If the task is already completed by another worker, return a 409.
