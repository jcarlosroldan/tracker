from pynput.mouse import Listener as MListener
from time import time
from tracker.idle import idle_refresh
from tracker.utils import cfg, error, log

def mouse_start():
	cfg('pressed_mbs', {})
	cfg('scroll', {'amount': None, 'dir': None, 'x': None, 'y': None, 'start': None})
	return MListener(
		on_click=lambda x, y, b, p: mouse_track('click', x, y, button=cfg('mouse')[b.name], pressed=p),
		on_scroll=lambda x, y, sx, sy: mouse_track('scroll', x, y, scroll_x=sx, scroll_y=sy),  # XXX test libinput for mouse touchpad
		on_move=lambda x, y: mouse_track('move', x, y)
	)

def mouse_track(event_type: str, x: int, y: int, button=None, pressed=None, scroll_x=None, scroll_y=None):
	try:
		idle_refresh()
		if event_type == 'click':
			flush_scroll()
			if pressed:
				cfg('pressed_mbs')[button] = (time(), x, y)
			elif button in cfg('pressed_mbs'):
				log('click', cfg('pressed_mbs')[button][0], x, y, cfg('pressed_mbs')[button][1], cfg('pressed_mbs')[button][2], button, '%.8f' % (time() - cfg('pressed_mbs')[button][0]))
				del cfg('pressed_mbs')[button]
		elif event_type == 'scroll':
			if scroll_x == 0:
				scroll_dir = 'D' if scroll_y > 0 else 'U'
			else:
				scroll_dir = 'R' if scroll_x > 0 else 'L'
			if cfg('scroll')['dir'] == scroll_dir:
				cfg('scroll')['amount'] += 1
			else:
				flush_scroll()
				cfg('scroll')['amount'] = 1
				cfg('scroll')['dir'] = scroll_dir
				cfg('scroll')['x'] = x
				cfg('scroll')['y'] = y
				cfg('scroll')['start'] = time()
	except:
		error('TRACK MOUSE')

def flush_scroll():
	if cfg('scroll')['dir'] is not None:
		log('scroll', cfg('scroll')['start'], cfg('scroll')['x'], cfg('scroll')['y'], cfg('scroll')['dir'], cfg('scroll')['amount'], '%.8f' % (time() - cfg('scroll')['start']))
		cfg('scroll')['dir'] = None
		cfg('scroll')['amount'] = 0