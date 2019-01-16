import pygame

WINSIZE = [800, 480]
# Hyperpixel 4 work around scaling
# https://forums.pimoroni.com/t/hyperpixel-4-touch-screen-dimensions-are-swapped/8198/2
SCALEX=1.67
SCALEY=0.6
ROTATE90 = False
#FRAMERATE = None
FRAMERATE = 10
THREADED_SYSTEM = True
MODE = pygame.NOFRAME | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
#MODE = pygame.DOUBLEBUF | pygame.HWSURFACE

BATT_DEVICE = '/sys/class/power_supply/bq27510-0/'
BATT_CAPACITY = 'capacity'
BATT_STATUS = 'status'
BATT_QUERY_TIME = 5

NETWORK_QUERY_TIME = 15

RESOURCE_DIR = '/home/pi/code/pgappmgr/res'

SYSTEM_HEADER_FONT_SIZE = 40
SYSTEM_HEADER_BAR_HEIGHT = 35
SYSTEM_HEADER_MEM_ICON = 'memory.png'
SYSTEM_HEADER_MEM_ICON_SIZE = (25,25)
SYSTEM_HEADER_CPU_ICON = 'cpu.png'
SYSTEM_HEADER_CPU_ICON_SIZE = (25,25)
SYSTEM_HEADER_BATT_ICON = 'battery.png'
SYSTEM_HEADER_BATT_ICON_SIZE = (25,25)
SYSTEM_HEADER_SPACING = 10

LAUNCHER_DIR = '/home/pi/code/pgappmgr/apps'
LAUNCHER_DEFAULT_CLASS = 'PygameApp'
LAUNCHER_ICON_FONT_SIZE = 24
LAUNCHER_ICON_IMAGE_SIZE = (64,64)
LAUNCHER_DEFAULT_ICON_IMAGE = 'python.png'
