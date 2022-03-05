from simpler import load
from sqlite3 import connect
from tracker.utils import cfg
from typing import Union

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