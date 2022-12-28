# Screen Capture Server
When requested, captures the screen and returns the image data.

## Usage
Open the server.
```
python screencaptureserver.py
```
Send a GET request (utilize [test.py](./test.py))
```
GET localhost:5000/screencaptureserver/jpg
```
To capture the second monitor:
```
GET localhost:5000/screencaptureserver/jpg?monitor_num=2
```

### Supported methods
- jpg
- png
- raw_bgra
- ppm (unoptimized)

## Benchmark
For 1080p, I could get 20fps for videos and 30fps for relatively still screens.

## Misc
This program uses [python-mss](https://github.com/BoboTiG/python-mss)<br>
This program is a side project for [DepthViewer](https://github.com/parkchamchi/DepthViewer)<br>
<br>
Just realized that [a project that uses the same name](https://github.com/aviloria/ScreenCaptureServer) exists. It's written in C++ for Windows.