from atexit import register
from datetime import datetime as dt
from flask import Flask, render_template, request, send_from_directory, jsonify
from json import dumps
from re import sub
from sys import stderr
from threading import Thread
from traceback import format_exc
from tracker.utils import cfg

APP = Flask(__name__, template_folder=cfg('path.templates'))

def server_start():
	register(lambda: request.environ.get('werkzeug.server.shutdown')())  # this is how Flask is closed
	return Thread(target=APP.run, kwargs={
		'port': cfg('server.port'),
		'host': '127.0.0.1' if cfg('server.local') else '0.0.0.0'
	})

@APP.before_request
def security_check():
	loc = request.path
	if any(loc.endswith(ext) for ext in cfg('extensions')):
		return send_from_directory(cfg('path.static'), loc.lstrip('/'))

@APP.route('/')
def home():
	return render_template('base.html')

@APP.route('/api/<method>.json')
def api(method):
	starts = {}
	try:
		with open(cfg('path.events'), 'r', encoding='utf-8') as fp:
			for line in fp:
				if line.startswith('B'):
					# session-starts
					stamp = dt.fromtimestamp(float(line[2:21]))
					key = (stamp.weekday(), stamp.hour)
					if key in starts:
						starts[key] += 1
					else:
						starts[key] = 1
					# session-lengths
					key = (stamp.weekday(), stamp.hour)
					if key in starts:
						starts[key] += 1
					else:
						starts[key] = 1
	except:
		print(format_exc(), file=stderr)
	res = {'error': 'Not existing method'}
	if method == 'session-starts':
		res = [[w, h, v] for (w, h), v in starts.items()]
	return jsonify(res)

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