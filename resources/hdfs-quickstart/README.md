# hadoop-quickstart

This project has the basics to get started running a Hadoop cluster locally.
It creates a cluster with 2 data nodes.

> [!TIP]
> Normally, you would run Hadoop in a cluster of servers. 
> However, for testing purposes, we can simulate it with Docker.
> We will spin up one container for each node.

## Setup
1. Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)


## Running locally
1. Create a Hadoop system
```bash
docker-compose up -d
```

> [!WARNING]
> Verify you see 6 containers under `hadoop-quickstart` in Docker desktop.

## Using the Hadoop client

1. Open a shell in the test client
```bash
docker exec -it hadoop-quickstart-testclient-1 /bin/sh
```

> [!TIP]
> The `apache/hadoop` container image conveniently has the `hdfs` CLI client.
> We can use it to send and download files from the HDFS cluster.
> The `testclient` container does nothing in the cluster (it is not any node).
> `testclient` it is just there for use to open a shell and run CLI commands.

2. Download an image to use for testing
```bash
curl https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/1024px-Cat_August_2010-4.jpg > cat1.png
```

3. Create a directory in HDFS
```bash
hdfs dfs -mkdir -p cats
```

4. Upload the cat image
```bash
hdfs dfs -put cat1.png cats/cat1.png
```

5. Verify the image has been uploaded
```bash
hdfs dfs -ls
hdfs dfs -ls cats
```

6. Download an image
```bash
hdfs dfs -get cats/cat1.png cat1-downloaded-from-hdfs.png
```

7. Verify the images are correct
```bash
diff -sq cat1.png cat1-downloaded-from-hdfs.png
```




## FAQ

### Where are blocks stored?

Blocks are stored in the data node in `/hadoop-data`.

### How to change block size?

Edit `HDFS-SITE.XML_dfs.block.size` in the [config](./config) file.

### How to change replication factor?

Edit `HDFS-SITE.XML_dfs.replication` in the [config](./config) file.

### How to get a report?

```bash
hdfs fsck /
```

### How to see the Hadoop dashboard?

Open [http://localhost:9870/explorer.html#/](http://localhost:9870/explorer.html#/) in a browser.

### Where are snapshots and the journal?

In the name node:
- `/tmp/hadoop-hadoop/dfs/name/current/edits_inprogress_****************` is the journal
- `/tmp/hadoop-hadoop/dfs/name/current/fsimage_****************` is the snapshot

### How to view the Journal (WAL) in a human-readable format?

```bash
hdfs oev -p xml -i /tmp/hadoop-hadoop/dfs/name/current/edits_inprogress_0000000000000000001 -o edits.xml && cat edits.xml
```

### How can I put a file with some test values?

```bash
echo "1 2 3 4 5 6 7 8 9" >> data.txt && hdfs dfs -put data.txt /data.txt
```