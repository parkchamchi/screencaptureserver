import requests
import numpy as np
import cv2

import time

host = "http://127.0.0.1:5000"
method = "jpg"
url = f"{host}/screencaptureserver/{method}"

params={
	"monitor_num": 2, #Has to be changed if you have a secondary mornitor
	#"left": .1,
	#"right": .2,
	#"up": .3,
	#"down": .4
}

print(f"Connecting to {host}, params={params}")

while True:
	last_time = time.time()

	res = requests.get(url, params=params)
	img = res.content

	img = np.frombuffer(img, np.uint8)
	img = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)

	cv2.imshow(f"{params}", img)
	print(f"\rfps: {1 / (time.time() - last_time)}", end="")

	# Press "q" to quit
	if cv2.waitKey(1) & 0xFF == ord("q"):
		cv2.destroyAllWindows()
		break