import aiofiles as aiof
import logging
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from typing import List

log = logging.getLogger(__name__)

class ReadWordlists:
    """
    Class to read all words from the wordlists directory.
    """
    
    async def read(self, path: str) -> List[str]:
        """
        Asynchronously read lines from a file and return them as a list of strings.
        If the file is not found, return the path as a single-element list.
        """
        if not path:
            return log.critical("No file/string was provided")
        try:
            async with aiof.open(path, "r") as file:
                log.debug(f"Starting to read __H{file.name}__h")
                return await file.readlines()
        except FileNotFoundError:
            log.debug(f"BOLDThe argument __H{path}__h wasn't found, so I'll consider it a string.")
            return [path]

class PreProcessing(ReadWordlists):
    """
    A pre-processing module that installs uvloop and asyncio to prepare the payloads.
    """
    def __init__(self, passwords_path: str, usernames_path: str):
        self.passwords_path = passwords_path
        self.usernames_path = usernames_path

    def _replace(self, template: str, username: str, password: str) -> str:
        """
        Replace placeholders in the template with the given username and password.
        """
        return template.replace("^USER^", username).replace("^PASS^", password).replace("\n", "")
    
    async def make(self, template: str) -> List[str]:
        """
        Create a list of payloads by replacing placeholders in the template with all combinations of usernames and passwords.
        """
        usernames = await self.read(self.usernames_path)
        log.debug(f"BOLDDone.")
        passwords = await self.read(self.passwords_path)
        log.debug(f"BOLDDone.")
        log.debug(f"BOLDGot usernames ({len(usernames)}) and passwords ({len(passwords)})")
        tasks = [
            self._replace(template, username, password)
            for username in usernames
            for password in passwords
        ]
        
        log.debug("BOLDTasks created with success.")
        return tasks