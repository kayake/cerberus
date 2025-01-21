import yaml

class ConfigManager:
    def __init__(self, file:str="config.yaml"):
        self.file = file
        self.load(file)

    def load(self, file: str) -> None:
        with open(file, "r") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

    def set(self, key_path: str, new_value: str | int | object) -> None:
        keys = key_path.split(".")
        current = self.config
        for key in keys[:-1]:
            current = current[key]
        
        current[keys[:-1]] = new_value

        with open(self.file, "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)
    
    def get(self, key) -> str | int | object:
        return self.config[key]
