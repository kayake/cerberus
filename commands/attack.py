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

        if isinstance(config.credentials.usernames, list) or isinstance(config.credentials.passwords, list):
            log.info("Using multiple wordlists")
            if len(config.credentials.usernames) > 10 or len(config.credentials.passwords) > 10:
                log.warning("BOLDYou are using a high number of wordlists, it may overload your CPU. (max recommended is 10)")
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