from lib.core.shell.shell import Cerberus
from lib.core.loggin import log

if __name__ == '__main__':
    try:
        cerberus = Cerberus()
        cerberus.start()
    except (KeyboardInterrupt, EOFError):
        log.error("User aborted")

