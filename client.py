from __future__ import print_function

import pb.echoserver_pb2 as echoserver
import pb.echoserver_pb2_grpc as echoserver_grpc

import grpc

channel = grpc.insecure_channel('localhost:12345')
stub = echoserver_grpc.EchoerStub(channel)

resp = stub.Echo(echoserver.Request(id=0, message="Hello", sleep_seconds=3.0))

print(resp)
