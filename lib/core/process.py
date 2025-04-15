import aiofiles as aiof
import logging
from pathlib import Path
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
            log.debug(f"BOLDString: {path}")
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


    async def get_save(self, wordlist1: str, wordlist2: str, template: str) -> List[str] | None:
        """
        Read a file and return its contents as a list of strings.
        If the file is not found, return None.
        """
        wordlist = f"{wordlist1}+{wordlist2}".replace("/", "_")
        path = Path().cwd() / f".cache/saves/{wordlist}/{template}"
        try:
            async with aiof.open(path, "r") as file:
                log.warning(f"BOLDTemplate already exists in __H{path}__h")
                y = input("Do you want to use it? [Y/n] ").lower() or "y"
                if y == "n":
                    y = input("Do you want delete it and create a new one? [Y/n] ").lower() or "y"
                    if y == "y":
                        log.debug(f"BOLDDeleting __H{path}__h")
                        await aiof.os.remove(path)
                        log.debug(f"BOLD__H{path}__h deleted.")
                        return None
                return await file.readlines()
        except FileNotFoundError:
            Path(path.parent).mkdir(parents=True, exist_ok=True)
            log.debug(f"BOLDCreating __H{path}__h")
            async with aiof.open(path, "w") as file:
                log.debug(f"BOLD__H{path}__h created.")
                return None
        except IsADirectoryError:
            log.debug(f"BOLDThe argument __H{path}__h is a directory, not a file.")
            return 3
        except PermissionError:
            log.debug(f"BOLDPermission denied to access __H{path}__h")
            return 3
        except Exception as e:
            log.debug(f"BOLDAn unexpected error occurred: {e}")
            return 3
        finally:
            log.debug(f"BOLD__H{path}__h closed.")
    
    async def save(self, wordlist1: str, wordlist2: str, template: str, payloads: List[str]) -> None:
        """
        Save the generated payloads to a file.
        """
        wordlist = f"{wordlist1}+{wordlist2}".replace("/", "_")
        path = Path().cwd() / f".cache/saves/{wordlist}/{template}"
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        log.debug(f"BOLDCSaving to __H{path}__h")
        async with aiof.open(path, "w") as file:
            await file.writelines(payloads)
            log.info(f"BOLDPayloads (__H{len(payloads)}__h) were saved in __H{path}__h.")

    async def make(self, template: str) -> List[str]:
        """
        Create a list of payloads by replacing placeholders in the template with all combinations of usernames and passwords.
        """
        save = await self.get_save(self.usernames_path, self.passwords_path, template)
        if save == 3:
            return None
        elif save:
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
        if not save:
            self.save(self.usernames_path, self.passwords_path, template, tasks)
        return tasks