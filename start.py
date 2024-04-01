from os import chdir
from os.path import dirname
from tracker import run

if __name__ == '__main__':
	chdir(dirname(__file__))
	run()