import logging
from colorama import init
from colorama import Fore, Back, Style
from datetime import datetime
from math import floor
init(autoreset=True)

BOLD = "\033[1m"
RESET = Style.RESET_ALL
THREAD_ID_COLOR = "\033[38;2;255;0;111m"

STATUS_COLORS = {
    "CONNECTION_ERROR": f"{Style.BRIGHT}\033[38;5;202m",
    "2xx": f"{BOLD}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}",
    "3xx": f"{Fore.LIGHTCYAN_EX}",
    "4xx": f"\033[38;5;214m", # orange
    "5xx": f"{BOLD}{Style.BRIGHT}{Fore.LIGHTRED_EX}"
}

def color_status(status_code):
    code = str(floor(status_code / 100)) + "xx"
    return f"{STATUS_COLORS[code]}{status_code}{RESET}"

LEVELS_COLOR = {
    "INFO": f"{Fore.GREEN}",
    "WARNING": f"{Fore.YELLOW}",
    "ERROR": f"{Fore.RED}",
    "CRITICAL": f"{Back.RED}{Fore.WHITE}",
    "DEBUG": f"{Style.BRIGHT}{Fore.BLUE}"
}
TIMESTAMP_STYLE = f"{Style.DIM}{Fore.CYAN}"

class Colorizing(logging.StreamHandler):
    def format(self, record):
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_color = LEVELS_COLOR.get(record.levelname, "")
        bold = getattr(record, "bold", False)
        levelname = f"[{level_color}{BOLD if bold else ""}{record.levelname}{RESET}]"
        return f"{RESET}[{TIMESTAMP_STYLE}{timestamp}{RESET}] {levelname} {record.getMessage()}"

log = logging.getLogger('cerberus')
log.setLevel(logging.DEBUG)

handler = Colorizing()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

def attempt(o, had_success=False, id="MAIN"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if had_success:
        success(o, id=id)
    else:
        colorize = f"[{THREAD_ID_COLOR}{id}{RESET}] ( {o['attempt']} of {o['total']} ) Login: {BOLD}{Style.BRIGHT}{Fore.LIGHTRED_EX}{o['username']}{RESET} - Password: {BOLD}{Style.BRIGHT}{Fore.RED}{o['password']}{RESET} [ {color_status(o["status_code"])} : {BOLD}{Style.BRIGHT}{Fore.LIGHTRED_EX}FAILED{RESET} ]"
        print(f"[{TIMESTAMP_STYLE}{timestamp}{RESET}] [{Style.BRIGHT}{Fore.BLUE}ATTEMPT{RESET}] {colorize}")

def success(o, id):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colorize = f"[{THREAD_ID_COLOR}{id}{RESET}] ( {o['attempt']} of {o['total']} ) Login: {BOLD}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}{o['username']}{RESET} - Password: {BOLD}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}{o['password']}{RESET} [ {color_status(o["status_code"])} : {BOLD}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}SUCCESS{RESET} ]"
    print(f"[{TIMESTAMP_STYLE}{timestamp}{RESET}] [{Style.BRIGHT}{Fore.BLUE}ATTEMPT{RESET}] {colorize}")

def reattempt(o, id):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{TIMESTAMP_STYLE}{timestamp}{RESET}] [{Style.BRIGHT}\033[38;5;214mRE-ATTEMPT{RESET}] [{THREAD_ID_COLOR}{id}{RESET}] ( {o['attempt']} of {o['total']} ) Login - {BOLD}{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}{o['username']}{RESET} - Password {BOLD}{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}{RESET} [ {color_status(o['status_code'])} : {BOLD}{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}WAITING{RESET} ]")

def tor(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{TIMESTAMP_STYLE}{timestamp}{RESET}] [{Style.BRIGHT}{BOLD}{Fore.MAGENTA}TOR{RESET}] {message}")

def input_logging(message):
    return input(f"{BOLD}{message}{RESET}")

log.attempt = attempt
log.tor = tor
log.reattempt = reattempt
log.input = input_logging