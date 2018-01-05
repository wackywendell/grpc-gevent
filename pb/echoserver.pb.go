// Code generated by protoc-gen-go. DO NOT EDIT.
// source: echoserver.proto

/*
Package pb is a generated protocol buffer package.

It is generated from these files:
	echoserver.proto

It has these top-level messages:
	Request
	Response
*/
package pb

import proto "github.com/golang/protobuf/proto"
import fmt "fmt"
import math "math"

import (
	context "golang.org/x/net/context"
	grpc "google.golang.org/grpc"
)

// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf

// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion2 // please upgrade the proto package

type Request struct {
	Id           int64   `protobuf:"varint,1,opt,name=id" json:"id,omitempty"`
	Message      string  `protobuf:"bytes,2,opt,name=message" json:"message,omitempty"`
	SleepSeconds float32 `protobuf:"fixed32,3,opt,name=sleep_seconds,json=sleepSeconds" json:"sleep_seconds,omitempty"`
}

func (m *Request) Reset()                    { *m = Request{} }
func (m *Request) String() string            { return proto.CompactTextString(m) }
func (*Request) ProtoMessage()               {}
func (*Request) Descriptor() ([]byte, []int) { return fileDescriptor0, []int{0} }

func (m *Request) GetId() int64 {
	if m != nil {
		return m.Id
	}
	return 0
}

func (m *Request) GetMessage() string {
	if m != nil {
		return m.Message
	}
	return ""
}

func (m *Request) GetSleepSeconds() float32 {
	if m != nil {
		return m.SleepSeconds
	}
	return 0
}

type Response struct {
	Id      int64  `protobuf:"varint,1,opt,name=id" json:"id,omitempty"`
	Message string `protobuf:"bytes,2,opt,name=message" json:"message,omitempty"`
}

func (m *Response) Reset()                    { *m = Response{} }
func (m *Response) String() string            { return proto.CompactTextString(m) }
func (*Response) ProtoMessage()               {}
func (*Response) Descriptor() ([]byte, []int) { return fileDescriptor0, []int{1} }

func (m *Response) GetId() int64 {
	if m != nil {
		return m.Id
	}
	return 0
}

func (m *Response) GetMessage() string {
	if m != nil {
		return m.Message
	}
	return ""
}

func init() {
	proto.RegisterType((*Request)(nil), "pb.Request")
	proto.RegisterType((*Response)(nil), "pb.Response")
}

// Reference imports to suppress errors if they are not otherwise used.
var _ context.Context
var _ grpc.ClientConn

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
const _ = grpc.SupportPackageIsVersion4

// Client API for Echoer service

type EchoerClient interface {
	Echo(ctx context.Context, in *Request, opts ...grpc.CallOption) (*Response, error)
}

type echoerClient struct {
	cc *grpc.ClientConn
}

func NewEchoerClient(cc *grpc.ClientConn) EchoerClient {
	return &echoerClient{cc}
}

func (c *echoerClient) Echo(ctx context.Context, in *Request, opts ...grpc.CallOption) (*Response, error) {
	out := new(Response)
	err := grpc.Invoke(ctx, "/pb.Echoer/Echo", in, out, c.cc, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// Server API for Echoer service

type EchoerServer interface {
	Echo(context.Context, *Request) (*Response, error)
}

func RegisterEchoerServer(s *grpc.Server, srv EchoerServer) {
	s.RegisterService(&_Echoer_serviceDesc, srv)
}

func _Echoer_Echo_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Request)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(EchoerServer).Echo(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/pb.Echoer/Echo",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(EchoerServer).Echo(ctx, req.(*Request))
	}
	return interceptor(ctx, in, info, handler)
}

var _Echoer_serviceDesc = grpc.ServiceDesc{
	ServiceName: "pb.Echoer",
	HandlerType: (*EchoerServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "Echo",
			Handler:    _Echoer_Echo_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "echoserver.proto",
}

func init() { proto.RegisterFile("echoserver.proto", fileDescriptor0) }

var fileDescriptor0 = []byte{
	// 173 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0x8c, 0x8f, 0xb1, 0xce, 0x82, 0x30,
	0x14, 0x46, 0xff, 0x96, 0x3f, 0xa0, 0x57, 0x34, 0xa6, 0x53, 0xe3, 0x44, 0x60, 0x61, 0x91, 0x41,
	0x7d, 0x05, 0x5f, 0xa0, 0x2e, 0x6e, 0x46, 0xe0, 0x8b, 0x90, 0x28, 0xad, 0xbd, 0xe8, 0xf3, 0x1b,
	0x41, 0x77, 0xb7, 0x7b, 0xce, 0x70, 0x72, 0x3f, 0x5a, 0xa2, 0x6a, 0x2c, 0xc3, 0x3f, 0xe1, 0x0b,
	0xe7, 0x6d, 0x6f, 0x95, 0x74, 0x65, 0x7a, 0xa4, 0xc8, 0xe0, 0xfe, 0x00, 0xf7, 0x6a, 0x41, 0xb2,
	0xad, 0xb5, 0x48, 0x44, 0x1e, 0x18, 0xd9, 0xd6, 0x4a, 0x53, 0x74, 0x03, 0xf3, 0xf9, 0x02, 0x2d,
	0x13, 0x91, 0x4f, 0xcd, 0x17, 0x55, 0x46, 0x73, 0xbe, 0x02, 0xee, 0xc4, 0xa8, 0x6c, 0x57, 0xb3,
	0x0e, 0x12, 0x91, 0x4b, 0x13, 0x0f, 0xf2, 0x30, 0xba, 0x74, 0x47, 0x13, 0x03, 0x76, 0xb6, 0x63,
	0xfc, 0x9e, 0xde, 0xac, 0x29, 0xdc, 0x57, 0x8d, 0x85, 0x57, 0x19, 0xfd, 0xbf, 0x2f, 0x35, 0x2b,
	0x5c, 0x59, 0x7c, 0x7e, 0x5c, 0xc5, 0x23, 0x8c, 0xd9, 0xf4, 0xaf, 0x0c, 0x87, 0x25, 0xdb, 0x57,
	0x00, 0x00, 0x00, 0xff, 0xff, 0x6f, 0x45, 0xf3, 0x9a, 0xdd, 0x00, 0x00, 0x00,
}
