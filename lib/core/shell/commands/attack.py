import argparse
import threading
import subprocess
import ua_generator
import requests
from os.path import exists
from lib.core.managers.bruteforce import Data_Attack, Proxy
from lib.core.managers.config import ConfigManager
from lib.core.loggin import log
from pathlib import Path

def test_tor_connection(proxy, protocol, port):
    try:
        requests.get("https://www.torproject.org", proxies={'http': f"{protocol}://127.0.0.1:{port}", 'https': f"{protocol}://127.0.0.1:{port}"})
        log.info("Connected to tor", extra={"bold": True})
    except:
        log.debug("Executing Tor")
        tor = subprocess.Popen(['tor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in iter(tor.stdout.readline, ''):
            if 'Done' in line:
                break
        log.info("Tor is ready", extra={"bold": True})


def group(n, array):
    chunks_size = len(array) // n
    return [array[i * chunks_size:(i + 1) * chunks_size] for i in range(n)]

def read_wordlist(path):
    if not path:
        return log.critical("No argument was provided to load the Wordlist")
    elif not exists(path):
        return log.critical(f"The Wordlist {path} doesn't exists")
    with open(path, 'r') as file:
        lines = file.read().split("\n")
        return lines

def read_header_file(path):
    if not path:
        return None
    elif not exists(path):
        return log.critical(f"The Header {path} doesn't exists")
    json = {}
    with open(path, "r") as file:
        lines = file.read().split("\n")
        for line in lines:
            splitted = line.replace(" ", "").split(": ")
            key = splitted[0]
            value = splitted[1]
            json[key] = value
        return json


class Attack:
    name = "attack"
    aliases = ["run", "brute", "bruteforce", "start", "r"]
    description = "Start the bruteforce attack"
    def __init__(self, this):
        self.cache = this

        self.threads = []

        self.parser = argparse.ArgumentParser(prog="attack", usage='attack [OPTIONS]', description="A bruteforce tool only for HTTPS and HTTP protocols", epilog="attack -u https://example.com/login -ra -l admin -P /usr/share/wordlists/rockyou.txt --tor --D 'username=^USER^&password=^PASS^ -H headers.txt -R 'F=401'")
        g1 = self.parser.add_argument_group(title="Target", description="Need to be provided to start the bruteforce attack.")
        g1.add_argument("--url", "-u", type=str, help="The target to attack. (e.g: -u https://example.com/)", required=True)
        g1.add_argument("--method", "-m", type=str, help="Set a method to attack the service (e.g: GET, POST).", default="POST", required=False)
        g2 = self.parser.add_argument_group(title="Wordlists", description="At least, 2 of these options need to be provided (e.g: attack -l admin -P /usr/share/dict/brazilian).")
        g2.add_argument("--passwords", "-P", type=str, help="Passwords list.", metavar="FILE")
        g2.add_argument("--logins", "-L", type=str, help="Usernames list.", metavar="FILE")
        g2.add_argument("--login", "-l", type=str, help="Username account.", metavar="username")
        g2.add_argument("--password", "-p", type=str, help="Password account.", metavar="password")

        g3 = self.parser.add_argument_group(title="Request", description="'Data' options is required to start any attack. All this options are used to customize the request, like adding your own header.")
        g3.add_argument("--data", "-D", type=str, help="The file of the data (in .txt) or raw to send.", metavar="RAW_OR_FILE", required=True)
        g3.add_argument("--threads", "-T", type=int, help="Define the number of threads you gonna use", metavar="LENGTH", required=False, default=5)
        g3.add_argument("--timeout", "-t", type=int, help="Set a timeout between requests", required=False, metavar="NUMBER", default=0)
        g3.add_argument("--response", "-R", type=str, help="Success or fail response that should return (e.g: -R 'F=403' or -R S=200).\nYou can use status text, or something that returns in a JSON response (e.g: -R 'S=user_id', -R 'S=successfully' or -R 'F={message: 'Fail to log in'})", required=True)
        g3.add_argument("--headers", "-H", type=str, help="The headers file to use.", required=False, metavar="FILE.txt")
        g3.add_argument("--random-agent", '-ra', action="store_true", help="Choose, randomily, an user agent.", required=False)
        g3.add_argument("--tor", action="store_true", default=False, help="Active tor.", required=False)
        g3.add_argument("--proxy", action="store_true", help="Use a single proxy", required=False)
        g3.add_argument("--proxies", action="store_true", help="Use random proxies", required=False)

        g4 = self.parser.add_argument_group(title="Output and Configuration File", description="Set a custom configuration and output files.")
        g4.add_argument("--output", "-o", help="Output file when passwords is found.", type=str, required=False)
        g4.add_argument("--config", "-c", default="config.yaml", help="Configuration file (.yaml)", type=str, metavar="config.yaml", required=False)

        g5 = self.parser.add_argument_group(title="Others")
        g5.add_argument('--ignore', '-I', action="store_true", default=False, required=False, help="Disable checkpoint of your attack.")
    def attack(self, arguments):
        if not Path(arguments.data).exists():
            with open(Path(arguments.data), "r") as file:
                arguments.data = file.read()
        config = ConfigManager(arguments.config)
        headers = read_header_file(arguments.headers) if arguments.headers else {}
        if arguments.random_agent:
            headers['User-Agent'] = ua_generator.generate().text
        tor = ()
        proxy = None
        proxies = []
        if arguments.tor:
            tor_configuration = config.get("tor")
            tor = (tor_configuration['protocol'], 
                   tor_configuration['port'], 
                   tor_configuration['control_port'], 
                   tor_configuration['password']
                )           
        elif arguments.proxy:
            proxy_configuration = config.get('proxy')
            proxy = f"{proxy_configuration['protocol']}://{proxy_configuration['address']}"
        elif arguments.proxies:
            proxies = read_wordlist(config.get('proxies'))

        bruteforce = Data_Attack(url=arguments.url, 
                                 data=arguments.data, 
                                 headers=headers, 
                                 timeout=arguments.timeout, 
                                 response=arguments.response.split("="), 
                                 method=arguments.method, 
                                 tor=tor, 
                                 proxy=proxy, 
                                 proxies=proxies,
                                 resume=not arguments.ignore,
                                 numer_of_threads=arguments.threads
                                )

        print(f"{"-"*30}\nMethod: {arguments.method}\nUrl: {arguments.url}\nBody Payload: {arguments.data}\nHeaders: {arguments.headers}\nTimeout: {arguments.timeout}\nThreads: {arguments.threads}\nResponse: {arguments.response}\nTor: {arguments.tor}\nRandom User-Agent: {arguments.random_agent}\n{"-"*30}")
       
       
        if arguments.passwords and arguments.login:
            passwords = read_wordlist(arguments.passwords)
            passwords_grouped = group(arguments.threads, passwords)

            bruteforce.total = len(passwords)
            for id in range(arguments.threads):
                self.threads.append(threading.Thread(target=bruteforce.bruteforce_password, args=(arguments.login, passwords_grouped, id), daemon=True))

        elif arguments.logins and arguments.password:
            usernames = read_wordlist(arguments.usernames)
            usernames_grouped = group(arguments.threads, usernames)

            bruteforce.total = len(usernames)
            for id in range(arguments.threads):
                self.threads.append(threading.Thread(target=bruteforce.bruteforce_username, args=(usernames_grouped, arguments.password, id), daemon=True)) 
            

        elif arguments.logins and arguments.passwords:
            passwords = read_wordlist(arguments.passwords)
            usernames = read_wordlist(arguments.usernames)
            passwords_grouped = group(arguments.threads, passwords)
            usernames_grouped = group(arguments.threads, usernames)

            bruteforce.total = len(passwords) * len(usernames)

            for id in range(arguments.threads):
                self.threads.append(threading.Thread(target=bruteforce.bruteforce_password_and_username, args=(usernames_grouped, passwords_grouped, id), daemon=True))
        
        else:
            return log.error("Provide at least one wordlist and username/password")
        bruteforce.running = True
        
        try:
            for t in self.threads:
                t.start()

            for t in self.threads:
                t.join()
        except (KeyboardInterrupt, EOFError):
            bruteforce.running = False
            bruteforce.stop()
            for t in self.threads:
                t.join(timeout=1)
        finally:
            self.threads = []
    
    def run(self, arguments):
        if not arguments:
            return self.parser.print_help()
        arguments = self.parser.parse_args(arguments)
        self.attack(arguments=arguments)
