import configparser

class ConfigMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwds):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwds)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class Config(metaclass = ConfigMeta):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./config_files/config.ini')
        
        self.VT_API_KEY = config['VT']['VT_API_KEY']
        self.VT_API_URL = config['VT']['VT_API_URL']
        self.filesystem_path = config['PATHS']['filesystem_path']
        self.db_path = config['PATHS']['db_path']
        self.disk_path = config['PATHS']['disk_path']
        self.phy_mount_path = config['PATHS']['phy_mount_path']
        self.skip_list = config['PATHS']['skip_list']