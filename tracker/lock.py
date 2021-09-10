from atexit import register
from os import makedirs, remove
from os.path import exists, dirname
from simpler import load, save
from time import time
from tracker.utils import cfg

def lock_start():
	makedirs(dirname(cfg('path.lock')), exist_ok=True)
	if exists(cfg('path.lock')):
		try:
			time_since_beat = time() - float(load(cfg('path.lock')))
			if time_since_beat <= cfg('period.lock') * 2 + 1:
				exit()
		except:
			pass
	register(lambda: remove(cfg('path.lock')))
	return lock_track, cfg('period.lock')

def lock_track():
	save(cfg('path.lock'), str(time()))