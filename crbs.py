from lib.core.shell.shell import Cerberus
from lib.core.loggin import log
from pathlib import Path

""" Veirify if there are requirements folders
    if not, create them to avoid errors """

Path(".cache/logs/").mkdir(parents=True, exist_ok=True)
Path(".cache/saves/").mkdir(parents=True, exist_ok=True)
Path("lib/plugins/").mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    try:
        cerberus = Cerberus()
        cerberus.start()
    except (KeyboardInterrupt, EOFError):
        log.error("User aborted")

