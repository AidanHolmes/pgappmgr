from os.path import join, isfile
from configparser import ConfigParser, ExtendedInterpolation, ParsingError

class ConfigError(Exception):
    def __init__(self, val):
        self._val = val
    def __str__(self):
        return repr(self._val)
    
class AppConfig(object):
    def __init__(self, config):
        self._config = config

    def getlist(self, txt):
        return [new.strip() for new in txt.split(",")]

    def getintsize(self,txt):
        vals = self.getlist(txt)
        if len(vals) == 2:
            try:
                return [int(val) for val in vals]
            except:
                raise ConfigError("Invalid integer size: {}".format(txt))
        else:
            raise ConfigError("2 values required for size configuration: {}".format(txt))

    def getfloatsize(self,txt):
        vals = self.getlist(txt)
        if len(vals) == 2:
            try:
                return [float(val) for val in vals]
            except:
                raise ConfigError("Invalid float size: {}".format(txt))
        else:
            raise ConfigError("2 values required for size configuration: {}".format(txt))
        
    def getcolourRGB(self,txt):
        vals = self.getlist(txt)
        if len(vals) == 3:
            try:
                return tuple([int(val) for val in vals])
            except:
                raise ConfigError("Invalid RGB configuration: {}".format(txt))
        else:
            raise ConfigError("3 values required for RGB configuration: {}".format(txt))

class DisplayConfig(AppConfig):
    def __init__(self, config, section='Display'):
        self._config = config[section]

    @property
    def size(self):
        strsize = self._config.get('size', None)
        if strsize is None:
            return None

        return self.getintsize(strsize)

    @property
    def fullscreen(self):
        return self._config.getboolean('fullscreen', False)

    @property
    def scalex(self):
        return self._config.getfloat('scale x', 1.0)

    @property
    def scaley(self):
        return self._config.getfloat('scale y', 1.0)

    @property
    def rotate90(self):
        return self._config.getboolean('rotate 90', False)

class BatteryConfig(AppConfig):
    def __init__(self, config, section='Application'):
        self._appsection = config[section]
        driver = self.driver
        self._config = None
        if driver is not None:
            self._config = config[driver]

    @property
    def config(self):
        return self._config

    @property
    def driver(self):
        return self._appsection.get('Battery Driver', None)

class SystemConfig(AppConfig):
    def __init__(self,config):
        self._config = config['System']

    @property
    def framerate(self):
        if self._config.get('framerate', 'None').upper() == 'NONE':
            return None
        return self._config.getint('framerate', None)

    @property
    def threaded(self):
        return self._config.getboolean('threaded', True)

    @property
    def resourcedir(self):
        return self._config.get('resource dir')

class NetworkConfig(AppConfig):
    def __init__(self, config, section='Network'):
        self._config = config[section]

    @property
    def statuspoll(self):
        return self._config.getint('Status Poll', 60)

class StatusBarConfig(AppConfig):
    def __init__(self, config, section='Status Bar'):
        self._config = config[section]

    @property
    def fontsize(self):
        return self._config.getint('Font Size', 40)

    @property
    def height(self):
        return self._config.getint('height', 35)

    @property
    def spacing(self):
        return self._config.getint('spacing', 10)

    @property
    def memory_icon(self):
        return self._config.get('memory icon', 'memory.png')

    @property
    def memory_icon_size(self):
        strsize = self._config.get('memory icon size', '25,25')
        return self.getintsize(strsize)

    @property
    def cpu_icon(self):
        return self._config.get('cpu icon', 'cpu.png')

    @property
    def cpu_icon_size(self):
        strsize = self._config.get('cpu icon size', '25,25')
        return self.getintsize(strsize)

    @property
    def battery_icon(self):
        return self._config.get('battery icon', '25,25')

    @property
    def battery_icon_size(self):
        strsize = self._config.get('battery icon size', '25,25')
        return self.getintsize(strsize)

    @property
    def background(self):
        strcol = self._config.get('background', '255,255,255')
        return self.getcolourRGB(strcol)


class LauncherConfig(AppConfig):
    def __init__(self, config, section='Launcher'):
        self._config = config[section]

    @property
    def launcherdir(self):
        return self._config['Launcher Dir']

    @property
    def defaultclass(self):
        return self._config['Default Class']

    @property
    def fontsize(self):
        return self._config.getint('font size', 24)

    @property
    def iconsize(self):
        strsize = self._config.get('icon size', '64,64')
        return self.getintsize(strsize)

    @property
    def defaulticon(self):
        return self._config['default icon']

    @property
    def background(self):
        strcol = self._config.get('background', '255,255,255')
        return self.getcolourRGB(strcol)

    @property
    def stride(self):
        return self._config.getint('stride', 150)

    @property
    def rowheight(self):
        return self._config.getint('rowheight', 150)
        
class PgAppMgrConfig(object):
    DEFAULT_FILE = "pgappmgr.ini"
    def __init__(self):
        self._file = None
        self._config = None
        self._isopen = False
        self.display = None
        self.system = None
        self.battery = None
        self.network = None
        self.statusbar = None
        self.launcher = None

    @property
    def isopen(self):
        return self._isopen
    
    def findconfig(self):
        if isfile(PgAppMgrConfig.DEFAULT_FILE):
            return PgAppMgrConfig.DEFAULT_FILE
        filename = join("/etc/", PgAppMgrConfig.DEFAULT_FILE)
        if isfile(filename):
            return filename

        return None
        
    def open(self, filename=None):
        if filename is None:
            self._file = self.findconfig()
            if self._file is None:
                raise ConfigError("Cannot find config file. Please check permissions or create a new config")
        else:
            self._file = filename

        if not isfile(self._file):
            raise ConfigError("Cannot open config file {}".format(self._file))

        try:
            self._config = ConfigParser(interpolation=ExtendedInterpolation(), default_section="Application")
            self._config.read_file(open(self._file))
        except ParsingError:
            print("Cannot open configuration file {}".format(self._file))
            raise
        except:
            raise

        self._isopen = True
        self.display = DisplayConfig(self._config)
        self.system = SystemConfig(self._config)
        self.battery = BatteryConfig(self._config)
        self.network = NetworkConfig(self._config)
        self.statusbar = StatusBarConfig(self._config)
        self.launcher = LauncherConfig(self._config)

Config = PgAppMgrConfig()
