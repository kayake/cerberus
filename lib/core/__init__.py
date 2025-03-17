import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from aiohttp import ClientResponse, TraceConfig

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

class Saver:
    def __init__(self):
        """
        Initialize the Saver instance.
        """
        self.file = None

    def save(self, name: str, data: str) -> None:
        """
        Save data to a file in the .cache/saves directory.
        
        :param name: Name of the file.
        :param data: Data to save.
        """
        self.file = Path.cwd() / f".cache/saves/{name}"
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(data)
    
class TraceConfig:
    def __init__(self):
        self.trace_config = TraceConfig()
        self.trace_config.on_request_start.append(self.on_request_start)
        self.trace_config.on_request_end.append(self.on_request_end)
    
    