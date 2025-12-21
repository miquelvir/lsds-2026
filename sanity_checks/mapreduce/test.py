import urllib.request
import logging
import subprocess
import time
import sys
import hashlib
import os
from collections import Counter
import re

SOLUTION_PATH = "./projects/2-mapreduce"
docker_compose_path = f"{SOLUTION_PATH}/docker-compose.yml"
client_path = f"{SOLUTION_PATH}/client"
client_requirements_path = f"{client_path}/requirements.txt"
client_run_path = f"{client_path}/run.py"
test_file = f"{SOLUTION_PATH}/data/medium-text"

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
            else:
                logging.warning(f"Healthcheck at {url!r} returned {response.status} instead of 200")
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
        check=True
    )
except subprocess.CalledProcessError as e:
    logging.exception("Unable to bring up docker compose")
    raise

try:
    _wait_until_healthcheck("http://localhost:8000")
    _wait_until_healthcheck("http://localhost:8001")
    _wait_until_healthcheck("http://localhost:8002")
    _wait_until_healthcheck("http://localhost:8003")
    _wait_until_healthcheck("http://localhost:8004")
    _wait_until_healthcheck("http://localhost:8005")

    logging.info("Docker compose containers are up and responding to healthcheck")


    try:
        subprocess.run(
            ["pip", "install", "-r", client_requirements_path, "-q", "--progress-bar", "off"],
            check=True
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to install client requirements")
        raise

    try:
        result = subprocess.run(
            ["python3", client_run_path, "small-text", "1", "3", "word_count"],
            check=True,
            timeout=100,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        logging.info("Client output:\n%s", result.stdout)

        m = re.search(r"job_id:\s*([0-9a-fA-F\-]{36})", result.stdout)
        if not m:
            raise AssertionError("Could not find job_id in client output")
        job_id = m.group(1)
    except subprocess.CalledProcessError:
        logging.exception("Unable to run job using client")
        raise

    results_dir = os.path.join(SOLUTION_PATH, "results", job_id)
    if not os.path.isdir(results_dir):
        raise AssertionError(f"Results folder not found: {results_dir}")
    if not os.path.exists(os.path.join(results_dir, "0")):
        print(f"Result partition 0 not found: {results_dir}")
        raise AssertionError(f"Result partition 0 not found: {results_dir}")
    if not os.path.exists(os.path.join(results_dir, "1")):
        print(f"Result partition 1 not found: {results_dir}")
        raise AssertionError(f"Result partition 1 not found: {results_dir}")
    if not os.path.exists(os.path.join(results_dir, "2")):
        print(f"Result partition 2 not found: {results_dir}")
        raise AssertionError(f"Result partition 2 not found: {results_dir}")
    logging.info(f"Found results folder: %s", results_dir)

    # Compare each partition file with its corresponding snapshot file
    for part in ("0", "1", "2"):
        part_path = os.path.join(results_dir, part)
        with open(part_path, "r") as fh:
            actual_lines = [ln.strip() for ln in fh if ln.strip()]

        snapshot_path = os.path.join(os.path.dirname(__file__), "snapshot", part)
        if not os.path.isfile(snapshot_path):
            raise AssertionError(f"Snapshot file not found for partition {part}: {snapshot_path}")
        with open(snapshot_path, "r") as fh:
            expected_lines = [ln.strip() for ln in fh if ln.strip()]

        actual_cnt = Counter(actual_lines)
        expected_cnt = Counter(expected_lines)
        if actual_cnt != expected_cnt:
            missing = expected_cnt - actual_cnt
            extra = actual_cnt - expected_cnt
            logging.error("Partition %s mismatch. Missing: %s Extra: %s", part, dict(missing), dict(extra))
            raise AssertionError(f"Result partition {part} does not match snapshot")
        logging.info("Partition %s matches snapshot", part)
finally:
    try:
        subprocess.run(
            ["docker", "compose", "-f", docker_compose_path, "down"],
            check=True
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to bring down docker compose")
        raise