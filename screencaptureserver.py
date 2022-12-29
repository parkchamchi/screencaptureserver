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

	#margins: {left, right, top, down}

	monitor = sct.monitors[monitor_num]

	if margins is not None:
		left_m = int(monitor["width"] * margins["left"])
		monitor["left"] += left_m
		monitor["width"] -= left_m
		monitor["width"] -= int(monitor["width"] * margins["right"])

		up_m = int(monitor["height"] * margins["up"])
		monitor["top"] += up_m
		monitor["height"] -= up_m
		monitor["height"] -= int(monitor["height"] * margins["down"])

	w = monitor["width"]
	h = monitor["height"]
	if w <= 0 or h <= 0:
		raise ValueError(f'Illegal shape {w}x{h} on margins={margins}, monitor_num={monitor_num}')
	#print(margins, monitor_num)
	#print(monitor)

	grabbed = sct.grab(monitor)
	return grabbed

@app.route("/screencaptureserver/<method>")
def parse(method):
	"""
	Returns a png bytestring

	parameters:
		monitor_num: defaults to 0 if not given
		MARGINS: all parameters (left, right, up, down) should be given. (Currently not used)
	"""

	args = flask.request.args

	monitor_num = int(args["monitor_num"]) if "monitor_num" in args else 0

	margins = None
	#This feature seems to be broken for a single mss object
	"""
	margins = {}
	for key in ["left", "right", "up", "down"]:
		if key not in args:
			margins = None
			break
		margins[key] = float(args[key])
	"""

	#with mss.mss() as sct:
	global sct
	try:
		grabbed = get_screen(sct, monitor_num, margins)
	except ValueError as exc:
		print("EXCEPTION")
		traceback.print_exc()
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