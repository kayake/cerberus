import pathlib
import plyvel

PATH = ".cache/"
SAVE_PATH = ".cache/saves/"

class CerberusCache:
    def __init__(self):
        self.path = pathlib.Path(PATH)
        self.save_path = pathlib.Path(SAVE_PATH)
        self.db = plyvel.DB(SAVE_PATH, create_if_missing=True)

    def get_save(self, name: str):
        """
        Get a save from the database.
        :param name: The name of the save to get (wordlist1+wordlist2).
        """
        if not self.save_path.exists():
            return None
        with self.db:
            return self.db.get(name.encode())

    def set_save(self, name: str, payload: list):
        """
        Set a save in the database.
        :param name: The name of the save to set (wordlist1+wordlist2).
        :param payload: The data to save.
        """
        _bytes = bytes(payload)
        data = _bytes.decode("utf-8")
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)
        with self.db:
            self.db.put(name.encode(), data)