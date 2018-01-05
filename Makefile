pb/echoserver.pb.go: proto/echoserver.proto
	protoc -I=proto --go_out=plugins=grpc:pb proto/echoserver.proto

gets:
	go get github.com/golang/protobuf/protoc-gen-go
	go get google.golang.org/grpc
