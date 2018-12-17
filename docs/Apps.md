# Applications
Apps are run from the launcher and use the same screen area as the launcher. <br />
In the background the launcher feeds inputs from screen and keys to the running app.<br /> 
If the app throws and unexpected exception then the launcher catches this and terminates the application.<br />
All applications are stored in the LAUNCHER_DIR location (see [config](Config.md)).<br />
All apps are currently single Python files in the launcher directory. In the future this will change to load the apps as modules.

## App Info
Each imported application file needs and `AppInfo` dictionary value to process the remaining application.<br />
Accepted values are
* iconname - string value displayed within the launcher. Needs to be short to display properly
* icon - filename of an image to show in the launcher. All images are found in the resource directory specified in [config](Config.md)
* description - string value providing more information on the application (currently unused)
* class - string providing the primary class name of the application. This class should be derived from PygameApp to support the correct interface
* framerate - optional integer value which provides the desired framerate for the application. Note that the actual rate is limited by the display hardware and CPU
