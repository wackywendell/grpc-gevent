from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all(thread=False)

import grpc._cython.cygrpc
grpc._cython.cygrpc.init_grpc_gevent()

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

request_choices = dict(plain=request_plain, thread=request_thread)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port', type=int, default=12345)
    parser.add_argument('--safe', action='store_true',
        help='Run with gevent.Timeout outside the call to imap')
    parser.add_argument('function', choices=list(request_choices), nargs='?',
        default='plain')

    args = parser.parse_args()
    request_func = request_choices[args.function]

    channel = grpc.insecure_channel('localhost:%d' % args.port)
    stub = echoserver_grpc.EchoerStub(channel)


    requests = [
        (1, "short 1", 1),
        (2, "short 2", 1),
        (3, "long", 4),
        (4, "middle", 2),
    ]

    start = datetime.now()
    pool = gevent.pool.Pool()

    try:
        if args.safe:
            def map_func(values):
                (i, m, s) = values
                return request_func(stub, i, m, s)

            mapped = pool.imap_unordered(map_func, requests)
            with gevent.Timeout(1.5):
                for rsp in mapped:
                    log(rsp.id, "Returned")

        else:
            def timeout_func(values):
                (i, m, s) = values
                with gevent.Timeout(1.5):
                    return request_func(stub, i, m, s)

            mapped = pool.imap_unordered(timeout_func, requests)
            for rsp in mapped:
                log(rsp.id, "Returned")
    except gevent.Timeout:
        print("Timed out, exiting.")

    end = datetime.now()
    print("Finished in", end - start)

if __name__ == '__main__':
    main()
