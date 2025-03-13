from atexit import register
from setproctitle import setproctitle
from threading import Thread
from time import sleep, time
from tracker.idle import idle_start
from tracker.keyboard import keyboard_start
from tracker.lock import lock_start
from tracker.mouse import mouse_start
from tracker.server import server_start
from tracker.utils import cfg, error, log
from tracker.window import window_start
from typing import Callable, Tuple
from webbrowser import open as open_browser

def run() -> None:
	try:
		setproctitle(cfg('proctitle'))
		cfg('running', True)
		register(lambda: cfg('running', False))
		threads = (
			server_start(),
			Thread(target=loop, args=idle_start()),
			Thread(target=loop, args=lock_start()),
			keyboard_start(),
			mouse_start()  # TODO add joystick tracking and periodic snapshots
		)
		log('begin')
		[t.start() for t in threads]
		open_browser('http://localhost:%s' % cfg('server.port'), new=0)
		loop(*window_start())  # GetWindowText requires being in the main thread due to W10 bug
		[t.join() for t in threads]
	except:
		error('TRACKER INIT')

def loop(target: Tuple[Callable, float], throttle: float = 0) -> None:
	try:
		while cfg('running'):
			now = time()
			target()
			sleep(max(0, now + throttle - time()))
	except:
		error(target.__name__.upper())