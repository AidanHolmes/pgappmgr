# Window and application classes for use with touchscreen and keyboard inputs 
#
# Copyright (C) 2018 Aidan Holmes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Email: aidanholmes@orbitalfruit.co.uk

import pygame
import time

AppInfo = {'iconname':'Default',
           'icon':None,
           'description':'Default',
           'class':'PygameApp'}

class Clock(object):
    def __init__(self, timeout = None, fn=None, immediate=True):
        self._t = 0
        self._fn = None
        self._sectimer = 0
        if timeout is not None:
            self.set_timer(timeout, fn, immediate)

    def set_timer(self, timeout, fn=None, immediate=True):
        if not immediate:
            self._t = time.time()
        self._sectimer = timeout
        self._fn = fn

    def tick(self):
        t = time.time()
        if self._t + self._sectimer <= t:
            self._t = t
            if self._fn is not None:
                self._fn()
            return True
        return False
        
class FrameClock(object):
    def __init__(self):
        self._clock = pygame.time.Clock()
        self._frame_t = 0
        self._framerate = None
        self._ontick = None

    def ontick(self, fr, fn=None):
        self._framerate = fr
        self._ontick = fn

    def tick(self):
        'Returns true if frame should be processed. Calls back function if provided'
        if not self._framerate:
            return False
        ret = False
        self._frame_t = self._frame_t + self._clock.get_rawtime()
        if self._frame_t > (1000/self._framerate):
            ret = True
            self._frame_t = 0
            if self._ontick :
                self._ontick()
        self._clock.tick()

        return ret

class PygameWnd(object):
    TOP = 0
    BOTTOM = -1
    def __init__(self, rect=None, screen=None):
        'Create a window for pygame. Optional rect to define location and size'
        self._surface = None
        self._wndpos = None
        self._isdirty = True
        self._invert = False
        self._ishidden = False
        self._isactive = True # will this wnd accept input?
        self._isfocused = False
        self._children = []
        if rect is not None:
            self._wndpos = rect.copy()
        if screen is not None:
            self._surface = screen
            if rect is None:
                self._wndpos = screen.get_rect()
        if rect is not None and screen is None:
            self.createwnd(rect)
        self.parent = None

    @property
    def screen_position(self):
        'obtain position on screen (actual)'
        if self.parent:
            rect = self._wndpos.copy()
            rect.x = rect.x + self.parent.screen_position.x
            rect.y = rect.y + self.parent.screen_position.y
            return rect
        else:
            # Top level windows just report their position
            return self._wndpos.copy()
        
    @property
    def position(self):
        'obtain position relative to parent window'
        return self._wndpos.copy()

    @position.setter
    def position(self, val):
        if isinstance(val, pygame.Rect):
            self._wndpos = val.copy()
        elif isinstance(val, tuple):
            if not len(val) == 4:
                raise TypeError("Incorrect tuple length")
            if val[0] is not None:
                self._wndpos.x = val[0]
            if val[1] is not None:
                self._wndpos.y = val[1]
            if val[2] is not None:
                self._wndpos.width = val[2]
            if val[3] is not None:
                self._wndpos.height = val[3]

        else:
            raise TypeError("Incorrect type for position")

    @property
    def hidden(self):
        return self._ishidden

    @hidden.setter
    def hidden(self,val):
        if val:
            self._ishidden = True
        else:
            self._ishidden = False

    @property
    def active(self):
        return self._isactive

    @active.setter
    def active(self,val):
        if val: self._isactive = True
        else: self._isactive = False

    @property
    def focused(self):
        return self._isfocused

    @focused.setter
    def focused(self,val):
        if val: self._isfocused = True
        else:
            self._isfocused = False
            for child in self._children:
                child.focused = False
        
    @property
    def invert(self):
        return self._invert

    @invert.setter
    def invert(self, setinvert):
        self._invert = setinvert

    def add_child(self, wnd, order=TOP):
        if wnd in self._children:
            # already added
            return False
        if order < 0 or order >= len(self._children):
            self._children.append(wnd)
        else:
            self._children.insert(order, wnd)

        wnd.parent = self

        return True

    def remove_child(self, wnd):
        try:
            self._children.remove(wnd)
            return True
        except ValueError:
            pass
        
        return False

    def set_zorder(self,wnd,order=TOP):
        self.remove_child(wnd)
        self.add_child(wnd,order)

    def get_zorder(self,wnd):
        return self._children.index(wnd)
    
    def touch(self, evt):
        'send touch event to a window. Triggers window_touch'
        if not self._isactive or self._ishidden:
            self.focused = False
            return False
        # otherwise process the touch event
        if self.screen_position.collidepoint(evt['x'], evt['y']):
            self.focused = True
            # Check children, did this hit them?
            for child in self._children:
                if child.touch(evt):
                    return True
            # No children to process, but this window can
            # Do work
            normalised_evt_x = evt['x'] - self.screen_position.x
            normalised_evt_y = evt['y'] - self.screen_position.y
            return self.window_touch(normalised_evt_x,
                                     normalised_evt_y,
                                     evt['press'])
        # Touch not for this window
        self.focused = False
        return False

    def window_touch(self, x, y, pressed):
        'called when this window has received a touch event'
        return False
    
    def keyinput(self, evt):
        'Send a key event to focused windows'
        if self._isfocused and not self._ishidden and self._isactive:
            if not self.window_key(evt['press'],evt['code'],evt['key']):
                for child in self._children:
                    child.keyinput(evt)

    def window_key(self, press, keyid, key):
        'key press received'
        # if key is processed and the parent window
        # doesn't want to cascade to child windows then
        # return true, else false to cascade key press.
        return False
    
    def createwnd(self, rect):
        self._surface = pygame.Surface((rect.width, rect.height)).convert()
        self._wndpos = rect.copy()

    def draw(self):
        'window self draw. The window should decide when to draw'
        if self._surface:
            self._surface.fill((255,255,255))
            
    def copy_to(self, wnd):
        'blit window image to surface'
        if not self._ishidden and self._surface:
            for child in reversed(self._children):
                # This could be improved by checking if a window is completely
                # obscured by other windows and avoid drawing.
                child.copy_to(self)

            if self._invert:
                wndcpy = pygame.Surface(self._wndpos.width, self._wndpos.height,0,self._surface)
                wndcpy.fill((255,255,255))
                wndcpy.blit(self._surface,(0,0),None,pygame.BLEND_SUB)
                wnd._surface.blit(wndcpy, self._wndpos)
            else:
                wnd._surface.blit(self._surface, self._wndpos)
        

class PygameApp(PygameWnd):
    def __init__(self, *args, **kwargs):
        PygameWnd.__init__(self,*args, **kwargs)
  
    def do_work(self):
        pass
    
    def touch(self, evt):
        PygameWnd.touch(self,evt)
    
    def keyinput(self, evt):
        PygameWnd.keyinput(self,evt)
    
    def suspend(self):
        'Save state to resume again. Close resources'
        pass
    
    def close(self):
        'Clear state and release resources'
        pass

class PygameButton(PygameWnd):
    def __init__(self, *arg, **kwargs):
        self._font = pygame.font.Font(None, 20)
        self.name = "Button"
        PygameWnd.__init__(self, *arg, **kwargs)
        self.draw()
        
    def createwnd(self,rect):
        PygameWnd.createwnd(self,rect)
        
    def draw(self):
        if self._surface:
            if self._isfocused:
                pygame.draw.rect(self._surface, (225,225,225), self._surface.get_rect(),0)
                pygame.draw.rect(self._surface, (0,120,215), self._surface.get_rect(),3)                
            else:
                pygame.draw.rect(self._surface, (225,225,225), self._surface.get_rect(),0)
                pygame.draw.rect(self._surface, (173,173,173), self._surface.get_rect(),1)

            text = self._font.render(self.name, 1, (10,10,10))
            self._surface.blit(text, text.get_rect(center=self._surface.get_rect().center))

class PygameTextWnd(PygameWnd):
    def __init__(self, *arg, **kwargs):
        PygameWnd.__init__(self, *arg, **kwargs)
        self._text = []
        self.margin = (0,0)
        self.background = (255,255,255)
        self.lineseparation = 5
        
    def add_text(self, text, size, colour, face=None):
        # Support newlines by breaking up text into fragments with newline attribute set
        lines = text.split('\n')
        font = pygame.font.Font(face, size)
        for i, line in enumerate(lines):
            newline = True
            if i == len(lines)-1:
                newline = False
            self._text.append({"text": line, "colour": colour, "fontobj": font, "newline": newline})
                
        self.draw()
        
    def clear_text(self):
        self._text = []
        self.draw()

    def draw(self):
        self._surface.fill(self.background)
        if not self.draw_text():
            print ("DEBUG: Text exceeds available window space")

    def draw_text(self):
        # Drawing cursor. Remember where the next word image starts
        cursor_x = self.margin[0]
        cursor_y = self.margin[1]
        # Line attributes
        max_height = 0
        max_ascent = 0
        max_descent = 0
        # Cache of images for a line of text
        img_line = [] 
        # A fragment is a string of word(s) with a specific font size, colour and style 
        for fragment in self._text:
            fontobj = fragment["fontobj"] # Easy ref for font object
            
            for word in fragment["text"].split(): # Split the text into separate words
                word = word + ' ' # use a space to separate
                (extents_x, extents_y) = fontobj.size(word)

                # Check that the word fits on the line
                adv_cursor_x = cursor_x + extents_x
                if adv_cursor_x + self.margin[0] > self.position.width and len(img_line) > 0:
                    # Reached the extents of the image. This is the end of the line
                    # Blit images
                    self.blit_line(img_line, max_ascent, cursor_y)
                    img_line = [] # remove img line cache for a fresh line
                    # Reset cursor x. Advance cursor y
                    cursor_x = self.margin[0]
                    cursor_y = cursor_y + max_height + self.lineseparation
                    max_height = 0
                    max_ascent = 0
                    max_descent = 0
                    if cursor_y + self.margin[1] > self.position.height:
                        # run out of room. Quit and soft error
                        return False

                # Render the text for this word. Add to list of images for the line
                img_line.append({"img": fontobj.render(word, 1, fragment["colour"]),
                                 "ascent": fontobj.get_ascent()})
                # Advance the x cursor to next work position in the line
                cursor_x = cursor_x + extents_x

                # Recalculate extents for this line
                max_height = max(extents_y, max_height)
                max_ascent = max(fontobj.get_ascent(), max_ascent)
                max_descent = max(fontobj.get_descent(), max_descent)
                    
            if fragment["newline"]:
                # This fragment requires a new line following the text
                # Does this contain text to blit or an empty newline?
                if len(img_line) > 0:
                    self.blit_line(img_line, max_ascent, cursor_y)
                    img_line = []
                    cursor_y = cursor_y + max_height + self.lineseparation
                else:
                    # No text. Assume get_height gives a reasonable height without any specified text
                    cursor_y = cursor_y + fontobj.get_height() + self.lineseparation
                cursor_x = self.margin[0]
                max_height = 0
                max_ascent = 0
                max_descent = 0
                if cursor_y + self.margin[1] > self.position.height:
                    # Cannot fit more lines into window
                    return False

        # Last fragment processed. Print final line
        if len(img_line) > 0:
            self.blit_line(img_line, max_ascent, cursor_y)
            
        # All processed within the window
        return True 

    def blit_line(self, img_line, max_ascent, cursor_y):
        tmp_x = self.margin[0]
        for img in img_line:
            # Different fonts/sizes will have a different baseline. Adjust for this
            height_diff = max_ascent - img["ascent"]
            # Copy to the image surface
            self._surface.blit(img["img"], (tmp_x, cursor_y + height_diff))
            # Advance temp x cursor to draw line
            tmp_x = tmp_x + img["img"].get_width()
