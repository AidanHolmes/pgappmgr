# Pygame application manager
This is a simple application manager written in Python Pygame for touchscreen and keyboard driven graphics displays.

The vision is to provide a graphics interface to control an embedded Linux system or Raspberry Pi. The idea originated from a hack of the B&N Nook Simple Touch to use the e-ink display.

Pygame was chosen as a quick language to create interfaces, taking advantage of the large number of open source libraries and existing code.

Note that new changes have been made to the configuration. config.py no longer contains the configuration and instead a pgappmgr.ini file is now representing the configuration.
Changes will be made to the Config.md reference to update the available settings.

## Reference
* [Configuration basics](docs/Config.md)
* [Plug-in application basics](docs/Apps.md)
* [PygameWnd reference](docs/PygameWnd.md)
