## Description

This is a minimal example demonstrating an issue with the current grpc experimental support and timeouts.

## Setup

You can run `make setup`, or read the Makefile and copy the directions there as you see fit.

## Running

In one terminal:

```bash
$ go run server.go
```

In another terminal:

```text
$ python client.py
2018-06-26 12:28:45.401972 [ 1] Started
2018-06-26 12:28:45.402720 [ 2] Started
2018-06-26 12:28:45.402882 [ 3] Started
2018-06-26 12:28:45.403063 [ 4] Started
2018-06-26 12:28:46.420758 [ 2] Received
2018-06-26 12:28:46.420957 [ 1] Received
Traceback (most recent call last):
  File "src/gevent/event.py", line 240, in gevent._event.Event.wait
  File "src/gevent/event.py", line 140, in gevent._event._AbstractLinkable._wait
  File "src/gevent/event.py", line 117, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/event.py", line 125, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/event.py", line 119, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 63, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/__greenlet_primitives.pxd", line 35, in gevent.__greenlet_primitives._greenlet_switch
gevent.timeout.Timeout: 1.5 seconds
Exception gevent.timeout.Timeout: <Timeout at 0x1058b8be0 seconds=1.5> in 'grpc._cython.cygrpc.run_loop' ignored
Traceback (most recent call last):
  File "src/gevent/event.py", line 240, in gevent._event.Event.wait
  File "src/gevent/event.py", line 140, in gevent._event._AbstractLinkable._wait
  File "src/gevent/event.py", line 117, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/event.py", line 125, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/event.py", line 119, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 63, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/__greenlet_primitives.pxd", line 35, in gevent.__greenlet_primitives._greenlet_switch
gevent.timeout.Timeout: 1.5 seconds
Exception gevent.timeout.Timeout: <Timeout at 0x1058c60a0 seconds=1.5> in 'grpc._cython.cygrpc.run_loop' ignored
2018-06-26 12:28:47.418784 [ 4] Received
Exception while running: 'NoneType' object has no attribute 'id'
Finished in 0:00:03.006112
```

## With threading

You can also run `python client.py thread` and see a different error:

```raw
$ 2018-06-26 12:31:10.974334 [ 1] Started
2018-06-26 12:31:10.974531 [ 1] Spawned
2018-06-26 12:31:10.974604 [ 2] Started
Traceback (most recent call last):
  File "src/gevent/event.py", line 240, in gevent._event.Event.wait
  File "src/gevent/event.py", line 140, in gevent._event._AbstractLinkable._wait
  File "src/gevent/event.py", line 117, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/event.py", line 119, in gevent._event._AbstractLinkable._wait_core
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 59, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/_greenlet_primitives.py", line 63, in gevent.__greenlet_primitives.SwitchOutGreenletWithLoop.switch
  File "src/gevent/__greenlet_primitives.pxd", line 35, in gevent.__greenlet_primitives._greenlet_switch
greenlet.error: cannot switch to a different thread2018-06-26 12:31:10.975160 [ 2] Spawned
2018-06-26 12:31:10.976075 [ 3] Started
2018-06-26 12:31:10.976193 [ 3] Spawned
2018-06-26 12:31:10.976259 [ 4] Started
2018-06-26 12:31:10.976535 [ 4] Spawned
[...]
```

Locally, this causes ~20k log lines.

## Running with `--safe`

Using `python client.py --safe` uses slightly different code around the timeout to wrap around the entire pool instead of individual tasks. Note that this is effective for `python client.py --safe plain` - it runs asynchronously, times out correctly, and cancels the grpc calls correctly - but `python client.py --safe thread` suffers the same problems as before, with ~20k log lines and errors as above.