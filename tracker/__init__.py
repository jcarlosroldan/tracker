from atexit import register
from setproctitle import setproctitle
from threading import Thread
from time import sleep, time
from tracker.idle import idle_start
from tracker.keyboard import keyboard_start
from tracker.lock import lock_start, lock_start
from tracker.mouse import mouse_start
from tracker.server import server_start
from tracker.utils import cfg, error, log
from tracker.window import window_start

def run():
	try:
		setproctitle(cfg('proctitle'))
		cfg('running', True)
		register(lambda: cfg('running', False))
		threads = (
			server_start(),
			Thread(target=loop, args=idle_start()),
			Thread(target=loop, args=lock_start()),
			keyboard_start(),
			mouse_start()  # XXX add joystick tracking and periodic snapshots
		)
		log('begin')
		# track_window is ran in the main thread due to a Windows 10 bug with running GetWindowText in separate threads
		[t.start() for t in threads]
		loop(*window_start())
		[t.join() for t in threads]
	except:
		error('TRACKER INIT')

def loop(target, throttle=0):
	try:
		while cfg('running'):
			delay = time()
			target()
			delay = time() - delay
			if delay < throttle: sleep(throttle - delay)
	except:
		error(target.__name__.upper())