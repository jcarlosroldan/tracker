from atexit import register
from os.path import exists
from simpler import cwd, load, save
from time import time
from traceback import format_exc
from typing import Optional, Union

PATH_CONFIG = 'static/config.json'

_cfg = {}
def cfg(path: str, value: object = None) -> Optional[object]:
	''' Given a config path, returns its value or sets it. '''
	if not len(_cfg):
		cwd()
		_cfg.update(load(PATH_CONFIG))
	res = _cfg
	*parents, key = path.split('.')
	[res := res[part] for part in parents]
	if value is None:
		return res[key] if key in res else None
	else:
		res[key] = value

def log(event: str, moment: float = None, *data) -> None:
	''' Logs the given event. '''
	if cfg('log.pending') is None:
		cfg('log.pending', 0)
		cfg('log.events', open(cfg('path.events'), 'a', encoding='utf-8'))
		register(cfg('log.events').close)
	moment = time() if moment is None else moment
	cfg('log.events').write(','.join((cfg('event')[event], '%.3f' % moment, *map(str, data))) + '\n')
	cfg('log.pending', cfg('log.pending') + 1)
	if cfg('log.pending') >= cfg('log.each'):
		cfg('log.events').flush()

def error(context: str) -> None:
	if cfg('log.error') is None:
		cfg('log.error', open(cfg('path.errors'), 'a', encoding='utf-8'))
		register(cfg('log.error').close)
	''' Logs the traceback of an error given a context of how did it happened. '''
	message = '[ERROR AT %s, %.3f] %s\n' % (context, time(), format_exc())
	cfg('log.error').write(message)
	cfg('log.error').flush()

def translate(src: Union[str, int] = None, reverse: bool = False) -> Union[int, str]:
	''' Translates the src entry into a code (or the opposite if `reverse` is set. '''
	if cfg('translate') is None:
		cfg('translate', [
			line.replace('\\n', '\n').replace('\\', '\\\\')
			for line in load(cfg('path.ids')).strip().split('\n')
		] if exists(cfg('path.ids')) else [])
	if reverse:
		return cfg('translate')[src]
	elif src in cfg('translate'):
		return cfg('translate').index(src)  # this is O(n), a trie structure would help
	else:
		code = len(cfg('translate'))
		save(cfg('path.ids'), src.replace('\\', '\\\\').replace('\n', '\\n') + '\n', append=True)
		cfg('translate').append(code)
		return code