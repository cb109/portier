import time
import socket
import logging
import argparse
import threading
import multiprocessing

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s | %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger("portier")


class Counter(object):

    def __init__(self, startAt=0, maxCount=100, verbose=True):
        self.current = startAt
        self.max = maxCount
        self.verbose = verbose
        self.lock = None

    def _increment(self):
        raise NotImplementedError

    def _getValue(self):
        raise NotImplementedError

    def clock(self):
        with self.lock:
            self._increment()
            if self.verbose:
                value = self._getValue()
                percent = value / (self.max / 100.0)
                log.info("{value}/{self.max} "
                    "- {percent:.2f}%".format(**locals()))

class ThreadedCounter(Counter):

    def __init__(self, startAt=0, maxCount=100, verbose=True):
        Counter.__init__(self, startAt, maxCount, verbose)
        self.lock = threading.Lock()

    def _increment(self):
        self.current += 1

    def _getValue(self):
        return self.current


class ProcessedCounter(Counter):

    def __init__(self, startAt=0, maxCount=100, verbose=True):
        Counter.__init__(self, startAt, maxCount, verbose)
        self.current = multiprocessing.Value("i", startAt)
        self.max = maxCount
        self.verbose = verbose
        self.lock = multiprocessing.Lock()

    def _increment(self):
        self.current.value += 1

    def _getValue(self):
        return self.current.value




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
    sock = socket.socket()
    try:
        sock.connect((address, port))
        return True
    except socket.error:
        return False


def checkPortRangeAsync(address, ports, capsule, counter):
    for port in ports:
        with multiprocessing.Lock():
            counter.clock()
            capsule[port] = checkPort(address, port)


def checkPortRangeAsyncMapped(args):
    address, ports, capsule, v = args
    checkPortRangeAsync(address, ports, capsule, v)


def report(result):
    openPorts = list(filter(lambda itm: itm[1] is True, result.items()))
    log.info("------------------------------")
    log.info("{num} ports habe been scanned.".format(num=len(result.items())))
    log.info("{num} open ports found.".format(num=len(openPorts)))
    log.info("------------------------------")
    for port, state in result.items():
        if state:
            log.info("{port} is open.".format(port=port))


def processed(args):
    s = time.time()
    manager = multiprocessing.Manager()
    capsule = manager.dict()

    portRange = getPortRange(args.port)
    chunks = list(chunkify(portRange, args.cores))

    counter = ProcessedCounter(0, len(portRange))

    processes = []
    for chunk in chunks:
        proc = multiprocessing.Process(target=checkPortRangeAsync,
            args=(args.address, chunk, capsule, counter))
        processes.append(proc)

    for proc in processes: proc.start()
    for proc in processes: proc.join()

    result = dict(capsule)
    report(result)

    e = time.time()
    log.info("checking processed" + str(len(portRange)) + " ports took " + str(e-s) + " seconds")


def threaded(args):
    s = time.time()
    capsule = dict()

    portRange = getPortRange(args.port)
    chunks = list(chunkify(portRange, args.cores))

    counter = ThreadedCounter(0, len(portRange))

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=checkPortRangeAsync,
            args=(args.address, chunk, capsule, counter))
        threads.append(thread)

    for thread in threads: thread.start()
    for thread in threads: thread.join()

    result = dict(capsule)
    report(result)

    e = time.time()
    log.info("checking threaded" + str(len(portRange)) + " ports took " + str(e-s) + " seconds")



def setupArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=str,
        help="port or port range to check (e.g. 435 or 20-1000)")
    parser.add_argument("-a", "--address", type=str, default="localhost",
        help="host to check  [default: localhost]")
    parser.add_argument("-v", "--verbosity", action="store_true",
        help="output debug information")
    parser.add_argument("-c", "--cores", type=int,
        help="number of cores to use", default=multiprocessing.cpu_count())
    return parser


if __name__ == "__main__":
    parser = setupArgParser()
    args = parser.parse_args()

    processed(args)
    # threaded(args)

