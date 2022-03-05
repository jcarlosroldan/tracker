from ctypes import c_char, WinDLL
from os import name as os_name, environ
from pyvda import GetCurrentDesktopNumber
from subprocess import Popen, PIPE
from time import time
from tracker.utils import cfg, log, translate
from win32con import PROCESS_QUERY_INFORMATION, MAX_PATH
from win32gui import GetForegroundWindow, GetWindowText
from win32process import GetWindowThreadProcessId

process_handle = WinDLL('kernel32.dll').OpenProcess
process_filename = WinDLL('Psapi.dll').GetProcessImageFileNameA

REGEX_WINDOW_CLASS = rb'WM_CLASS\(\w*STRING\) = "(.+)", "(.+?)"'
REGEX_WINDOW_NAME = rb'WM_NAME\(\w*STRING\) = "(.+?)"'

def window_start():
	environ['DISPLAY'] = ':0'
	cfg('last_window', [None, None])
	return window_track, cfg('period.window')

def window_track():
	if os_name == 'nt':
		window = get_window_win()
	else:
		window = get_window_unix()
	if window != cfg('last_window'):
		log(
			'window',
			time(),
			translate(window[0]),
			translate(window[1]),
			window[2]
		)
		cfg('last_window', window)

def get_window_win():
	window = ['', '', '']  # [app, activity, desktop]
	fw = GetForegroundWindow()
	pid = GetWindowThreadProcessId(fw)[1]
	hproc = process_handle(PROCESS_QUERY_INFORMATION, False, pid)
	if hproc:
		fname = (c_char * MAX_PATH)()
		if process_filename(hproc, fname, MAX_PATH) > 0:
			window[0] = fname.value.decode('iso-8859-15', errors='replace')  # XXX might depend on system locale
	window[1] = GetWindowText(fw)
	window[2] = GetCurrentDesktopNumber() - 1
	return window

def get_window_unix():
	window = ['', '', '']  # [app, activity, desktop]
	data, _ = Popen('xdotool getactivewindow getwindowpid getwindowname get_desktop', shell=True, stdout=PIPE).communicate()
	data = data.strip().split(b'\n')
	if len(data) == 3:
		try:
			psname, _ = Popen(['ps', '-p', data[0], '-o' 'comm='], stdout=PIPE).communicate()
			window = [psname.strip().decode(), data[1].decode(), data[2].decode()]
		except:
			pass
	return window