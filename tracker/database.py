from typing import Union
from simpler import load, save
from sqlite3 import connect
from tracker.utils import cfg

def init_db():
	conn = connect(cfg('path.database'))
	conn.executescript(load(cfg('path.schema')))
	cfg('database', conn)
	mappings = [r[0] for r in conn.execute('SELECT value FROM mapping ORDER BY id').fetchall()]
	cfg('mappings', mappings)
	cfg('mappings_reverse', {v: k for k, v in enumerate(mappings)})

def translate(src: Union[str, int] = None, reverse: bool = False) -> Union[int, str]:
	''' Translates the src entry into a code, or the opposite if `reverse` is set. '''
	if isinstance(src, int):
		return cfg('mappings')[src]
	else:
		try:
			return cfg('mappings_reverse')[src]
		except ValueError:
			cfg('database').execute('INSERT INTO mapping (value) VALUES (?)', (src,))
	if reverse:
		return cfg('translate')[src]
	else:
		src = src.replace('\n', ' ')
		try:
			return cfg('translate').index(src)  # this is O(n), a trie structure would help
		except ValueError:
			code = len(cfg('translate'))  # this operation should be sequential with the next to avoid concurrency issues
			cfg('translate').append(src)
			save(cfg('path.ids'), src + '\n', append=True)
			return code