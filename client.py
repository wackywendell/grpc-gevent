from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all(thread=False)

import argparse
from datetime import datetime

import pb.echoserver_pb2 as echoserver
import pb.echoserver_pb2_grpc as echoserver_grpc

import grpc
import gevent.pool
import gevent.threadpool
import gevent.event

def log(id, msg, *args):
        print(str(datetime.now()), '[%2d]' % id, msg % args)

def request_plain(client, id, msg, sleep_secs):
    """
    Each request blocks gevent in normal operation.
    """
    req = echoserver.Request(id=id, message=msg, sleep_seconds=sleep_secs)
    log(req.id, "Started")
    resp = client.Echo(req)
    log(req.id, "Received")
    return resp

threadpool = gevent.get_hub().threadpool
# threadpool = gevent.threadpool.ThreadPool
# threadpool takes a `maxsize` argument, but that's irrelevant here.

def request_thread(client, id, msg, sleep_secs):
    """
    Using a threadpool gets around this.
    """
    req = echoserver.Request(id=id, message=msg, sleep_seconds=sleep_secs)
    log(req.id, "Started")
    ar = threadpool.spawn(client.Echo, req, timeout=20)
    log(req.id, "Spawned")
    resp = ar.wait()
    log(req.id, "Received")
    return resp


def request_future(client, id, msg, sleep_secs):
    """
    Using grpc futures.

    This half-works, and fails in what may seem like a surprising way:
    > This operation would block forever

    This is because grpc creates threads that are not controlled by gevent.
    gevent is an event loop that needs something to do at all times; if its
    told to "wait" for an AsyncResult, it will simply jump to another greenlet
    and mark the waiting greenlet as "waiting". If all greenlets are "waiting"
    for an AsyncResult, then it doesn't know what is left to do; it assumes
    that AsyncResults are set by threads, so therefore it believes its deadlocked.

    In addition, this is probably also racy; gevent.AsyncResult is not threadsafe.
    """

    req = echoserver.Request(id=id, message=msg, sleep_seconds=sleep_secs)
    log(req.id, "Started")
    future = client.Echo.future(req, timeout=20)
    log(req.id, "Future created")
    ar = gevent.event.AsyncResult()
    future.add_done_callback(lambda f: ar.set(f.result()))
    log(req.id, "Async Result added")
    resp = ar.wait()
    log(req.id, "Received")
    return resp

request_choices = dict(plain=request_plain, thread=request_thread, future=request_future)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port', type=int, default=12345)
    parser.add_argument('hack', choices=list(request_choices), nargs='?',
        default='thread')

    args = parser.parse_args()
    request_func = request_choices[args.hack]

    channel = grpc.insecure_channel('localhost:%d' % args.port)
    stub = echoserver_grpc.EchoerStub(channel)


    requests = [
        (1, "short 1", 1),
        (2, "short 2", 1),
        (3, "long", 4),
        (4, "middle", 2),
    ] + [
        (10 + n, "sequential %d" % n, n) for n in range(10)
    ]

    map_func = lambda (i, m, s): request_func(stub, i, m, s)

    start = datetime.now()
    pool = gevent.pool.Pool()
    mapped = pool.imap_unordered(map_func, requests)

    gevent.sleep(3)

    try:
        for rsp in mapped:
            log(rsp.id, "Returned")
    except Exception as e:
        print("Exception while running:", e)

    end = datetime.now()
    print("Finished in", end - start)

if __name__ == '__main__':
    main()
