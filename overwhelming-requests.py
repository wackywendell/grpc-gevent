from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import grpc._cython.cygrpc
grpc._cython.cygrpc.init_grpc_gevent()

import argparse
from datetime import datetime
import random

import pb.echoserver_pb2 as echoserver
import pb.echoserver_pb2_grpc as echoserver_grpc

import grpc
import gevent.pool

def log(id, msg, *args):
        print(str(datetime.now()), '[%2d]' % id, msg % args)

def request(client, id, msg, sleep_secs):
    """
    Each request blocks gevent in normal operation.
    """
    if random.random() < 0.01:
        # cause a grpc error
        id=-id

    req = echoserver.Request(id=id, message=msg, sleep_seconds=sleep_secs)

    resp = client.Echo(req)
    return resp

def multi_requester(client, id, sleep_time_func, count=10):
    requests = [
        (id+n, "rid-%d" % n, sleep_time_func())
        for n in range(count)
    ]

    def request_map(values):
        (i, m, s) = values
        try:
            return request(client, i, m, s)
        except Exception as e:
            log(i, "Error: %s", e)
            return e

    pool = gevent.pool.Pool()
    mapped = pool.imap_unordered(request_map, requests)

    return list(mapped)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port', type=int, default=12345)
    parser.add_argument('-n', dest='request_count', type=int, default=1000)
    parser.add_argument('-t', '--sleep-time', dest='sleep_time', type=float, default=2.0)
    parser.add_argument('-b', '--branch-count', dest='branch_count', type=int, default=10)

    args = parser.parse_args()

    channel = grpc.insecure_channel('localhost:%d' % args.port)
    client = echoserver_grpc.EchoerStub(channel)

    start = datetime.now()
    pool = gevent.pool.Pool()

    per_branch = args.request_count // args.branch_count
    def multi_request_map(id):
        t_func = lambda: random.randrange(args.sleep_time)
        return id, multi_requester(client, id, t_func, count=per_branch)

    ids = [n*10*per_branch for n in range(args.branch_count)]

    mapped = pool.imap_unordered(multi_request_map, ids)

    try:
        for i, mr in mapped:
            log(i, "Returned")
    except Exception as e:
        print("Exception while running:", e)

    end = datetime.now()
    print("Finished in", end - start)

if __name__ == '__main__':
    main()