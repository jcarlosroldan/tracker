from pynput.keyboard import Listener as KBListener
from time import time
from tracker.idle import idle_refresh
from tracker.utils import cfg, error, log

def keyboard_start():
	cfg('pressed_keys', {})
	return KBListener(
		on_press=lambda k: keyboard_track('down', k),
		on_release=lambda k: keyboard_track('up', k)
	)

def keyboard_track(event_type, key):
	try:
		idle_refresh()
		if 'char' in key.__dict__:
			key = str(ord(key.char))
		else:
			key = str(key.value.vk)
		if event_type == 'down':
			cfg('pressed_keys')[key] = time()
		elif key in cfg('pressed_keys'):
			log('keyboard', cfg('pressed_keys')[key], key, '%.8f' % (time() - cfg('pressed_keys')[key]))
			del cfg('pressed_keys')[key]
	except:
		error('TRACK_KEYBOARD')