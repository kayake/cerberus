from requests import Session, Request, get
from stem.control import Controller

from src.utils.loggin import log
from re import search
from .loggin import Fore, Style, RESET, BOLD

class Tor:
    def __init__(self, control_port=9051):
        self.port = control_port
        self.controller = None

    def connect(self, password=None):
        try:
            self.controller = Controller.from_port(port=self.port)
            self.controller.authenticate(password=password)
            return log.info("Connected to ControlPort", extra={"bold": True})
        except (ConnectionRefusedError, ConnectionError) as err:
            log.error(f"Error trying to connect to Tor:\n{err}")

    def renew_circuit(self):
        if self.controller and self.controller.is_authenticated():
            try:
                self.controller.signal("NEWNYM")
                log.info("The new circuit was created with successfully", extra={"bold": True})
            except Exception as e:
                log.error(f"Failed to create another circuit:\n{e}")
        else:
            log.warn("It wasn't detected any connection to ControlPort.", extra={"bold": True})
            yn = log.input("Do you want to connect to ControlPort? [Y/n] ") or 'y'
            if 'y' in yn.lower():
                log.debug("Starting to connect to the ControlPort")
                password = log.input("Password (if there isn't password, leave it blank): ")
                self.connect(password=password)
            else:
                pass

    def close(self):
        if self.controller:
            self.controller.close()
            log.debug("The ControlPort Connection was closed", extra={"bold": True})

proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}

def request(method, url, data=None, headers=None):
    session = Session()

    session.proxies.update(proxies)
    req = Request(method=method, url=url, data=data, headers=headers)
    prepped = req.prepare()

    resp = session.send(prepped)
    return resp

def test_ip():
    res = request(method="GET", url="https://check.torproject.org/")
    match = search(r"Your IP address appears to be:\s*<strong>([\d\.]+)</strong>", res.text)
    if match:
        ip = match.group(1)
        log.info(f"You're connected to Tor. Your IP: {BOLD}{Style.BRIGHT}{Fore.MAGENTA}{ip}{RESET}", extra={"bold": True})