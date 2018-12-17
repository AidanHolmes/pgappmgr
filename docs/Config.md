# Configuration
Settings are simply a Python file containing global variables for the application. These are documented here.<br />
All settings are contained in `config.py` and everything is included into the other Python files.

## WINSIZE
*Accepted values:* A list containing 2 values for width and height. <br />
This acts as a preferred screen size.<br />
The setting is mandatory for the App Launcher, but may become optional in the future as Pygame detects the available resolutions.

## ROTATE90
*Accepted values:* True or False<br />
If True then the screen is drawn 90 anti-clockwise, otherwise no rotation is applied. 

## FRAMERATE
*Accepted values:* Integer value<br />
Mandatory setting to set the number of cycles that the main application launcher and system header runs at. 
Applications can override this and specify faster or slower framerates. This value will be retained when returning back to the launcher.
If None is specified then the main application runs as fast as possible, which will be required if the system is not threaded (see THREADED_SYSTEM).
A framerate of at least 2 per second is needed to maintain updates of the UI. 

## THREADED_SYSTEM
*Accepted values:* True or False<br />
Touch and key inputs are handled in a separate thread. Setting this to True saves CPU cycles when app is idle in combination with a low idle framerate.<br />
The setting is mandatory.

## MODE
*Accepted values:* pygame screen modes (see pygame docs)<br />
This may be removed in the future as the application requires fullscreen to properly work. Windowed mode doesn't support the touch inputs. 
Values can be combined together with the bit operator |

## BATT_DEVICE
*Accepted value:* path string<br />
Path to a battery driver in Linux which provides information of power levels. The application will work with an invalid path and will not provide battery power info if unavailable.

## BATT_CAPACITY
*Accepted value:* string<br />
Name of attribute in driver which specifies the percentage of battery remaining as an integer

## BATT_STATUS
*Accepted value:* string<br />
Name of driver attribute which provides status

## BATT_QUERY_TIME
*Accepted value:* integer<br />
Number of seconds to query battery driver.

## NETWORK_QUERY_TIME
*Accepted value:* integer<br />
Number of seconds between queries of network status. Picks up device IP in query. Shouldn't need to be very frequent.

## RESOURCE_DIR
*Accepted value:* path string<br />
Directory where the application resource files are stored.

## LAUNCHER_DIR
*Accepted value:* path string<br />
Directory where applications are stored for the launcher app. The launcher queries this directory on startup to list apps and run them.

## LAUNCHER_DEFAULT_CLASS
*Accepted value:* string<br />
Name of default class to look for if App Info is missing the class name. Recommended to keep as `PygameApp`.

## LAUNCHER_ICON_FONT_SIZE 
*Accepted value:* integer<br />
The font size to use for launcher app icons

## LAUNCHER_ICON_IMAGE_SIZE 
*Accepted value:* tuple containing 2 integer values<br />
A width and height value specifying the size of the icon images

## LAUNCHER_DEFAULT_ICON_IMAGE 
*Accepted value:* string<br />
This is the filename of a default icon image to use when App Info omits the name or it cannot be found. This image must reside in the RESOURCE_DIR.

