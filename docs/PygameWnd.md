# PygameWnd class reference
## Notes
Windows are expected to handle their own drawing routines.<br />
A parent window will recursively blit child surfaces when copy_to is called and assumes the child surface is drawn.

## Importing
Requires pygame module<br />
`from pgwindow import PygameWnd`

## __init__(rect=None, screen=None)
Initialise the window with optional parameters of `rect` or `screen`<br />
If no parameters are given then the window will not yet be created and a call to `createwnd` will be necessary
`rect` specifies a `pygame.Rect` object for the window. x and y offsets are requried to position a window relative to the parent.
`screen` specifies a `pygame.Surface` object to use. If not specified then one will be created from `rect` diamensions. 
If `rect` is no specified then diamensions from the `screen` Surface will be used but will be missing x,y relative offsets.

## Properties
* parent - set or get the parent window. This is set implicitly by `add_child`
* screen_position - gets the absolute Rect of the window within the app. Recursive query. Cannot set this value directly
* position - gets or sets the relative window with a 4 value tuple of (x,y,width,height)
* hidden - returns True if window is hidden. Will not draw to parent if hidden
* active - returns True if active. Inactive windows do not process inputs
* focused - returns True if window is in focus. Can be set to focused or implicitly set by touch inputs. Only key inputs go to focused windows
* invert - returns True if inverted. When inverted the entire window graphics are inverted in colour

## add_child(wnd, order=TOP)
Adds a child window to a parent. This allows processing of inputs and suface blitting to the parent window.<br />
`wnd` is a PygameWnd class object contained in the parent window<br />
`order` sets the zorder of the window. If not specified it will be the topmost window

## remove_child(wnd)
Remove child from parent window. Returns True if successful and False if child doesn't exist<br />
`wnd` must be base classed from a PygameWnd object

## set_zorder(wnd,order=TOP)
Same functionality as add_child for an existing child window. Changes the zorder or if `order` is not specified then moves window to the top

## get_zorder(wnd)
Returns zorder index of a window specified in `wnd`. The window should have been set by add_child

## touch(evt)
Touch event router function. Calls `window_touch` function if touch events are on a window. Continues until a window processes the touch event<br />
Override this to create custom touch event routing<br />
`evt` is a dictionary of the touch event. Values are absolute for the screen.

## window_touch(x, y, pressed)
Called when a window has received a touch event. Override to process these messages. <br />
Return True to confirm that the touch was processed and prevent the parent receiving the touch event.<br />
Return False to pass the event up to the parent window to process<br />
`x` contains the relative x location touched<br />
`y` contains the relative y location touched<br />
`pressed` contains 1 for touch down and 0 for touch up

## keyinput(evt)
Key input router function. This will call the `window_key` function for focused windows.<br />
Override to customise the key event routing.<br />
`evt` is a dictionary of the key event

## window_key(press, keyid, key)
Called when a window receives a key press. Only focused windows receive these.<br />
`press` key up when 0 and down when 1<br />
`keyid` the numeric identifier for the key (from evdev)<br />
`key` contains a text name for the key pressed (if known)<br /><br />

## createwnd(rect)
Create a window Surface<br />
`rect` specifies the diamensions as well as the windows relative position<br />
<br />
## copy_to(surface)
Copy the calling window to a pygame.Surface specified by `surface`.<br />
Automatically inverts windows and calls blit to copy contents. 

