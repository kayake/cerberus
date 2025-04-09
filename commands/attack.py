from lib.core.http import Attack as HTTPAttack, MultipleWordlists
from lib.core import ReadYAMLFile

import logging

log = logging.getLogger(__name__)

class Attack:
    async def run(self, arguments) -> None:
        config = ReadYAMLFile(arguments.config or "configs/attack.yaml")
        if not config:
            log.error(f"Invalid configuration file {config.file_path}")
            return None

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
                arguments.proxy,
                arguments.tor,
                arguments.proxies,
                arguments.random_agent,
                arguments.user_agent_list
            )
            return await bruteforce_with_mutiple_wordlists.start()

        bruteforce = HTTPAttack(
            config, 
            arguments.proxy, 
            arguments.tor, 
            arguments.proxies, 
            arguments.random_agent, 
            arguments.user_agent,
            arguments.user_agent_list
        )
        
        return await bruteforce.attack()