from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import grpc._cython.cygrpc
grpc._cython.cygrpc.init_grpc_gevent()

import argparse
from datetime import datetime
import random
import sys
import time

import pb.echoserver_pb2 as echoserver
import pb.echoserver_pb2_grpc as echoserver_grpc

import grpc
import gevent.pool
import gevent.queue


def log(id, msg, *args):
        print(str(datetime.now()), '[%2d]' % id, msg % args)


class TimeoutException(Exception):
    pass

class Parallelized(object):
    """
    Will use `gevent` to run `func` in parallel over `iterable`, if possible;
    otherwise, it will just use a serial runner.

    Equivalent to imap(func, iterable), except order is not guaranteed.

    This can hopefully one day be replaced with gevent.pool.Group.imap_unordered,
    but this class abstracts out the feature flagged parallelization, as well as
    integrating with trace.
    """
    def __init__(self, func, iterable, timeout=None, max_size=None, sleep_between=0.01):
        """
        params:

        func: function to run on each item in iterable
        iterable: items to run over
        timeout:
            timeout for each item. Only used with gevent. None (default) blocks forever.
        max_size (int or None): when not None, the amount of concurrent
            greenlets is limited to this number
        sleep_between (float): Seconds to wait between spawning each request
        """
        self.func = func
        self.iterable = list(iterable)
        self.timeout = timeout
        self._gevent_pool = None
        self.max_size = max_size
        self.sleep_between = sleep_between

    def __iter__(self):
        for is_ok, value in self.safe_iter():
            if not is_ok:
                # Raise exception with its original traceback
                raise value[0], value[1], value[2]
            yield value

    def safe_iter(self):
        # We run the function, and either get the value or the exception raised.
        # We put a flag is_ok in the flag to denote which it is.
        queue = gevent.queue.Queue()
        if self.max_size is None:
            pool = self._gevent_pool = gevent.pool.Group()
        else:
            pool = self._gevent_pool = gevent.pool.Pool(size=self.max_size)

        def spawn_func(item):
            try:
                value = self.func(item)
                return (True, value)
            except Exception:
                exc_info = sys.exc_info()
                return (False, exc_info)

        return pool.imap_unordered(spawn_func, self.iterable)

    def kill(self):
        if self._gevent_pool is not None:
            self._gevent_pool.kill()


class Requester(object):
    def __init__(self, ports, id, max_sleep, sleep_between, timeout=None):
        self.ports = ports
        self.max_sleep = max_sleep
        self.sleep_between = sleep_between
        self.timeout = timeout

    def sleep_amount(self):
        return random.random() * self.max_sleep

    def request(self, client, id, msg):
        """
        Each request blocks gevent in normal operation.
        """
        if random.random() < 0.01:
            # cause a grpc error
            id=-id

        req = echoserver.Request(id=id, message=msg, sleep_seconds=self.sleep_amount())

        resp = client.Echo(req)
        return resp

    def batch(self, id, count=10):
        requests = (
            (id+n, random.choice(self.ports), "rid-%d" % n)
            for n in range(count)
        )

        def request_map(values):
            (i, p, m) = values

            channel = grpc.insecure_channel('localhost:%d' % p)
            client = echoserver_grpc.EchoerStub(channel)
            rv = self.request(client, i, m)
            return rv

        p = Parallelized(request_map, requests,
            timeout=self.timeout, sleep_between=self.sleep_between)

        vals = []
        for val in p:
            vals.append(val)
        return vals



def comma_separated_ints(s):
    return [int(p) for p in s.split(',')]

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--ports', type=comma_separated_ints, default=comma_separated_ints('12345'))
    parser.add_argument('-n', dest='request_count', type=int, default=20, help="Requests per branch")
    parser.add_argument('-t', '--sleep-time', dest='sleep_time', type=float, default=10.0)
    parser.add_argument('--sleep-between', dest='sleep_between', type=float, default=0.05)
    parser.add_argument('-b', '--branch-count', dest='branch_count', type=int, default=100)
    parser.add_argument('--batch-timeout', dest='batch_timeout', type=int, default=None)

    args = parser.parse_args()


    start = datetime.now()

    def multi_request_map(vs):
        id, sleep_time = vs

        gevent.sleep(random.random() * args.sleep_between)
        requester = Requester(args.ports, id, sleep_time, args.sleep_between,
            timeout=None)
        return id, requester.batch(id, count=args.request_count)

    vals = (
        (n*10*args.request_count, args.sleep_time*(args.branch_count - n + 1)/args.branch_count)
        for n in range(args.branch_count)
    )

    p = Parallelized(multi_request_map, vals, timeout=args.batch_timeout)

    for is_ok, val in p.safe_iter():
        if not is_ok:
            log(0, "Err returned: %s", val)
            continue
        i, mr = val
        log(i, "Returned %d", len(mr))

    end = datetime.now()
    print("Finished in", end - start)

if __name__ == '__main__':
    main()