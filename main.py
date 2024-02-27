import logging
import os
import subprocess
from time import sleep

if __name__ == "__main__":

    # os.environ["PRODUCTION"] = "1"
    sleep(20)
    while True:
        try:
            subprocess.run(["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app_run:app"])
        except Exception as error:
            logging.error(error)
            sleep(5)
