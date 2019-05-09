# WinTT
Awesome time tracker for Windows

## Known problems

### Keyboard input scrambling

Listening to keystrokes in Python has a number of problems If we want something cross-platform. If we look at all alternatives:

* **Pynput:** Currently used any other OS, alhough other parts of the app are only supported in Windows. Scrambles accent keystrokes in Windows. See [Issue #118](https://github.com/moses-palmer/pynput/issues/118).
* **Keyboard:** Is not working in Windows due to a ctypes Win32 error. See [Issue #157](https://github.com/boppreh/keyboard/issues/157). Otherwise `keyboard.read_event` (polling) or `keyboard.hook` (notification) would do the thing.
* **PyHook:** It also [scrambles keystrokes](https://sourceforge.net/p/pyhook/bugs/2/). The [docs](https://sourceforge.net/p/pyhook/wiki/PyHook_Tutorial/) are a bit obscure, and the [library is not in pip](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyhook).
* **PyGame:** It is required [to create a Window](https://stackoverflow.com/questions/36876829/pygame-key-listener-for-python-3) to capture keyboard events.
* **Msvcrt:** Only works in console apps, similar to C `getch` function.
* **Curses:** Only able to capture key events [in the console](https://stackoverflow.com/questions/16740385/python-curses-redirection-is-not-supported/33958141#33958141).
* **Termios:** Not available in Windows.

Only these two alternatives haven't been explored yet:

* **PyWin32:** This could be a good choice, since it is being used on many other parts of the interface.
* **GTK, TKinter:** Yet to explore.