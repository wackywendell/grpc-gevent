protos: pb/echoserver.pb.go pb/echoserver_pb2.py pb/echoserver_pb2_grpc.py pb/__init__.py

pb/echoserver.pb.go: proto/echoserver.proto
	protoc -I=proto --go_out=plugins=grpc:pb proto/echoserver.proto

pb/__init__.py:
	touch pb/__init__.py

pb/echoserver_pb2.py: proto/echoserver.proto
	python -m grpc.tools.protoc -I proto --proto_path=pb/ --python_out=pb/ --grpc_python_out=pb/ proto/echoserver.proto

pb/echoserver_pb2_grpc.py: proto/echoserver.proto
	python -m grpc.tools.protoc -I proto --proto_path=pb/ --python_out=pb/ --grpc_python_out=pb/ proto/echoserver.proto

setup:
	go get github.com/golang/protobuf/protoc-gen-go
	go get google.golang.org/grpc
	pip install --user grpcio-tools==1.2.1
