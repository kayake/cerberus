import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Tuple


import yaml
from aiohttp import ClientResponse
from packaging.version import parse, Version

REPO_URL = "https://github.com/kayake/cerberus"

# Configure logging with colors and custom time format
class CustomFormatter(logging.Formatter):
    """Custom logging formatter to add colors and custom time format."""
    COLORS = {
        'DEBUG': '\033[34m',  # Blue
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m',  # Magenta
        'CYAN': '\033[96m',  # Cyan
        'ORANGE': '\033[33m',  # Orange
        'DARK_CYAN': '\033[36m',  # Dark Cyan
        'LIGHT_GRAY': '\033[37m',  # Light Gray
        'DARK_GRAY': '\033[90m',  # Dark Gray
        'LIGHT_RED': '\033[91m',  # Light Red
        'LIGHT_GREEN': '\033[92m',  # Light Green
        'LIGHT_YELLOW': '\033[93m',  # Light Yellow
        'LIGHT_BLUE': '\033[94m',  # Light Blue
        'LIGHT_MAGENTA': '\033[95m',  # Light Magenta
        'LIGHT_CYAN': '\033[96m',  # Light Cyan
        'WHITE': '\033[97m',  # White
        'BLACK': '\033[30m',  # Black
        'RED': '\033[31m',  # Red
        'GREEN': '\033[32m',  # Green
        'YELLOW': '\033[33m',  # Yellow
        'BLUE': '\033[34m',  # Blue
        'MAGENTA': '\033[35m',  # Magenta
        'CYAN': '\033[36m',  # Cyan
        'DARK_GREEN': '\033[32m',  # Dark Green
        'DARK_BLUE': '\033[34m',  # Dark Blue
        'DARK_MAGENTA': '\033[35m',  # Dark Magenta
        'DARK_YELLOW': '\033[33m',  # Dark Yellow
        'DARK_RED': '\033[31m',  # Dark Red
        'DARK_ORANGE': '\033[33m',  # Dark Orange
        'DARK_PURPLE': '\033[35m',  # Dark Purple
        'DARK_PINK': '\033[35m',  # Dark Pink
        'DARK_TEAL': '\033[36m',  # Dark Teal
        'DARK_BROWN': '\033[33m',  # Dark Brown
        'DARK_AQUA': '\033[36m',  # Dark Aqua
        'DARK_VIOLET': '\033[35m',  # Dark Violet
        'DARK_INDIGO': '\033[34m',  # Dark Indigo
        'DARK_LIME': '\033[32m',  # Dark Lime
        'DARK_MINT': '\033[36m',  # Dark Mint
        'DARK_TURQUOISE': '\033[36m',  # Dark Turquoise
        'DARK_SALMON': '\033[31m',  # Dark Salmon
        'DARK_CORAL': '\033[31m',  # Dark Coral
        'DARK_PEACH': '\033[33m',  # Dark Peach
        'DARK_MAROON': '\033[31m',  # Dark Maroon
        'DARK_OLIVE': '\033[32m',  # Dark Olive
        'DARK_NAVY': '\033[34m',  # Dark Navy
        'DARK_SKY': '\033[36m',  # Dark Sky
        'DARK_SEA': '\033[36m',  # Dark Sea
        'DARK_FOREST': '\033[32m',  # Dark Forest
        'DARK_JADE': '\033[36m',  # Dark Jade
        'DARK_EMERALD': '\033[32m',  # Dark Emerald
        'DARK_RUBY': '\033[31m',  # Dark Ruby
        'DARK_SAPPHIRE': '\033[34m',  # Dark Sapphire
        'DARK_AMETHYST': '\033[35m',  # Dark Amethyst
        'DARK_TOPAZ': '\033[33m',  # Dark Topaz
        'DARK_OPAL': '\033[36m',  # Dark Opal
        'DARK_QUARTZ': '\033[37m',  # Dark Quartz
        'DARK_DIAMOND': '\033[37m',  # Dark Diamond
        'DARK_GOLD': '\033[33m',  # Dark Gold
        'DARK_SILVER': '\033[37m',  # Dark Silver
        'DARK_BRONZE': '\033[33m',  # Dark Bronze
        'DARK_COPPER': '\033[33m',  # Dark Copper
        'DARK_PLATINUM': '\033[37m',  # Dark Platinum
        'DARK_TITANIUM': '\033[37m',  # Dark Titanium
        'DARK_ZINC': '\033[37m',  # Dark Zinc
        'DARK_NICKEL': '\033[37m',  # Dark Nickel
        'DARK_CHROME': '\033[37m',  # Dark Chrome
        'DARK_STEEL': '\033[37m',  # Dark Steel
        'DARK_IRON': '\033[37m',  # Dark Iron
        'DARK_ALUMINUM': '\033[37m',  # Dark Aluminum
        'DARK_TIN': '\033[37m',  # Dark Tin
        'DARK_LEAD': '\033[37m',  # Dark Lead
        'DARK_MERCURY': '\033[37m',  # Dark Mercury
        'DARK_URANIUM': '\033[37m',  # Dark Uranium
        'DARK_PLUTONIUM': '\033[37m',  # Dark Plutonium
        'DARK_NEPTUNIUM': '\033[37m',  # Dark Neptunium
        'DARK_AMERICIUM': '\033[37m',  # Dark Americium
        'DARK_CURIUM': '\033[37m',  # Dark Curium
        'DARK_BERKELIUM': '\033[37m',  # Dark Berkelium
        'DARK_CALIFORNIUM': '\033[37m',  # Dark Californium
        'DARK_EINSTEINIUM': '\033[37m',  # Dark Einsteinium
        'DARK_FERMIUM': '\033[37m',  # Dark Fermium
        'DARK_MENDELEVIUM': '\033[37m',  # Dark Mendelevium
        'DARK_NOBELIUM': '\033[37m',  # Dark Nobelium
        'DARK_LAWRENCIUM': '\033[37m',  # Dark Lawrencium
        'DARK_RUTHERFORDIUM': '\033[37m',  # Dark Rutherfordium
        'DARK_DUBNIUM': '\033[37m',  # Dark Dubnium
        'DARK_SEABORGIUM': '\033[37m',  # Dark Seaborgium
        'DARK_BOHRIUM': '\033[37m',  # Dark Bohrium
        'DARK_HASSIUM': '\033[37m',  # Dark Hassium
        'DARK_MEITNERIUM': '\033[37m',  # Dark Meitnerium
        'DARK_DARMSTADTIUM': '\033[37m',  # Dark Darmstadtium
        'DARK_ROENTGENIUM': '\033[37m',  # Dark Roentgenium
        'DARK_COPERNICIUM': '\033[37m',  # Dark Copernicium
        'DARK_NIHONIUM': '\033[37m',  # Dark Nihonium
        'DARK_FLEROVIUM': '\033[37m',  # Dark Flerovium
        'DARK_MOSCOVIUM': '\033[37m',  # Dark Moscovium
        'DARK_LIVERMORIUM': '\033[37m',  # Dark Livermorium
        'DARK_TENNESSINE': '\033[37m',  # Dark Tennessine
        'DARK_OGANESSON': '\033[37m',  # Dark Oganesson
    } 
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        if 'BOLD' in record.msg:
            record.levelname = f"{log_color}{self.BOLD}{record.levelname}{self.RESET}"
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.name = f"{self.COLORS.get('DARK_RUBY')}{record.name}{self.RESET}"
        record.asctime = self.formatTime(record, "%H:%M:%S")
        return f"[{self.COLORS.get("DARK_CYAN")}{record.asctime}{self.RESET}] - {record.name} - {record.levelname} - {record.msg.replace("BOLD", "").replace("__H", self.COLORS.get("MAGENTA")).replace("__h", self.RESET)}"

log = logging.getLogger(__name__)

class ReadYAMLFile:
    def __init__(self, file_path: str):
        """
        Initialize the ReadYAMLFile instance by reading the YAML file and wrapping its contents.
        
        :param file_path: Path to the YAML file.
        """
        self._data = {}
        data = self.read(file_path)
        self._data = {k: self.__wrap__(v) for k, v in data.items()}

    def read(self, file_path: str) -> Dict[str, Any]:
        """
        Read the .yaml configuration from the file.
        
        :param file_path: Path to the YAML file.
        :return: Parsed YAML data as a dictionary.
        """
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
        
    def __wrap__(self, value: Any) -> Any:
        """
        Recursively wrap dictionary and list values into ReadYAMLFile instances or lists.
        
        :param value: Value to wrap.
        :return: Wrapped value.
        """
        if isinstance(value, dict):
            obj = self.__class__.__new__(self.__class__)
            obj._data = {k: self.__wrap__(v) for k, v in value.items()}
            return obj
        elif isinstance(value, list):
            return [self.__wrap__(item) for item in value]
        return value
    
    def __getattr__(self, name: str) -> Any:
        """
        Get attribute from the wrapped data, creating a new wrapped instance if it doesn't exist.
        
        :param name: Attribute name.
        :return: Attribute value.
        """
        if name not in self._data:
            self._data[name] = self.__wrap__({})
        return self._data[name]

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set attribute in the wrapped data.
        
        :param name: Attribute name.
        :param value: Attribute value.
        """
        if name == '_data':
            super().__setattr__(name, value)
        else:
            self._data[name] = self.__wrap__(value)

    def __getitem__(self, key: str) -> Any:
        """
        Get item from the wrapped data using square bracket notation.
        
        :param key: Key name.
        :return: Value associated with the key.
        """
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set item in the wrapped data using square bracket notation.
        
        :param key: Key name.
        :param value: Value to set.
        """
        self._data[key] = self.__wrap__(value)

    def __repr__(self) -> str:
        """
        Represent the object as a string for debugging.
        
        :return: String representation of the internal data.
        """
        return repr(self._data)

async def verify_response(expected_response: Any, response: ClientResponse) -> bool:
    """
    Verify the response from an aiohttp ClientResponse object.
    
    :param expected_response: Expected response content.
    :param response: aiohttp ClientResponse object.
    :return: True if the response matches the expected content, False otherwise.
    """
    status = str(response.status)

    if expected_response == status or str(expected_response) in status:
        return True

    try:
        json_response = await response.json()

        if expected_response in json_response or expected_response in json.dumps(json_response):
            return True
    except Exception:
        pass
    text_response = await response.text()

    if expected_response in text_response:
        return True

    return False

class HeadersReader:
    def __init__(self, headers_path: str):
        """
        Initialize the HeadersReader instance by reading the headers file.
        
        :param headers_path: Path to the headers file.
        """
        self.headers_path = Path.cwd() / headers_path
        if not self.headers_path.exists():
            log.warning(f"Headers file not found: {self.headers_path}")
    
    def __read_headers(self) -> Dict[str, str]:
        """
        Read the headers from the file.
        
        :return: Parsed headers as a dictionary.
        """
        headers = {}
        with open(self.headers_path, "r") as file:
            headers = yaml.load(file)
        return headers

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the headers from the file.
        
        :return: Headers as a dictionary.
        """
        if not self.headers_path.exists():
            return {}
        try:
            headers = self.__read_headers()
            return headers
        except Exception as e:
            log.debug(f"Failed to read headers: {e}")
            return {}
    
class CheckUpdate:
    def __init__(self):
        """
        Initialize the CheckUpdate instance.
        """
        self.file = None

    def run_git(self, cmd: str) -> str | Tuple[None, str]:
        try:
            result = subprocess.run(
                ['git'] + cmd.split(), 
                capture_output=True,
                check=True,
                text=True, 
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.debug(f"Command '{cmd}' failed with error: {e.stderr.strip()}")
            return None
        
    def current_version(self) -> Tuple[Version, str]:
        """
        Get the current version of Cerberus.
        
        :return: Current version of Cerberus.
        """
        current_tag = self.run_git("describe --tags --exact-match HEAD")
        if current_tag:
            return parse(current_tag), "stable"
    
        # check if user is using dev branch
        current_tag_aprox: Version = parse(self.run_git("describe --tags --abbrev=0"))
        current_branch = self.run_git("rev-parse --abbrev-ref HEAD")
        if current_branch == "dev":
            commit_hash = self.run_git("rev-parse --short HEAD")
            return parse(f"{current_tag_aprox.major}.{current_tag_aprox.minor}.dev{current_tag_aprox.micro}+{commit_hash}"), "dev"
        
        return "Custom", "custom"

    def check_update_priority(self) -> int:
        """
        Check the priority of the update.
        
        :return: Priority of the update.
        """
        current, type = self.current_version()
        self.run_git(f"config --local --add cerberus.lastVersion {current}")
        if type == "dev":
            _, last_dev_tag = self.fetch_dev_status()
            if not last_dev_tag:
                return 4
            return 3
        
        _, last_stable_tag = self.fetch_stable_status()
        if not last_stable_tag:
            return 0
        
        latest = parse(last_stable_tag)

        if current.major < latest.major:
            return 2
        
        if (current.minor, current.micro) < (latest.minor, latest.micro):
            return 1
        
        return 0
    

    def fetch_dev_status(self) -> Tuple[bool, str]:
        """
        Fetch the development status of Cerberus.
        
        :return: True if the development status is "dev", False otherwise.
        """
        dev_tag = self.run_git("fetch --tags origin dev")
        if not dev_tag:
            self.run_git("fetch origin dev")
        dev_commit = self.run_git("rev-parse origin/dev")
        current_commit = self.run_git("rev-parse HEAD")
        return dev_commit != current_commit, dev_tag

    def fetch_stable_status(self) -> Tuple[bool, str]:
        """
        Fetch the stable status of Cerberus.
        
        :return: True if the stable status is "stable", False otherwise.
        """
        stable_tag = self.run_git("fetch --tags origin master")
        stable_commit = self.run_git("rev-parse origin/master")
        current_commit = self.run_git("rev-parse HEAD")
        return stable_commit != current_commit, stable_tag
    
    def generate_changelog(self, old_version: str, new_version: str) -> str:
        """
        Generate a changelog between two versions.
        
        :param old_version: Old version of Cerberus.
        :param new_version: New version of Cerberus.
        :return: Changelog as a string.
        """
        current_branch = self.run_git("rev-parse --abbrev-ref HEAD")
        commits = self.run_git(f"log --pretty=format:%h||%s||%b {old_version}..{new_version}")
        if not commits:
            return "No changes found."
        changes = []
        for commit in commits.split("\n"):
            commit_hash, subject, body = commit.split("||", 2)
            changes.append(f"[{commit_hash}]({REPO_URL}/{current_branch}/commits/{hash}): {subject}\n{body}")
        if not changes:
            return "No changes found."
        # Format the changelog
        changes = [f"- {change}" for change in changes]
        changes = "\n".join(changes)
        # Add the version numbers
        changes = changes.replace(old_version, f"**{old_version}**")
        changes = changes.replace(new_version, f"**{new_version}**")
        # Generate changelog
        return f"Changelog from {old_version} to {new_version}:\n" + "\n".join(changes)

    def perform_update(self, dev: bool = False) -> None:
        """
        Perform the update of Cerberus.
        
        :param dev: If True, update to the development version.
        """
        if dev:
            self.run_git("checkout dev")
            self.run_git("pull origin dev")
        else:
            self.run_git("pull origin master")

    def handle_update(self, grade: int) -> Tuple[str]:
        """
        Handle the update status and return a formatted message.
        
        :param grade: Grade of the update.
        :return: Formatted message and grade.
        """
        colors = {
            0: "\033[92m",
            1: "\033[38;5;214m",
            2: "\033[91m",
            3: "\033[94m",
            4: "\033[94m"
        }

        messages = {
            0: "latest",
            1: "stable",
            2: "outdated",
            3: "dev",
            4: "dev"
        }

        if grade == -1:
            return "\033[91mFailed to check for updates.\033[0m", grade

        return f"{colors[grade]}{messages.get(grade, 'NOT_DETECTED')}\033[0m", grade

    def update(self) -> Tuple[any, str, str]:
        """
        Update the Cerberus repository.
        """
        log.info("Checking for updates and version")
        update_dev, dev = self.fetch_dev_status()
        update_master, stable = self.fetch_stable_status()
        current, type = self.current_version()
        grade = self.check_update_priority()
        log.info(f"BOLDVersion: {current} ({self.handle_update(grade)[0]})")
        if grade == 0:
            return None
        if grade == 1:
            if update_master:
                log.warning(f"Update available ({stable})")
                y = input(f"\033[1mDo you want to update to the latest stable version? [Y/n] \033[0m").lower() or "y"
                if "y" in y.lower():
                    log.info("Updating to the latest stable version...")
                    self.perform_update()
                    log.info("BOLDUpdate complete!")
                return None
            elif update_dev:
                log.warning(f"Update available ({dev})")
                y = input(f"\033[1mDo you want to update to the latest dev version? [Y/n] \033[0m").lower() or "y"
                if "y" in y.lower():
                    log.info("Updating to the latest dev version...")
                    self.perform_update(dev=True)
                    log.info("BOLDUpdate complete!")
            else:
                log.info("Already on the latest version.")
        if grade == 2:
            if update_master:
                log.warning(f"Update available ({stable})")
                log.info("Updating to the latest stable version...")
                self.perform_update()
                log.info("BOLDUpdate complete!")
            if update_dev:
                log.warning(f"Update available ({dev})")
                log.info("Updating to the latest dev version...")
                self.perform_update(dev=True)
                log.info("BOLDUpdate complete!")

        if update_dev or update_master and grade != 4:
            changelog = self.generate_changelog(current, stable)
            print(f"Changelog:\n{changelog}")
            self.run_git("config --local --add cerberus.lastVersion {stable}")
            if type == "dev":
                self.run_git("config --local --add cerberus.lastVersion {dev}")
            
        return self.run_git, current, type