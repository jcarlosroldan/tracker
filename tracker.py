# --- pre-import singleton check ----------------------------------------------

from time import time, sleep
from os import makedirs, environ
from os.path import exists, dirname

PATH_BASE = dirname(__file__) + '/files/%s'
PATH_LOCK = PATH_BASE % '.lock'

UPDATE_LOCK_EACH = 5

makedirs(dirname(PATH_LOCK), exist_ok=True)

if exists(PATH_LOCK):
	with open(PATH_LOCK, 'r') as fp:
		time_since_beat = time() - int(fp.read())
		if time_since_beat <= UPDATE_LOCK_EACH * 2 + 1:
			exit()

# --- imports and parameters --------------------------------------------------

from atexit import register
from collections import defaultdict as ddict
from flask import Flask, render_template, request, send_from_directory
from json import dumps
from os import remove
from pickle import load as pload, dump as pdump
from pyglet.window.key import symbol_string
from pynput.keyboard import Listener as KBListener
from pynput.mouse import Listener as MListener
from re import search, match
from setproctitle import setproctitle
from subprocess import Popen, PIPE
from sys import stderr
from threading import Thread
from traceback import format_exc

PATH_EVENTS = PATH_BASE % 'events.csv'
PATH_IDS = PATH_BASE % 'ids.pk'
PATH_TEMPLATES = (PATH_BASE % '').replace('files', 'templates')
PATH_ERRORS = PATH_BASE % 'errors.txt'

REGEX_WINDOW_CLASS = rb'WM_CLASS\(\w*STRING\) = "(.+)", "(.+?)"'
REGEX_WINDOW_NAME = rb'WM_NAME\(\w*STRING\) = "(.+?)"'

EVENTS = {'begin': 'B', 'keyboard': 'K', 'scroll': 'S', 'click': 'C', 'window': 'W', 'idle': 'I'}

FLUSH_LOG_EACH = 30
TRACK_WINDOW_EACH = .25
TRACK_IDLE_EACH = 1
TIME_UNTIL_IDLE = 30

APP = Flask(__name__, template_folder=PATH_TEMPLATES)
PUBLIC_EXTENSIONS = ('.png', '.ico', '.css', '.js', '.eot', '.otf', '.svg', '.ttf', '.woff', '.woff2', '.txt', '.csv')

# --- core classes ------------------------------------------------------------

class Tracker:
	def __init__(self, port=7548):
		environ['DISPLAY'] = ':0'
		setproctitle('tracker')
		self.init_log()
		try:
			self.running = False
			self.translator = StringTranslator()
			self.pressed_keys = {}
			self.pressed_mbs = {}
			self.scroll = {'amount': None, 'dir': None, 'x': None, 'y': None, 'start': None}
			self.last_window = [None, None]
			self.idle = False
			self.last_input_time = time()
			Thread(target=APP.run, kwargs={'port': port}).start()
			register(self.close)
		except:
			self.error('TRACKER INIT')

	def close(self):
		self.running = False
		self.log_file.close()
		self.error_file.close()
		APP.close()
		remove(PATH_LOCK)

	def run(self):

		def loop_run(function, throttle=0):
			try:
				while self.running:
					delay = time()
					function()
					delay = time() - delay
					if delay < throttle: sleep(throttle - delay)
			except:
				self.error(function.__name__.upper())

		threads = [
			Thread(target=loop_run, args=(self.track_window, TRACK_WINDOW_EACH)),
			Thread(target=loop_run, args=(self.track_idle, TRACK_IDLE_EACH)),
			Thread(target=loop_run, args=(self.update_lock, UPDATE_LOCK_EACH)),
			KBListener(
				on_press=lambda k: self.track_keyboard('down', k),
				on_release=lambda k: self.track_keyboard('up', k)
			),
			MListener(
				on_click=lambda x, y, b, p: self.track_mouse('click', x, y, button=b.value, pressed=p),
				on_scroll=lambda x, y, sx, sy: self.track_mouse('scroll', x, y, scroll_x=sx, scroll_y=sy),
				on_move=lambda x, y: self.track_mouse('move', x, y)
			)
		]
		self.running = True
		[t.start() for t in threads]
		[t.join() for t in threads]

	def init_log(self):
		self.log_file = open(PATH_EVENTS, 'a', encoding='utf-8')
		self.error_file = open(PATH_ERRORS, 'a', encoding='utf-8')
		self.log_writes = 0
		self.log('begin', time())

	def log(self, event, time, *data):
		msg = '%s,%.8f,%s\n' % (EVENTS[event], time, ','.join(map(str, data)))
		self.log_file.write(msg)
		self.log_writes += 1
		if self.log_writes >= FLUSH_LOG_EACH:
			self.flush_log()

	def flush_log(self):
		self.log_file.flush()
		self.log_writes = 0

	def error(self, context):
		message = '[ERROR AT %s, %s] %s\n' % (context, time(), format_exc())
		self.error_file.write(message)
		self.error_file.flush()

	def track_keyboard(self, event_type, key):
		self.last_input_time = time()
		try:
			key = str(ord(key.char))
		except:
			try:
				key = str(key.value.vk)
			except:
				key = str(key.vk)
		if event_type == 'down':
			self.pressed_keys[key] = time()
		elif key in self.pressed_keys:
			self.log('keyboard', self.pressed_keys[key], key, '%.8f' % (time() - self.pressed_keys[key]))
			del self.pressed_keys[key]

	def track_mouse(self, event_type, x, y, button=None, pressed=None, scroll_x=None, scroll_y=None):
		self.last_input_time = time()
		if event_type == 'click':
			self.flush_scroll()
			if pressed:
				self.pressed_mbs[button] = (time(), x, y)
			elif button in self.pressed_mbs:
				self.log('click', self.pressed_mbs[button][0], x, y, self.pressed_mbs[button][1], self.pressed_mbs[button][2], button, '%.8f' % (time() - self.pressed_mbs[button][0]))
				del self.pressed_mbs[button]
		elif event_type == 'scroll':
			if scroll_x == 0:
				scroll_dir = 'D' if scroll_y > 0 else 'U'
			else:
				scroll_dir = 'R' if scroll_x > 0 else 'L'
			if self.scroll['dir'] == scroll_dir:
				self.scroll['amount'] += 1
			else:
				self.flush_scroll()
				self.scroll['amount'] = 1
				self.scroll['dir'] = scroll_dir
				self.scroll['x'] = x
				self.scroll['y'] = y
				self.scroll['start'] = time()

	def flush_scroll(self):
		if self.scroll['dir'] != None:
			self.log('scroll', self.scroll['start'], self.scroll['x'], self.scroll['y'], self.scroll['dir'], self.scroll['amount'], '%.8f' % (time() - self.scroll['start']))
			self.scroll['dir'] = None
			self.scroll['amount'] = 0

	def track_window(self):
		window = ['', '', '']
		# find the active window id
		data, _ = Popen('xdotool getactivewindow getwindowpid getwindowname get_desktop', shell=True, stdout=PIPE).communicate()
		data = data.strip().split(b'\n')
		if len(data) == 3:
			try:
				psname, _ = Popen(['ps', '-p', data[0], '-o' 'comm='], stdout=PIPE).communicate()
				window = [psname.strip().decode(), data[1].decode(), data[2].decode()]
			except:
				pass
		if window != self.last_window:
			self.log(
				'window',
				time(),
				self.translator.get_id(window[0]),
				self.translator.get_id(window[1]),
				window[2]
			)
			self.flush_log()
			self.last_window = window

	def track_idle(self):
		idle = time() - self.last_input_time > TIME_UNTIL_IDLE
		if idle and not self.idle:
			self.log('idle', self.last_input_time, 1)
			self.idle = True
		elif not idle and self.idle:
			self.log('idle', self.last_input_time, 0)
			self.idle = False

	def update_lock(self):
		with open(PATH_LOCK, 'w') as fp:
			fp.write(str(int(time())))

class StringTranslator:
	def __init__(self):
		if exists(PATH_IDS):
			with open(PATH_IDS, 'rb') as fp:
				self.word_list = pload(fp)
		else:
			self.word_list = []
		register(self.save)

	def save(self):
		with open(PATH_IDS, 'wb') as fp:
			pdump(self.word_list, fp)

	def get_id(self, text):
		try:
			return self.word_list.index(text)
		except:
			self.word_list.append(text)
			self.save()
			return len(self.word_list) - 1

	def get_text(self, _id):
		if 0 >= len(self.word_list) > _id:
			return self.word_list[_id]

# --- server controllers ------------------------------------------------------

@APP.before_request
def security_check():
	loc = request.path
	if any(loc.endswith(ext) for ext in PUBLIC_EXTENSIONS):
		return send_from_directory(PATH_BASE % '', loc.lstrip('/'))

@APP.route('/')
def home():
	return render_template('index.html')

# --- server methods ----------------------------------------------------------

_human_date_measures = (
	('year', 365 * 24 * 3600),
	('month', 30 * 24 * 3600),
	('week', 7 * 24 * 3600),
	('day', 24 * 3600),
	('hour', 3600),
	('minute', 60),
	('second', 1)
)
def human_date(date):
	''' Return a date the a human-friendly format "1 month ago". '''
	res = dt.strptime(date, '%Y-%m-%d, %H:%M:%S')
	diff = (dt.now() - res).total_seconds()
	for name, amount in _human_date_measures:
		if diff > amount:
			diff = diff // amount
			return '%d %s%s ago' % (diff, name, 's' if diff > 1 else '')

APP.jinja_env.filters['json_pretty'] = lambda t: dumps(t, ensure_ascii=False, indent=4, separators=(',', ': '), default=lambda o: '<not serializable>')
APP.jinja_env.filters['json_min'] = lambda t: dumps(t, ensure_ascii=False, separators=(',', ':'), default=lambda o: str(o))
APP.jinja_env.filters['reverse_dict'] = lambda d: {v: k for k, v in d.items()}
APP.jinja_env.filters['percent'] = lambda n: '%.2f%%' % (100 * n)
APP.jinja_env.filters['comma_separated'] = lambda n: '{:,d}'.format(n)
APP.jinja_env.filters['str_list'] = lambda n: ', '.join(n)
APP.jinja_env.filters['str_list_code'] = lambda n: ', '.join(['<code class="text-primary">%s</code>' % e for e in n])
APP.jinja_env.filters['ucfirst'] = lambda t: t[0].upper() + t[1:]
APP.jinja_env.filters['single_quote_escape'] = lambda t: t.replace('\\', '\\\\').replace('\'', '\\\'')
APP.jinja_env.filters['human_date'] = human_date
APP.jinja_env.filters['xpath_min'] = lambda t: sub(r'\[(\d+)\]', r'<sub>\1</sub>', t.split('/body[1]/')[1])
APP.jinja_env.globals.update(enumerate=enumerate, zip=zip, len=len, reversed=reversed, list=list)

# --- entrypoint --------------------------------------------------------------

if __name__ == '__main__':
	t = Tracker()
	try:
		t.run()
	except:
		t.error('TRACKER RUN')