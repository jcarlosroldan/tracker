from utils import *

# easy time
def et(secs):
	if secs < MINUTE: return "%.2fs" % secs
	if secs < HOUR: return "%.2fm" % (secs / MINUTE)
	if secs < DAY: return "%.2fh" % (secs / HOUR)
	if secs < WEEK: return "%.2fd" % (secs / DAY)
	if secs < MONTH: return "%.2fmo" % (secs / WEEK)
	if secs < YEAR: return "%.2fy" % (secs / MONTH)
	return "%.2fm" % (secs / YEAR)

# easy process
__ep_mem = {}
def ep(process):
	if process in __ep_mem: return __ep_mem[process]
	res = process.rsplit("\\", 1)[-1].split(".")[0]
	res = res[0].upper() + res[1:].replace("_", " ")
	__ep_mem[process] = res
	return res

# easy task
__etk_trailing = ["•", " ", "*"]
def etk(task):
	if " - " in task:
		res = task.rsplit(" - ", 1)[0]
	else:
		res = task
	while len(res) and res[-1] in __etk_trailing: res = res[:-1]
	return res.replace("\\", "/")

def top(collection, order_by, filter_function=None, group_by=None, score_display=None):
	if filter != None: collection = filter(filter_function, collection)
	if group_by == None:
		collection = map(lambda a: ("%s - %s" % (a[2], a[3]) if len(a[3]) else a[2], order_by(a)), collection)
	else:
		collection = [(group_by(c), order_by(c)) for c in collection]
	col = {}
	for c in collection:
		k = c[0]
		if k not in col: col[k] = 0
		col[k] += c[1]
	ntop = Counter(col).most_common(STATS_TOP_LENGTH)
	if score_display:
		ntop = [(k, score_display(v)) for k, v in ntop]
	res = "\n".join("\t%s. %s: %s" % (n + 1, elem[0], elem[1]) for n, elem in enumerate(ntop))
	return res


def load_activities():
	with open(PATH_ACTIVITIES, "r") as fp:
		activities = [list(map(int, line.split("\t"))) for line in fp.read().split("\n")[:-1]]
	with open(PATH_IDS, "r", encoding="utf-8") as fp:
		ids = fp.read().split("\n")
	for n in range(len(activities)):
		start = dt.strptime(str(activities[n][0]), "%Y%m%d%H%M%S%f")
		process = ep(id2text(int(activities[n][1])))
		task = etk(id2text(int(activities[n][2])))
		activities[n] = [start, 0, process, task] + activities[n][3:]
	for n, act in enumerate(activities[:-1]):
		activities[n][1] = (activities[n + 1][0] - act[0]).total_seconds()
	return activities

def analysis():
	acts = load_activities()
	acts = [act for act in acts if act[2] not in ["END TRACKING", "IDLE OFF"]]
	res = analysis_basic(acts) + "\n"
	res += analysis_idle(acts) + "\n"
	res += analysis_private(acts) + "\n"
	res += analysis_startup(acts) + "\n"
	acts = [act for act in acts if act[3] != "NONE"]
	res += analysis_tops(acts) + "\n"
	res += analysis_classifications(acts)
	return res

def analysis_basic(acts):
	res = "BASIC ANALYSIS:\n"
	ps = len(set(a[2] for a in acts))
	cs = len(set(a[2] for a in acts))
	res += "%s activities tracked (%s distinct ones)\n" % (len(acts), cs)
	res += "%s distinct processes\n" % ps
	res += "%s tracked\n" % et(sum(a[1] for a in acts))
	return res

def analysis_idle(acts):
	res = "IDLENESS ANALYSIS:\n"
	idle = 0
	not_idle = 0
	idle_t = 0
	not_idle_t = 0
	for act in acts:
		if act[2] == "IDLE ON":
			idle += 1
			idle_t += act[1]
		else:
			not_idle += 1
			not_idle_t += act[1]
	res += "%.2f%% of idle time\n" % (100 * idle_t / (idle_t + not_idle_t))
	if idle > 0:
		res += "Average %s per idle lapse\n" % et(idle_t / idle)
	else:
		res += "Not idle activity\n"
	res += "Average %s per active lapse\n" % et(not_idle_t / not_idle)
	res += "Longest idle times: %s\n" % "top"
	res += "Your most idler activities: %s (%s), %s (%s), %s (%s).\n"  # sum of idles within no process change / total_time(process)
	return res

def analysis_private(acts):
	return ""

def analysis_startup(acts):
	res = ""

	start_tracking = [n for n, act in enumerate(acts) if act[2] == "START TRACKING"]

	res += "Your most frequent activities on startup:\n%s\n" % "top"  # 5 next to a FLAG_START_TRACKING
	res += "Your most frequent activities before shutdown:\n%s\n" % "top"  # 5 previous to a FLAG_START_TRACKING
	return res

def analysis_tops(acts):
	res = "TOPS ANALYSIS:\n"

	ntop = top(acts, lambda x: x[1], group_by=lambda x: x[2], score_display=et)
	res += "Processes where more time was elapsed:\n%s\n" % ntop

	ntop = top(acts, lambda x: x[1], group_by=lambda x: x[3], filter_function=lambda x: len(x[3]), score_display=et)
	res += "Activities where more time was elapsed:\n%s\n" % ntop

	ntop = top(acts, lambda x: 1, group_by=lambda x: x[2], score_display=int)
	res += "Processes with more distinct activities:\n%s\n" % ntop

	return res

def analysis_classifications(acts):
	res = "CLASSIFICATIONS:\n"
	res += "Mainly brosed pages:\n%s\n" % "top"  # time of pages
	res += "Social media daily usage: %sh\n"
	res += "Main social media:\n%s\n" % "top"
	return res
	# images
	# line with main activity each 10 seconds in a color; a line per day analyzed (white = idle or right before/after started tracking)
	# average time spent per hour of the day

def analysis_correlations(acts, ps, tks, tacts):
	# analyse correlations: processes that always precedes to another one, or processes that are always after one
	pass

if __name__ == "__main__":
	print(analysis())