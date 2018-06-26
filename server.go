package main

import (
	"flag"
	"fmt"
	"log"
	"net"
	"sync/atomic"
	"time"

	"github.com/wackywendell/grpc-gevent/pb"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
)

var port = flag.Int("port", 12345, "The server port")

type Echoer struct {
	count int64
}

func (s *Echoer) Echo(ctx context.Context, req *pb.Request) (*pb.Response, error) {
	if req.SleepSeconds < 0 {
		return nil, fmt.Errorf("Negative sleep time")
	}

	n := atomic.AddInt64(&s.count, 1) - 1

	log.Printf("Received %d message %d: %s", n, req.Id, req.Message)
	time.Sleep(time.Duration(req.SleepSeconds*1000) * time.Millisecond)

	rsp := &pb.Response{
		Id:      req.Id,
		Message: req.Message,
	}

	err := ctx.Err()
	if err != nil {
		log.Printf("Context err %d message %d: %s, err: %s", n, req.Id, req.Message, err)
		return nil, err
	}

	log.Printf("Finished %d message %d: %s", n, req.Id, req.Message)
	return rsp, nil
}

func main() {
	flag.Parse()

	echoer := Echoer{}

	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterEchoerServer(grpcServer, &echoer)
	grpcServer.Serve(lis)
}
