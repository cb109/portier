#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import logging
import argparse
import threading

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s | %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger("portier")


MAX_THREADS = 200


class ThreadedCounter(object):
    """A counter to be used in multiple threads."""
    def __init__(self, startAt=0, maxCount=100, verbose=False):
        self.current = startAt
        self.max = maxCount
        self.verbose = verbose
        self.lock = threading.Lock()

    def clock(self):
        with self.lock:
            self.current += 1
            percent = self.current / (self.max / 100.0)
            if self.verbose:
                log.info("{v}/{m} - {p:.2f}%".format(
                    v=self.current, m=self.max, p=percent))


def chunkify(array, n):
    """Divides array into n chunks."""
    start = 0
    for i in range(n):
        stop = start + len(array[i::n])
        yield array[start:stop]
        start = stop


def getPortRange(portString):
    """Converts the string to a list of individual ports."""
    tokens = portString.split("-")
    try:
        start, end = tokens
    except ValueError:
        start = end = tokens[0]
    portRange = list(range(int(start), int(end) + 1))
    return portRange


def checkPort(address, port):
    """Tests if the port is open on the host address."""
    sock = socket.socket()
    try:
        sock.connect((address, port))
        return True
    except socket.error:
        return False


def checkPortRange(address, ports, capsule, counter):
    """Checks all ports in the given list.

    Meant to be executed on a separate thread.

    """
    for port in ports:
        with threading.Lock():
            counter.clock()
            capsule[port] = checkPort(address, port)


def check(args):
    """Checks given port range multithreaded."""
    capsule = dict()

    portRange = getPortRange(args.port)
    numTasks = len(portRange)
    numChunks = args.instances or min([numTasks, MAX_THREADS])
    chunks = list(chunkify(portRange, numChunks))
    counter = ThreadedCounter(
        startAt=0,
        maxCount=numTasks,
        verbose=args.verbose)

    threads = []
    for chunk in chunks:
        thread = threading.Thread(
            target=checkPortRange,
            args=(args.address, chunk, capsule, counter))
        threads.append(thread)

    for thread in threads: thread.start()
    for thread in threads: thread.join()

    report(capsule)


def setupArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=str,
        help="port or port range to check (e.g. 435 or 20-1000)")
    parser.add_argument("-a", "--address", type=str, default="localhost",
        help="host to check  [default: localhost]")
    parser.add_argument("-i", "--instances", type=int,
        help=("number of threads to use (uses many by default, "
            "use this setting to decrease the amount"))
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def report(result):
    """Logs open ports to stdout."""
    openPorts = list(filter(lambda itm: itm[1] is True, result.items()))
    log.info("------------------------------")
    log.info("{num} ports have been scanned.".format(num=len(result.items())))
    log.info("{num} open ports found.".format(num=len(openPorts)))
    log.info("------------------------------")
    for port, state in result.items():
        if state:
            log.info("{port} is open.".format(port=port))


def main():
    parser = setupArgParser()
    args = parser.parse_args()
    check(args)


if __name__ == "__main__":
    main()

