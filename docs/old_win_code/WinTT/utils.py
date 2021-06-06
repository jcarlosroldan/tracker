from atexit import register
from collections import Counter
from configparser import ConfigParser
from ctypes import windll, c_char, WinDLL
from datetime import datetime as dt
from math import sqrt
from os import remove, makedirs, getenv
from os.path import abspath, join, isfile, exists
from pynput import mouse, keyboard
from subprocess import Popen
from sys import path
from threading import Thread
from time import time, sleep
from traceback import format_exc
from win32con import CW_USEDEFAULT, IMAGE_ICON, LR_DEFAULTSIZE, LR_LOADFROMFILE, MAX_PATH, MB_TOPMOST, PROCESS_QUERY_INFORMATION, TPM_LEFTALIGN, WM_COMMAND, WM_DESTROY, WM_LBUTTONDBLCLK, WM_NULL, WM_RBUTTONUP, WM_RBUTTONUP, WM_USER, WS_OVERLAPPED, WS_SYSMENU, MFT_RADIOCHECK, MFS_CHECKED, MFS_UNCHECKED, MF_BYCOMMAND
from win32gui import CheckMenuItem, CreatePopupMenu, CreateWindow, DestroyWindow, GetCursorPos, GetForegroundWindow, GetMenuDefaultItem, GetMenuState, GetWindowText, InsertMenuItem, LoadImage, LOWORD, NIF_ICON, NIF_INFO, NIF_MESSAGE, NIF_TIP, NIM_ADD, NIM_DELETE, NIM_MODIFY, PostMessage, PostQuitMessage, PumpWaitingMessages, RegisterClass, SetForegroundWindow, Shell_NotifyIcon, TrackPopupMenu, UpdateWindow, WNDCLASS
from win32gui_struct import PackMENUITEMINFO
from win32process import GetWindowThreadProcessId

# --- constants ---------------------------------------------------------------

# path flags
BASE = "%s\\WinTT\\" % getenv('APPDATA')
PATH_LOCK = "%s.lock" % BASE
PATH_ACTIVITIES = "%sactivities.txt" % BASE
PATH_IDS = "%sids.txt" % BASE
PATH_OPTIONS = "%soptions.txt" % BASE
PATH_PRIVATE = "res/private.txt"
PATH_ICON = "res/%s.ico"

# time constants
TIME_BETWEEN_READS = 0.2
TIME_BETWEEN_BEATS = 2
TIME_UNTIL_IDLE = 3 * 60
READS_UNTIL_IDLE = None
READS_UNTIL_IDLE_FULLSCREEN = None

# stats values
STATS_TOP_LENGTH = 5

# activity flags
AC_NONE = -1
AC_START_TRACKING = -2
AC_END_TRACKING = -3
AC_IDLE_ON = -4
AC_IDLE_OFF = -5
AC_PRIVATE = -6

# menu ids
MN_OPEN_ACTIVITIES = 1
MN_TOGGLE_PRIVATE = 2
MN_EXIT = 3

# time values
MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY
YEAR = 365.25 * DAY

# --- dictionary mappings -----------------------------------------------------

__ids = None
def text2id(text):
	global __ids
	if __ids == None:
		try:
			with open(PATH_IDS, "r", encoding="utf-8") as f:
				__ids = f.read().strip().split("\n")
		except:
			__ids = []
	if text in __ids:
		pid = __ids.index(text)
	else:
		__ids.append(text)
		with open(PATH_IDS, "a", encoding="utf-8") as f:
			f.write(text + "\n")
		pid = len(__ids) - 1
	return pid

def id2text(id):
	global __ids
	if __ids == None:
		try:
			with open(PATH_IDS, "r", encoding="utf-8") as f:
				__ids = f.read().strip().split("\n")
		except:
			__ids = []
	if id < 0:
		return ["NONE", "START TRACKING", "END TRACKING", "IDLE ON", "IDLE OFF", "PRIVATE"][abs(id) - 1]
	else:
		return __ids[id]