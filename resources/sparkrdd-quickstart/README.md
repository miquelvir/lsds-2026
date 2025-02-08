# Spark sample

Start a Spark cluster locally using Docker compose:

```zsh
docker-compose up
```

This cluster has 2 workers and a master. You can use the following command to open a terminal in the master server: `docker-compose exec spark-master`

Check the local IP for the Spark Master service in the `spark-master-1` container logs. You should see a log similar to `Starting Spark master at spark://172.20.0.2:7077`.

To run a job with Spark, run the `spark-submit` command in the master:

```zsh
docker-compose exec spark-master spark-submit --master spark://{IP_FROM_PREVIOUS_STEP}:7077 /opt/bitnami/spark/app/spark_sum.py /opt/bitnami/spark/app/data/numbers1.txt
```
