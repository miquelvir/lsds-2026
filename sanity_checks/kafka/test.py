import urllib.request
import logging
import subprocess
import time
import sys
import os
import uuid

SOLUTION_PATH = "./projects/4-kafka"
docker_compose_path = f"{SOLUTION_PATH}/docker-compose.yml"
client_path = f"{SOLUTION_PATH}/client"
client_requirements_path = f"{client_path}/requirements.txt"
client_create_topic_path = f"{client_path}/create_topic.py"
client_consume_path = f"{client_path}/consume.py"
client_produce_path = f"{client_path}/produce.py"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def _wait_until_healthcheck(url):
    timeout_seconds = 60
    interval_seconds = 2
    elapsed_seconds = 0
    while elapsed_seconds < timeout_seconds:
        try:
            response = urllib.request.urlopen(f"{url}/healthcheck")
            if response.status == 200:
                logging.info(f"Healthcheck at {url!r} succeeded")
                break
        except:
            pass

        time.sleep(interval_seconds)
        elapsed_seconds += interval_seconds
    else:
        raise TimeoutError(f"Timeout waiting for docker compose containers to be running and responding to healthcheck at {url!r}")


logging.info(f"Using docker compose file at: {docker_compose_path}")

try:
    subprocess.run(
        ["docker", "compose", "-f", docker_compose_path, "up", "--build", "-d"],
        check=True,
    )
except subprocess.CalledProcessError:
    logging.exception("Unable to bring up docker compose")
    raise

try:
    # wait for brokers on ports 8001..8005
    _wait_until_healthcheck("http://localhost:8001")
    _wait_until_healthcheck("http://localhost:8002")
    _wait_until_healthcheck("http://localhost:8003")
    _wait_until_healthcheck("http://localhost:8004")
    _wait_until_healthcheck("http://localhost:8005")

    logging.info("Docker compose containers are up and responding to healthcheck")

    try:
        subprocess.run(
            ["pip", "install", "-r", client_requirements_path, "-q", "--progress-bar", "off"],
            check=True,
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to install client requirements")
        raise

    time.sleep(10)  # wait a moment for brokers to elect a leader

    # use client scripts to create topic, produce and consume
    topic = str(uuid.uuid4()).replace("-", "")
    try:
        subprocess.run([
            "python3",
            client_create_topic_path,
            topic,
            "-p",
            "1",
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        logging.error("create_topic.py failed:\n%s", e.stdout)
        raise AssertionError("Failed to create topic via client")

    time.sleep(5)  # wait a moment for changes to propagate

    # produce three records with the same key
    key = "samekey"
    payloads = ["payload1", "payload2", "payload3"]
    produce_input_lines = []
    for payload in payloads:
        produce_input_lines.append(key)
        produce_input_lines.append(payload)
    produce_input_lines.append("")
    produce_input = "\n".join(produce_input_lines) + "\n"

    try:
        proc = subprocess.run([
            "python3",
            client_produce_path,
            topic,
        ], input=produce_input, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=20)
        logging.info("produce.py output:\n%s", proc.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("produce.py failed:\n%s", e.stdout)
        raise AssertionError("Failed to produce records via client")
    except subprocess.TimeoutExpired as e:
        logging.error("produce.py timed out; output:\n%s", e.stdout or "")
        raise AssertionError("produce.py timed out")

    # consume the target partition and assert all produced payloads are present
    tp = f"{topic}-1"
    proc = subprocess.Popen([
        "python3",
        "-u",
        client_consume_path,
        tp,
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()

    logging.info("consume.py output for %s:\n%s", tp, out)
    
    for expected_payload in payloads:
        if expected_payload not in out:
            logging.error("Expected payload %r not found in consume output for %s:\n%s", expected_payload, tp, out)
            raise AssertionError(f"Expected payload {expected_payload} not found in {tp}")
    logging.info("Partition %s contains expected payloads", tp)

finally:
    try:
        pass
        subprocess.run(
            ["docker", "compose", "-f", docker_compose_path, "down"],
            check=True,
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to bring down docker compose")
        raise
