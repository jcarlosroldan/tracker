from threading import Thread
from pynput.mouse import Listener as MListener, Controller as MController
from pynput.keyboard import Listener as KListener, Controller as KController, Key
from time import sleep, time

TRIGGER = Key.caps_lock
TRIGGER_TIMES = 2
TRIGGER_THRESHOLD = .25

mc = MController()
kc = KController()

_trigger = {'last': 0, 'times': 0}
_state = 0  # 0 = wait, 1 = record, 2 = play
_record = None
_turbo = False
def event(ev_type, args):  # ev_type: 0 = press, 1 = release, 2 = move, 3 = click, 4 = scroll
	global _trigger, _state, _record, _turbo
	# check state cycling
	if ev_type == 1 and args[0] == TRIGGER:
		_turbo = False
		now = time()
		if now - _trigger['last'] > TRIGGER_THRESHOLD:
			_trigger = {'last': now, 'times': 1}
		else:
			_trigger['last'] = now
			_trigger['times'] += 1
		if _trigger['times'] == TRIGGER_TIMES:
			_trigger['last'] = 0
			_state = (_state + 1) % 3
			if _state == 1:
				_record = {'start': time(), 'actions': [(0, 2, *mc.position)]}
				return
			if _state == 2:
				Thread(target=play).start()
	if ev_type == 0 and args[0] == TRIGGER and _state == 2:
		_turbo = True
	# store key press
	if _state == 1:
		_record['actions'].append(((time() - _record['start']) / 5, ev_type, *args))

def play():
	# ignore the shortcut noise from the recorded actions
	remaining_press = TRIGGER_TIMES
	remaining_release = TRIGGER_TIMES - 1
	for a in range(len(_record['actions']) - 1, -1, -1):
		if _record['actions'][a][1] == 0 and _record['actions'][a][2] == TRIGGER and remaining_press:
			_record['actions'].pop(a)
			remaining_press -= 1
		elif _record['actions'][a][1] == 1 and _record['actions'][a][2] == TRIGGER and remaining_release:
			_record['actions'].pop(a)
			remaining_release -= 1
	# replay in loop the record
	while _state == 2:
		start = time()
		for a, action in enumerate(_record['actions']):
			if _state != 2: break
			now = time() - start
			if now < action[0]:
				sleep(.01 if _turbo else action[0] - now)
			if action[1] == 0:
				kc.press(action[2])
			elif action[1] == 1:
				kc.release(action[2])
			elif action[1] == 2:
				mc.position = action[2:]
			elif action[1] == 3:
				mc.position = action[2:4]
				if action[5]:
					mc.press(action[4])
				else:
					mc.release(action[4])
					mc.release(action[4])
			elif action[1] == 4:
				mc.position = action[2:4]
				mc.scroll(*action[4:])
	# release all mouse and keyboard buttons pressed
	release = set(
		action[2]
		for a, action in enumerate(_record['actions'])
		if action[1] == 0
	)
	[kc.release(k) for k in release]
	release = set(
		action[4]
		for a, action in enumerate(_record['actions'])
		if action[1] == 3 and action[5]
	)
	[mc.release(k) for k in release]


kl = KListener(on_press=lambda *k: event(0, k), on_release=lambda *k: event(1, k))
ml = MListener(on_move=lambda *k: event(2, k), on_click=lambda *k: event(3, k), on_scroll=lambda *k: event(4, k))
kl.start()
ml.start()
kl.join()
ml.join()