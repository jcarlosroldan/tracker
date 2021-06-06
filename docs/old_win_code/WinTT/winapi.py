from utils import *
from stats import *

OpenProcess = WinDLL('kernel32.dll').OpenProcess
GetProcessImageFileName = WinDLL('Psapi.dll').GetProcessImageFileNameA

def is_singleton():
	if isfile(PATH_LOCK):
		with open(PATH_LOCK, "r") as fp:
			last_beat = float(fp.read())
	else:
		last_beat = 0
	return time() - last_beat > TIME_BETWEEN_BEATS * 2

def canonical(text):
	return text.replace("\ufffd", "_").replace("\t", " ").replace("\n", " ")

__last_mouse = None
__idle_steps = 0
__idle = False
def idle_toggled(mbuttons, wheel, keys, gamepad, mouse, fullscreen):
	global __last_mouse, __idle, __idle_steps
	if mouse == __last_mouse and keys + wheel + mbuttons + gamepad == 0:
		__idle_steps += 1
	else:
		__idle_steps = 0
	if fullscreen:
		idle = __idle_steps >= READS_UNTIL_IDLE_FULLSCREEN
	else:
		idle = __idle_steps >= READS_UNTIL_IDLE
	res = idle != __idle

	__last_mouse = mouse
	__idle = idle

	return res

class InputListener:
	def __init__(self):
		self.running = True
		self.mouse_strokes = 0
		self.mouse_wheel = 0
		self.key_strokes = 0
		self.gamepad = 0
		ms = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
		ks = keyboard.Listener(on_release=self.on_release)
		gs = Thread(target=self.listen_gamepad)
		ms.start()
		ks.start()
		gs.start()

	def on_release(self, key):
		self.key_strokes += 1
		return self.running

	def on_click(self, x, y, button, pressed):
		if pressed: self.mouse_strokes += 1
		return False

	def on_scroll(self, x, y, dx, dy):
		self.mouse_wheel += 1

	def listen_gamepad(self):
		while self.running:
			sleep(1)  # todo: implement gamepad

	def read(self):
		res = self.mouse_strokes, self.mouse_wheel, self.key_strokes, self.gamepad
		self.mouse_strokes = self.mouse_wheel = self.key_strokes = self.gamepad = 0
		return res

_il = None
def info():
	""" Returns (current process, current caption, number of keystrokes since
	last time called, mouse position, is_fullscreen). Keystrokes take mouse
	buttons and gamepads into account. """
	global _il
	fw = GetForegroundWindow()
	process = None
	pid = GetWindowThreadProcessId(fw)[1]
	hproc = OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
	if hproc:
		fname = (c_char * MAX_PATH)()
		if GetProcessImageFileName(hproc, fname, MAX_PATH) > 0:
			process = canonical(fname.value.decode('iso-8859-15', errors='replace'))
	caption = canonical(GetWindowText(fw))
	try:
		mouse = GetCursorPos()
	except:
		mouse = None
	if _il == None: _il = InputListener()
	mbuttons, wheel, keys, gamepad = _il.read()
	fullscreen = False
	return process, caption, mbuttons, wheel, keys, gamepad, mouse, fullscreen

def log(pid, cid=AC_NONE, mbuttons=0, wheel=0, keys=0, gamepad=0, mouse_distance=0):
	""" Log an activity record. """
	text = "%s\t%s\t%s\t%s\t%d\t%d\t%d\t%d\n" % (dt.now().strftime("%Y%m%d%H%M%S%f"), pid, cid, keys, mouse_distance, mbuttons, wheel, gamepad)
	with open(PATH_ACTIVITIES, "a") as f:
		f.write(text)

class TrayApp:
	""" The main view controller """
	running = True

	def __init__(self):
		self.options = self.load_options()
		# create window class
		wc = WNDCLASS()
		wc.lpszClassName = "PyTracker"
		wc.lpfnWndProc = {
			WM_DESTROY: self._destroy,
			WM_COMMAND: self._command,
			WM_USER + 20: self._notify
		}
		# create window
		self.window = CreateWindow(RegisterClass(wc), "PyTracker", WS_OVERLAPPED | WS_SYSMENU, 0, 0, CW_USEDEFAULT, CW_USEDEFAULT, 0, 0, None, None)
		UpdateWindow(self.window)
		# create menu
		self.menu = CreatePopupMenu()
		item, _ = PackMENUITEMINFO(text="Open activities", wID=MN_OPEN_ACTIVITIES)
		InsertMenuItem(self.menu, 0, 1, item)
		item, _ = PackMENUITEMINFO(text="Private tracking protection", wID=MN_TOGGLE_PRIVATE, fState=MFS_CHECKED if self.private else MFS_UNCHECKED)
		InsertMenuItem(self.menu, 1, 1, item)
		item, _ = PackMENUITEMINFO(text="Exit", wID=MN_EXIT)
		InsertMenuItem(self.menu, 2, 1, item)
		# set state
		self.change(action=NIM_ADD)

	def change(self, state="base", hover_text="PyTracker is active", action=NIM_MODIFY):
		icon_path = abspath(join(path[0], PATH_ICON % state))
		self.icon = LoadImage(None, icon_path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE | LR_DEFAULTSIZE)
		nid = (self.window, 0, NIF_ICON | NIF_MESSAGE | NIF_TIP, WM_USER + 20, self.icon, hover_text)
		Shell_NotifyIcon(action, nid)

	def popup(self, title, msg, sleep_time=0):
		Shell_NotifyIcon(NIM_MODIFY, (self.window, 0, NIF_INFO, WM_USER + 20, self.icon, "Notificación", msg, 200, title))
		if sleep_time:
			sleep(sleep_time)

	def msgbox(self, text, caption="PyTracker"):
		windll.user32.MessageBoxW(0, text, caption, MB_TOPMOST)

	def check(self):
		PumpWaitingMessages()

	def load_options(self):
		global TIME_BETWEEN_READS, TIME_BETWEEN_BEATS, TIME_UNTIL_IDLE, READS_UNTIL_IDLE, READS_UNTIL_IDLE_FULLSCREEN
		if isfile(PATH_OPTIONS):
			config = ConfigParser()
			config.read(PATH_OPTIONS)
			if 'General' in config.sections():
				self.private = config['General'].getboolean('private', True)
			if 'Time' in config.sections():
				TIME_BETWEEN_READS = config['Time'].getfloat("between_reads", TIME_BETWEEN_READS)
				TIME_BETWEEN_BEATS = config['Time'].getfloat("between_beats", TIME_BETWEEN_BEATS)
				TIME_UNTIL_IDLE = config['Time'].getfloat("until_idle", TIME_UNTIL_IDLE)
		else:
			self.private = True
		READS_UNTIL_IDLE = TIME_UNTIL_IDLE / TIME_BETWEEN_READS
		READS_UNTIL_IDLE_FULLSCREEN = READS_UNTIL_IDLE * 1.5

	def save_options(self):
		global TIME_BETWEEN_READS, TIME_BETWEEN_BEATS, TIME_UNTIL_IDLE
		config = ConfigParser()
		config["General"] = {
			"private": self.private
		}
		config["Time"] = {
			"between_reads": TIME_BETWEEN_READS,
			"between_beats": TIME_BETWEEN_BEATS,
			"until_idle": TIME_UNTIL_IDLE
		}
		with open(PATH_OPTIONS, "w") as fp:
			config.write(fp)

	def end(self, save=True):
		if self.running:
			print('Ending TrayApp')
			self.running = False
			DestroyWindow(self.window)
			if save:
				remove(PATH_LOCK)
				self.save_options()
			if _il != None:
				self.running = False
				_il.running = False

	def _notify(self, hwnd, msg, wparam, lparam):
		if lparam == WM_RBUTTONUP:  # right click
			pos = GetCursorPos()
			SetForegroundWindow(self.window)
			TrackPopupMenu(self.menu, TPM_LEFTALIGN, pos[0], pos[1], 0, self.window, None)
			PostMessage(self.window, WM_NULL, 0, 0)
		elif lparam == WM_LBUTTONDBLCLK:  # double click
			self.msgbox(analysis())
		return True

	def _command(self, hwnd, msg, wparam, lparam):
		global _il
		id = LOWORD(wparam)
		if id == MN_EXIT:
			self.end()
		elif id == MN_OPEN_ACTIVITIES:
			Popen("explorer /select,\"%s\"" % PATH_ACTIVITIES)
		elif id == MN_TOGGLE_PRIVATE:
			state = GetMenuState(self.menu, id, MF_BYCOMMAND)
			if state == MFS_CHECKED:
				rc = CheckMenuItem(self.menu, id, MF_BYCOMMAND | MFS_UNCHECKED)
				self.private = False
			elif state == MFS_UNCHECKED:
				rc = CheckMenuItem(self.menu, id, MF_BYCOMMAND | MFS_CHECKED)
				self.private = True

	def _destroy(self, hwnd, msg, wparam, lparam):
		nid = (self.window, 0)
		Shell_NotifyIcon(NIM_DELETE, nid)
		PostQuitMessage(0)