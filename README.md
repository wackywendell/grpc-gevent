## Description

This is an example repository showing what happens if you use `gevent` with `grpc`, and demonstrating that
running grpc calls in a gevent.threadpool allows gevent to run normally.

## Setup

You can run `make setup`, or read the Makefile and copy the directions there as you see fit.

## Running

In one terminal:

```bash
$ go run server.go
```

In another terminal:

```bash
$ python client.py
2018-01-05 16:53:24.637027 [ 1] Started
2018-01-05 16:53:24.637386 [ 1] Spawned
2018-01-05 16:53:24.637804 [ 2] Started
2018-01-05 16:53:24.638113 [ 2] Spawned
2018-01-05 16:53:24.638290 [ 3] Started
2018-01-05 16:53:24.638590 [ 3] Spawned
...
2018-01-05 16:53:25.645519 [ 1] Received
2018-01-05 16:53:25.645593 [ 2] Received
2018-01-05 16:53:25.645652 [11] Received
2018-01-05 16:53:26.642848 [ 4] Received
...
Finished in 0:00:10.016921
```

Note that `python client.py plain` will attempt to use gevent with grpc and just be synchronous (taking >50 s), whereas the default `python client.py` uses the gevent threadpool to actually do concurrent grpc requests and finishes in ~10 seconds.

## Load testing

To run a load test:

In one terminal:

```bash
$ go run server.go -port 12340
```

In another terminal:

```bash
$ loadtest.py -p 12340 -n 10 -b 10
```

You should see an error that looks something like this:

```raw
Traceback (most recent call last):
  File "grpc-gevent/lib/python2.7/site-packages/gevent/event.py", line 219, in wait
    return self._wait(timeout)
  File "grpc-gevent/lib/python2.7/site-packages/gevent/event.py", line 129, in _wait
    gotit = self._wait_core(timeout)
  File "grpc-gevent/lib/python2.7/site-packages/gevent/event.py", line 106, in _wait_core
    result = self.hub.switch()
  File "grpc-gevent/lib/python2.7/site-packages/gevent/hub.py", line 630, in switch
    return RawGreenlet.switch(self)
greenlet.GreenletExit
Exception greenlet.GreenletExit: GreenletExit() in 'grpc._cython.cygrpc.run_loop' ignored
```