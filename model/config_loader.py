import yaml

class ConfigLoader:
    _config_path = ""
    _config = None

    _char_density_path = ""
    _weapon_density_path = ""
    _char_pity = 0
    _weapon_pity = 0
    _model_output_path = ""
    _model_output_filename = ""
    _models_conf = None

    def __init__(self, config_path):
        self._config_path = config_path

    
    def load(self):
        with open(self._config_path) as config_file:
            self._config = yaml.safe_load(config_file)

        self._char_density_path = self._config["char_density_path"]
        self._weapon_density_path = self._config["weapon_density_path"]
        self._char_pity = self._config["char_pity"]
        self._weapon_pity = self._config["weapon_pity"]
        self._model_output_path = self._config["model_output_path"]
        self._model_output_filename = self._config["model_output_filename"]
        self._models_conf = self._config["models_conf"]

    @property
    def char_density_path(self):
        return self._char_density_path
    
    @property
    def weapon_density_path(self):
        return self._weapon_density_path
    
    @property
    def char_pity(self):
        return self._char_pity
    
    @property
    def weapon_pity(self):
        return self._weapon_pity
    
    @property
    def model_output_path(self):
        return self._model_output_path
    
    @property
    def model_output_filename(self):
        return self._model_output_filename
    
    @property
    def models_conf(self):
        return self._models_conf