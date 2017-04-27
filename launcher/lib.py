import os
import sys
import subprocess

from PyQt5 import QtCore

self = sys.modules[__name__]
self._path = os.path.dirname(__file__)
self._current_task = None

try:
    basestring
except NameError:
    basestring = str


def resource(*path):
    path = os.path.join(self._path, "res", *path)
    return path.replace("\\", "/")


def which(program):
    """Locate `program` in PATH

    Arguments:
        program (str): Name of program, e.g. "python"

    """

    def is_exe(fpath):
        if os.path.isfile(fpath) and os.access(fpath, os.X_OK):
            return True
        return False

    for path in os.environ["PATH"].split(os.pathsep):
        for ext in os.getenv("PATHEXT", "").split(os.pathsep):
            fname = program + ext.lower()
            abspath = os.path.join(path.strip('"'), fname)

            if is_exe(abspath):
                return abspath

    return None


def which_app(app):
    """Locate `app` in PATH

    Arguments:
        app (str): Name of app, e.g. "python"

    """

    for path in os.environ["PATH"].split(os.pathsep):
        fname = app + ".yml"
        abspath = os.path.join(path.strip('"'), fname)

        if os.path.isfile(abspath):
            return abspath

    return None


def dict_format(original, **kwargs):
    """Recursively format the values in *original* with *kwargs*.

    Example:
        >>> sample = {"key": "{value}", "sub-dict": {"sub-key": "sub-{value}"}}
        >>> dict_format(sample, value="Bob") == \
            {'key': 'Bob', 'sub-dict': {'sub-key': 'sub-Bob'}}
        True

    """

    new_dict = dict()
    new_list = list()

    if isinstance(original, dict):
        for key, value in original.items():
            if isinstance(value, dict):
                new_dict[key.format(**kwargs)] = dict_format(value, **kwargs)
            elif isinstance(value, list):
                new_dict[key.format(**kwargs)] = dict_format(value, **kwargs)
            elif isinstance(value, basestring):
                new_dict[key.format(**kwargs)] = value.format(**kwargs)
            else:
                new_dict[key.format(**kwargs)] = value

        return new_dict

    else:
        assert isinstance(original, list)
        for value in original:
            if isinstance(value, dict):
                new_list.append(dict_format(value, **kwargs))
            elif isinstance(value, list):
                new_list.append(dict_format(value, **kwargs))
            elif isinstance(value, basestring):
                new_list.append(value.format(**kwargs))
            else:
                new_list.append(value)

        return new_list


def schedule(task, delay=10):
    """Delay execution of `task` by `delay` milliseconds

    As opposed to a plain `QTimer.singleShot`, this will also
    ensure that only one task is ever queued at any one time.

    """

    try:
        self._current_task.stop()
    except AttributeError:
        # No task currently running
        pass

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(task)
    timer.start(delay)

    self._current_task = timer


def launch(executable, args=None, environment=None):
    """Launch a new subprocess of `args`

    Arguments:
        executable (str): Relative or absolute path to executable
        args (list): Command passed to `subprocess.Popen`
        environment (dict, optional): Custom environment passed
            to Popen instance.

    Returns:
        Popen instance of newly spawned process

    Exceptions:
        OSError on internal error
        ValueError on `executable` not found

    """

    CREATE_NO_WINDOW = 0x08000000
    IS_WIN32 = sys.platform == "win32"

    abspath = executable

    kwargs = dict(
        args=[abspath] + args or list(),
        env=environment or os.environ,

        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,

        # Output `str` through stdout on Python 2 and 3
        universal_newlines=True,

        shell=True
    )

    if IS_WIN32:
        kwargs["creationflags"] = CREATE_NO_WINDOW

    popen = subprocess.Popen(**kwargs)

    return popen


def stream(stream):
    for line in iter(stream.readline, ""):
        yield line
