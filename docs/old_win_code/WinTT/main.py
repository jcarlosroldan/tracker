from winapi import *
from utils import *

__private_filters = None
def is_private(task):
	global __private_filters
	if __private_filters == None:
		try:
			with open(abspath(join(path[0], PATH_PRIVATE)), "r", encoding="utf-8") as f:
				__private_filters = f.read().split("\n")
		except:
			__private_filters = []
	ltask = task.lower()
	return any(f in ltask for f in __private_filters)

__reads_until_beat = 0
def beat():
	global __reads_until_beat
	__reads_until_beat -= 1
	if __reads_until_beat <= 0:
		__reads_until_beat = TIME_BETWEEN_BEATS / TIME_BETWEEN_READS
		with open(PATH_LOCK, "w") as fp:
			fp.write(str(time()))

__last_m = None
def mouse_distance(m):
	global __last_m
	if __last_m == None:
		res = 0
	else:
		res = sqrt((__last_m[0] - m[0])**2 + (__last_m[1] - m[1])**2)
	__last_m = m
	return res

def track(tray_app):
	total_mbuttons = 0
	total_wheel = 0
	total_keys = 0
	total_gamepad = 0
	total_mouse_distance = 0
	previous_state = None
	idle = False
	log(AC_START_TRACKING)
	while tray_app.running:
		process, caption, mbuttons, wheel, keys, gamepad, mouse, fullscreen = info()
		if process == None: continue  # OS PIDs changed during read
		if idle_toggled(mbuttons, wheel, keys, gamepad, mouse, fullscreen):
			idle = not idle
			tray_app.change("idle" if idle else "base")
			log(AC_IDLE_ON if idle else AC_IDLE_OFF)
		if not idle:
			if tray_app.private and is_private(caption):
				pid = AC_PRIVATE
				cid = AC_NONE
				tray_app.change("private")
			else:
				if previous_state != None and previous_state[0] == AC_PRIVATE: tray_app.change("base")
				pid = text2id(process)
				cid = text2id(caption)
			total_mbuttons += mbuttons
			total_wheel += wheel
			total_keys += keys
			total_gamepad += gamepad
			total_mouse_distance += mouse_distance(mouse)
			if (pid, cid) != previous_state:
				log(pid, cid, total_mbuttons, total_wheel, total_keys, total_gamepad, total_mouse_distance)
				previous_state = (pid, cid)
				total_mbuttons = 0
				total_wheel = 0
				total_keys = 0
				total_gamepad = 0
				total_mouse_distance = 0
		beat()
		sleep(TIME_BETWEEN_READS)
		tray_app.check()
	log(AC_END_TRACKING)


if __name__ == "__main__":
	ta = TrayApp()
	try:
		makedirs(BASE, exist_ok=True)
		if is_singleton():
			register(ta.end)
			track(ta)
		else:
			ta.change("alert", "PyTracker will end soon")
			ta.popup("Already running", "Another instance was already running a few seconds ago.", 1)
	except (SystemExit, KeyboardInterrupt):
		pass
	except:
		ta.change("alert", "PyTracker will end soon")
		ta.msgbox(format_exc(), "An exception occurred")
	ta.end(save=False)