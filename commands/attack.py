import asyncio
from lib.core.http import Attack as HTTPAttack, MultipleAttack, MultipleWordlists

class Attack:
    async def run(self, arguments) -> None: 
        if arguments.mutiple_sites:
            bruteforces = MultipleAttack(
                arguments.config,
                arguments.clusters,
                arguments.proxy,
                arguments.tor,
                arguments.proxies,
                arguments.random_agent,
                arguments.user_agent_list
            )

            asyncio.run(bruteforces.start())
            return True

        bruteforce = HTTPAttack(
            arguments.config, 
            arguments.proxy, 
            arguments.tor, 
            arguments.proxies, 
            arguments.random_agent, 
            arguments.user_agent,
            arguments.user_agent_list
        )
        if isinstance(bruteforce.config.credentials.usernames, list) or isinstance(bruteforce.config.credentials.passwords, list):
            bruteforce_with_mutiple_wordlists = MultipleWordlists(
                arguments.config,
                arguments.clusters,
                arguments.proxy,
                arguments.tor,
                arguments.proxies,
                arguments.random_agent,
                arguments.user_agent_list
            )
            asyncio.run(bruteforce_with_mutiple_wordlists.start())
            return True
        
        return await bruteforce.attack()