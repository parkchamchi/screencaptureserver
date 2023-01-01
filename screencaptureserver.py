import mss
import flask
from PIL import Image
import numpy as np

import traceback
import io

app = flask.Flask(__name__)

def get_screen(sct, monitor_num, margins: dict=None):
	"""
	returns `mss.base.ScreenShot` obj.
	"""

	#margins: {left, right, top, down}, with values = [0, ..., 1)

	monitor = sct.monitors[monitor_num].copy()

	if margins is not None:
		left_m = int(monitor["width"] * margins["left"])
		right_m = int(monitor["width"] * margins["right"])

		monitor["left"] += left_m
		monitor["width"] -= left_m
		monitor["width"] -= right_m

		up_m = int(monitor["height"] * margins["up"])
		down_m = int(monitor["height"] * margins["down"])

		monitor["top"] += up_m
		monitor["height"] -= up_m
		monitor["height"] -= down_m

	w = monitor["width"]
	h = monitor["height"]
	if w <= 0 or h <= 0:
		raise ValueError(f'Illegal shape {w}x{h} on margins={margins}, monitor_num={monitor_num}')

	grabbed = sct.grab(monitor)
	return grabbed

@app.route("/screencaptureserver/<method>")
@app.route("/scserver/<method>")
def parse(method):
	"""
	Returns a png bytestring

	parameters:
		monitor_num: defaults to 0 if not given
		MARGINS: {left, right, up, down} can be given, as percentage to be cut

	e.g.
		/scserver/jpg?monitor_num=2&left=50
	"""

	args = flask.request.args

	monitor_num = int(args["monitor_num"]) if "monitor_num" in args else 0

	margins = None
	#This feature seems to be broken for a single mss object
	margins = {}
	for key in ["left", "right", "up", "down"]:
		margins[key] = (float(args[key]) / 100) if key in args else 0

	#with mss.mss() as sct:
	global sct
	try:
		grabbed = get_screen(sct, monitor_num, margins)
	except ValueError as exc:
		print('\n', '*'*32, "EXCEPTION", '*'*32)
		traceback.print_exc()
		print('*'*75)

		flask.abort(404)

	#Tested on 1080p video
	if method == "png": #8fps
		return mss.tools.to_png(grabbed.rgb, grabbed.size) #main overhead

	elif method == "jpg": #20fps
		with Image.frombytes("RGB", grabbed.size, grabbed.bgra, "raw", "BGRX") as img:
			with io.BytesIO() as bio:
				img.save(bio, format="JPEG")
				jpg = bio.getvalue()

		return jpg

	elif method == "raw_bgra": #4bytes per pixel -- shape data has to be returned too
		return grabbed.bgra

	elif method == "ppm": #similar to jpg
		w, h = grabbed.size.width, grabbed.size.height
		ppm = b"P6\n" + "{} {} {}\n".format(w, h, 255).encode("ascii")
		ppm += grabbed.rgb

		return ppm

	else:
		print(f"Illegal method {method}")
		flask.abort(404)

if __name__ == "__main__":
	sct = mss.mss()
	app.run()