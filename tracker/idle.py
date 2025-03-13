from time import time
from tracker.utils import cfg, log

def idle_start():
	cfg('idle', False)
	idle_refresh()
	return idle_track, cfg('period.idle')

def idle_refresh():
	cfg('last_input_time', time())

def idle_track():
	is_idle = time() - cfg('last_input_time') > cfg('period.idle_after')
	if is_idle and not cfg('idle'):
		log('idle', cfg('last_input_time'), 1)
		cfg('idle', True)
	elif not is_idle and cfg('idle'):
		log('idle', cfg('last_input_time'), 0)
		cfg('idle', False)