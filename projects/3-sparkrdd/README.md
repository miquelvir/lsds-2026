# Using Spark RDD with Python

The goal of this lab is to use Spark RDD to analyze data.

# Grade

Requirements are divided into categories to help you prioritize.

| Weight               | Description                              | Symbol   |
|----------------------|------------------------------------------|----------|
| 40% | Essential, needed to get something working       | (^)      |
| 40% | Nice-to-haves, not required to get something working | (^^)     |
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

## [3.1] SparkRDD

### [2.1.1] Summing numbers (^)

Start up a Spark cluster locally using Docker compose: `docker-compose up`.

Check the local IP for the Spark Master service in the spark-master-1 container logs. You should see a log similar to `Starting Spark master at spark://172.20.0.2:7077`.

Run the job with Spark: `docker-compose exec spark-master spark-submit --master spark://{IP_FROM_PREVIOUS_STEP}:7077 /opt/bitnami/spark/app/spark_sum.py /opt/bitnami/spark/app/data/numbers1.txt`

Take a close look at the logs. What was the result of your job?

### [2.1.2] Summing even numbers (^)

The file `numbers2.txt` has many lines, each with many numbers.

Create a file `spark_sum_even.py` which computes the sum of all the even numbers.


### [2.1.3] Counting people in cities (^^)

The file `people.txt` has many lines, each with `{NAME} {LANGUAGE} {CITY}`.

Create a file `spark_count_people.py` that counts how many people live in each city.

### [2.1.4] Counting bigrams (^^)

The file `cat.txt` has many lines, each with a sentence.

Create a file `spark_count_bigrams.py` that counts how many times each bigram appears.

### [2.1.5] Reverse index (^^^)

Find the latest available Wikipedia datasets from [dumps.wikimedia](https://dumps.wikimedia.org/other/enterprise_html/runs/). For example, https://dumps.wikimedia.org/other/enterprise_html/runs/20240901/enwiki-NS0-20240901-ENTERPRISE-HTML.json.tar.gz.

Then, download the first 10 and 1k articles in different files. The smaller datasets will be useful for testing.

```
curl -L https://dumps.wikimedia.org/other/enterprise_html/runs/20240901/enwiki-NS0-20240901-ENTERPRISE-HTML.json.tar.gz | tar xz --to-stdout | head -n 10 > wikipedia10.json

curl -L https://dumps.wikimedia.org/other/enterprise_html/runs/20240901/enwiki-NS0-20240901-ENTERPRISE-HTML.json.tar.gz | tar xz --to-stdout | head -n 1000 > wikipedia1000.json
```

Write a Spark RDD job that creates a reverse index for all the crawled articles. he reverse index must map every word in the abstract of every article, to the list of article (ids) that contain it. Store this as a file. The format must be: `LINE CRLF LINE CRLF LINE CRLF ...`, where each LINE is `WORD SP DOCID SP DOCID SP DOCID SP ... DOCID`. For example:

```
seven 18847712 76669474 76713187 75388615 1882504 18733291 19220717 3118126 31421710 26323888 52867888 76712306 76711442 48957757
seasons 58765506 76669474 7755966 66730851 53056676 40360169 7871468 60331788 52867888 70406270 52243132 17781886
22 12000256 14177667 56360708 50648266 31581711 76395922 31418962 73082202 33375130 76669474 76713187 5799657 40360169 65704112 18688178 48850419 37078259 63141238 40538167 32644089
due 76731844 41098246 25214406 41098253 1658830 31581711 8905616 45711377 14259409 76708884 2723548 76732829 1122974 41233503 43331165 76669474 12365159 18733291 7871468 65704112 63447415 63840761 68538426 36367677
sold 76669474 31728882 53538197 63141238 12243595
```
