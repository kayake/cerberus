import aiofiles as aiof
import logging
from pathlib import Path
from typing import List
import os

from lib.core.database import SavePayloads

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
            log.debug(f"BOLDString: {path}")
            return [path]

class PreProcessing(ReadWordlists):
    """
    A pre-processing module that installs uvloop and asyncio to prepare the payloads.
    """
    def __init__(self, passwords_path: str, usernames_path: str):
        self.passwords_path = passwords_path
        self.usernames_path = usernames_path
        self.database = SavePayloads()

    def _replace(self, template: str, username: str, password: str) -> str:
        """
        Replace placeholders in the template with the given username and password.
        """
        return template.replace("^USER^", username).replace("^PASS^", password).replace("\n", "")


    def get_save(self, wordlist1: str, wordlist2: str, template: str) -> List[str] | None:
        """
        Read a file and return its contents as a list of strings.
        If the file is not found, return None.
        """
        wordlist = f"{wordlist1}+{wordlist2}".replace("/", "_")
        payloads = self.database.get(template, wordlist)
        if payloads:
            log.warning(f"BOLDPayloads for template __H{template}__h already exists in __H{self.database.save_path}__h")
            y = input("Do you want to use it? [Y/n] ").lower() or "y"
            if y == "n":
                y = input("Do you want delete it and create a new one? [Y/n] ").lower() or "y"
                if y == "y":
                    log.debug(f"BOLDDeleting __H{wordlist}__h")
                    success = self.database.delete(template)
                    if success:
                        log.debug(f"BOLD__H{wordlist}__h deleted.")
                    return None
            return payloads
    
    def save(self, wordlist1: str, wordlist2: str, template: str, payloads: List[str]) -> None:
        """
        Save the generated payloads to a file.
        """
        wordlist = f"{wordlist1}+{wordlist2}".replace("/", "_")
        self.database.set_save(template, wordlist, payloads)
        log.info(f"BOLDPayloads (__H{len(payloads)}__h) were saved in __H{self.database.save_path}__h.")

    async def make(self, template: str) -> List[str]:
        """
        Create a list of payloads by replacing placeholders in the template with all combinations of usernames and passwords.
        """
        save = self.get_save(self.usernames_path, self.passwords_path, template)
        if save:
            log.debug(f"BOLDDone.")
            log.debug(f"BOLDGot __H{len(save)}__h payloads")
            return save
        
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
        
        self.save(self.usernames_path, self.passwords_path, template, tasks)
        return tasks