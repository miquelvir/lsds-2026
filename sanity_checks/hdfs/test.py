import urllib.request
import logging
import subprocess
import time
import sys
import hashlib
import os

SOLUTION_PATH = "./projects/1-hdfs"
docker_compose_path = f"{SOLUTION_PATH}/docker-compose.yml"
client_path = f"{SOLUTION_PATH}/client"
client_requirements_path = f"{client_path}/requirements.txt"
client_upload_path = f"{client_path}/upload.py"
client_download_path = f"{client_path}/download.py"
test_file = f"{SOLUTION_PATH}/test_files/cat.jpg"

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


def _file_hash(path, algo="sha256", chunk_size=8192):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

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
        subprocess.run(
            ["python3", client_upload_path, test_file, "uploaded-cat.jpg"],
            check=True
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to upload file using client")
        raise

    if os.path.exists("downloaded-cat.jpg"):
        try:
            os.remove("downloaded-cat.jpg")
            logging.info("Removed existing downloaded-cat.jpg")
        except Exception:
            logging.exception("Unable to remove existing downloaded-cat.jpg")
            raise

    try:
        subprocess.run(
            ["python3", client_download_path, "uploaded-cat.jpg", "downloaded-cat.jpg"],
            check=True
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to download file using client")
        raise

    if _file_hash(test_file) != _file_hash("downloaded-cat.jpg"):
        logging.error("Downloaded file does not match uploaded file")
        raise RuntimeError("Downloaded file does not match uploaded file")
    else:
        logging.info("Downloaded file matches uploaded file")
finally:
    try:
        subprocess.run(
            ["docker", "compose", "-f", docker_compose_path, "down"],
            check=True
        )
    except subprocess.CalledProcessError:
        logging.exception("Unable to bring down docker compose")
        raise