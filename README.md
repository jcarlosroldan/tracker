# Tracker

This simple tracker allows you to analyse your activity in the computer, keyboard, mouse, gamepad and much more.

*here it will go a beautiful image of the final result*

## Installation

Installing it is very simple, it will require you to have Python 3 and pip installed.

### Linux

Download this zip and uncompress it in a convenient place, such as `\~/Documents/tracker`. Then open a terminal in that directory, and install the required dependencies.

```
pip3 install -r requirements.txt
```

Then, edit the crontab by typing into a console `crontab -e` and add the following two lines at the end.

```
0,30 * * * * DISPLAY=:0 python3 ~/Documents/tracker/tracker.py
@reboot sleep 60; DISPLAY=:0 python3 ~/Documents/tracker/tracker.py
```

And you are done! Reboot and you will have your tracker running. To see the output just go to [http://localhost:75483/](http://localhost:75483/).

### Windows

Unfortunately, this library is not available for Windows yet. See [pynput #118](https://github.com/moses-palmer/pynput/issues/118) for more details.

### MacOS

This library have not been tested in MacOS yet, but you can help by installing it. How? Now idea, that why we need you!

## Research

If you want to add new features to this tool, or to use the data it gathers for your research, this section provides some insights about the tracking data.

When you run the tool for the first time, a `files` folder is generated. This folder contains all the tracking information that the tool gathers, spread in two files.

The file `events.csv` is the main document, with one line per each event that has been tracked since the beginning of the ages (or the installation). Each line starts with a letter that identifies the type of event, followed by a timestamp from when the event occurred, and some data that changes for each event type:

| log_type     |       |           |          |           |       |         |         |
| ------------ | ----- | --------- | -------- | --------- | ----- | ------- | ------- |
| **B**egin    | start |           |          |           |       |         |         |
| **K**eyboard | start | key_code  | elapsed  |           |       |         |         |
| **S**croll   | start | start_x   | start_y  | direction | lines | elapsed |         |
| **C**lick    | start | start_x   | start_y  | end_x     | end_y | button  | elapsed |
| **W**indow   | start | app       | activity | desktop   |       |         |         |
| **I**dle     | start | is_active |          |           |       |         |         |

Since there is a thread running for each kind of tracker (mouse, keyboard, window...), this lines may not be always sorted by start time.

The file `ids.pk` is a pickle file that contains a list of strings that correspond to app names and activity names. If you are procrastinating in your computer, two event lines may look like this:

```
W,12345678.12345678,4,145,0
W,12345680.12345678,4,160,0
```

Then, If you import the `ids.pk` file you'll see that the string in the position 4 is `"Firefox"`, the position 145 is `"Facebook"`, and 160 is `"Twitter"`.

## Tasks

* Update the web interface so it is not 90's internet style
* Add the analytics
* Add gamepad tracking
* Add device connect/disconnect tracking
* Add IP/SSID tracking