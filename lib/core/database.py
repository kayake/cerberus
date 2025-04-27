import pathlib
import plyvel
import json

PATH = ".cache/"
SAVE_PATH = ".cache/saves/payloads/"
CHECKPOINT_PATH = ".cache/saves/checkpoints/"

class SavePayloads:
    def __init__(self):
        self.path = pathlib.Path(PATH)
        self.save_path = pathlib.Path(SAVE_PATH)
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)
        self.db = plyvel.DB(
            SAVE_PATH, 
            create_if_missing=True,
            )

    def get(self, template: str, name: str):
        """
        Get a save from the database.
        :param name: The name of the save to get (wordlist1+wordlist2).
        """
        data = self.db.get(template.encode())
        if data:
            data = json.loads(data.decode())
            return data.get(name, None)
        return None

    def get_all(self, template: str):
        """
        Get all saves from the database.
        :param template: The name of the save to get (wordlist1+wordlist2).
        """
       
        return self.db.get(template.encode())
    
    def get_all_keys(self):
        """
        Get all keys from the database.
        :return: A list of all keys in the database.
        """
        
        return [key.decode() for key, _ in self.db.iterator()]

    def set_save(self, template: str, name: str, payload: list):
        """
        Set a save in the database.
        :param name: The name of the save to set (wordlist1+wordlist2).
        :param payload: The data to save.
        """
        
        self.db.put(template.encode(), json.dumps({name: payload}).encode())
    
    def delete(self, template: str):
        """
        Delete a save from the database.
        :param template: The name of the save to delete (wordlist1+wordlist2).
        """
       
        self.db.delete(template.encode())
        return True

class Checkpoint:
    def __init__(self):
        self.path = pathlib.Path(PATH)
        self.save_path = pathlib.Path(SAVE_PATH)
        if not self.save_path.exists():
            self.save_path.mkdir(parents=True, exist_ok=True)
        self.db = plyvel.DB(SAVE_PATH, create_if_missing=True)

    def get(self, name: str, id: int = 0):
        """
        Get a checkpoint from the database.
        :param name: The name of the checkpoint to get (wordlist1+wordlist2).
        """
        with self.db:
            return self.db.get(name.encode()).get(id, None)
    def set(self, name: str, id: int, index: int):
        """
        Set a checkpoint in the database.
        :param name: The name of the checkpoint to set (wordlist1+wordlist2).
        :param id: The id of the checkpoint to set.
        :param index: The index to save.
        """
        _bytes = bytes(index)
        data = _bytes.decode("utf-8")
        
        with self.db:
            self.db.put(name.encode(), {id: data})