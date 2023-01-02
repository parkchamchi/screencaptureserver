import requests

import tkinter as tk

class Screen:
	def __init__(self, w, h):
		self.w = w
		self.h = h

		self.borders = [(0, 0), (1, 1)]

	def set_border(self, x, y, border_idx):
		assert border_idx in [0, 1]

		self.borders[border_idx] = ((x/self.w, y/self.h))

	def get_margins(self):
		left = min(self.borders, key=lambda x: x[0])[0]
		up = min(self.borders, key=lambda x: x[1])[1]
		right = 1 - max(self.borders, key=lambda x: x[0])[0]
		down = 1 - max(self.borders, key=lambda x: x[1])[1]

		margins = {}
		for key, value in zip(["left", "up", "right", "down"], [left, up, right, down]):
			margins[key] = str(float(value * 100))

		return margins

screen = Screen(0, 0)
host = "http://localhost:5000/scserver"

def get(url, params=None) -> bytes:
	res = requests.get(url, params=params)
	img = res.content

	return img

def update():
	global screen, lbl_image
	
	url = f"{host}/default/png"
	ppm = get(url)
	newimage = tk.PhotoImage(data=ppm, format="PNG")

	#subsample such that the height is about 720px
	# h / x == 720
	# x == h / 720

	newimage = newimage.subsample(newimage.height() // 720)
	lbl_image.configure(image=newimage)
	lbl_image.image = newimage

	screen = Screen(newimage.width(), newimage.height())
	#show_borders()

def clicked(event):
	num = event.num
	if num == 1: #left click
		border_idx = 0
	elif num == 3: #right licke
		border_idx = 1
	else:
		return

	x, y = event.x, event.y

	screen.set_border(x, y, border_idx)
	show_borders()

	margins = screen.get_margins()
	print(margins)
	requests.put(f"{host}/gui/margins", json=margins)

def show_borders():
	global lbl_borders, lbl_image

	absx, absy = lbl_image.winfo_x(), lbl_image.winfo_y()

	for lbl_border, (x, y) in zip(lbl_borders, screen.borders):
		lbl_border.place(x=(absx + x*screen.w), y=(absy + y*screen.h))

window = tk.Tk()

frm_control = tk.Frame(master=window, relief=tk.GROOVE)

btn_update = tk.Button(master=frm_control, text="Update", command=update)
btn_update.pack(side=tk.LEFT)

frm_control.pack()

lbl_image = tk.Label()
lbl_image.bind("<Button>", clicked)
lbl_image.pack()

lbl_borders = [tk.Label(bg=color, fg="white", text='↖') for color in ["red", "blue"]]
for e in lbl_borders:
	e.place(x=0, y=0)

window.mainloop()