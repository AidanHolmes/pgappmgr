# Toplevel system window implementation. Called by main app class to handle
# inputs and graphics. All other windows are children of this class
#
# Copyright (C) 2019 Aidan Holmes
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

from config import Config
from appmsg import *
import pygame
import psutil
import time
from os.path import join
from launcher import PygameLauncher
from msgqueue import AppPublisher, AppSubscriber, MessageQueue
from pgwindow import PygameWnd

class HeaderBar(AppSubscriber, PygameWnd):
  def __init__(self, mq, *arg, **kwargs):
    PygameWnd.__init__(self, *arg, **kwargs)
    AppSubscriber.__init__(self,mq)

    self.subscribe_message(MSG_SYS_BATTERY, None, self._battevent)
    self.subscribe_message(MSG_SYS_NETWORK, None, self._networkevent)

    self._font = pygame.font.Font(None, Config.statusbar.fontsize)
    self._batteryicon = pygame.image.load(join(Config.system.resourcedir,Config.statusbar.battery_icon))
    self._batteryicon = pygame.transform.scale(self._batteryicon, Config.statusbar.battery_icon_size)
    self._batterycharge = None
    self._batterystatus = 'Full'
    self._networkip = 'Unknown'

    self._blink_t = 0
    self._blink_on = False

    self._memicon = pygame.image.load(join(Config.system.resourcedir,Config.statusbar.memory_icon))
    self._memicon = pygame.transform.scale(self._memicon, Config.statusbar.memory_icon_size)
    self._mem_poll_t = 0
    self._mem_poll = 2 # sec
    self._memory = psutil.virtual_memory()

    self._cpuicon = pygame.image.load(join(Config.system.resourcedir,Config.statusbar.cpu_icon))
    self._cpuicon = pygame.transform.scale(self._cpuicon, Config.statusbar.cpu_icon_size)
    self._cpu = psutil.cpu_percent(None,False)

    self._background = Config.statusbar.background
    self._headerspacing = Config.statusbar.spacing

  def work(self):
    t = time.time()
    redraw = False
    if t > self._blink_t + 1:
      self._blink_t = t
      self._blink_on = not self._blink_on
      redraw = True
    if t > self._mem_poll_t + self._mem_poll:
      self._mem_poll_t = t
      self._memory = psutil.virtual_memory()
      self._cpu = psutil.cpu_percent(None,False)
      redraw = True

    if redraw:
      self.draw()

  def draw(self):
    # Clear background of header
    self._surface.fill((255,255,255))
    screenrect = self._surface.get_rect()

    txtcharge = ''
    if self._batterystatus == 'Charging':
      txtcharge = '+'
    elif self._batterystatus == 'Discharging':
      txtcharge = '-'

    # Draw battery status
    if self._batterycharge is not None:
      text = self._font.render(self._batterycharge + txtcharge + '%', 1, (10,10,10))
      pos = text.get_rect()
      pos.right = self._wndpos.width
      pos.centery = screenrect.centery
      self._surface.blit(text,pos)
      pos = self._batteryicon.get_rect(centery=screenrect.centery, right=pos.left)
      self._surface.blit(self._batteryicon,pos)
    else:
      pos = pygame.Rect(screenrect.right,0,0,screenrect.height)

    # Draw memory utilisation
    text = self._font.render(str(int(self._memory.percent)) + '%', 1, (10,10,10))
    pos = text.get_rect(right = pos.left-self._headerspacing, centery=screenrect.centery)
    self._surface.blit(text,pos)
    pos = self._memicon.get_rect(centery=screenrect.centery, right=pos.left)
    self._surface.blit(self._memicon,pos)

    # Draw CPU utilisation
    text = self._font.render(str(int(self._cpu)) + '%', 1, (10,10,10))
    pos = text.get_rect(right = pos.left-self._headerspacing, centery=screenrect.centery)
    self._surface.blit(text,pos)
    pos = self._cpuicon.get_rect(centery=screenrect.centery, right=pos.left)
    self._surface.blit(self._cpuicon,pos)
    
    text = self._font.render(self._networkip, 1, (10,10,10))
    pos = text.get_rect(left=0, centery=screenrect.centery)
    self._surface.blit(text,pos)

    # Blink activity for debug purpose
    if self._blink_on:
      text = self._font.render('*', 1, (10,10,10))
      pos = text.get_rect(center=screenrect.center)
      self._surface.blit(text,pos)
        
    # Draw the dividing line between header and app body images
    pygame.draw.line(self._surface, (0,0,0),
                     (screenrect.left,screenrect.bottom-1),
                     (screenrect.right, screenrect.bottom-1), 1)
    
  def _battevent(self, msgid, context, message):
    if context == BATT_CAPACITY:
      self._batterycharge = message
    elif context == BATT_STATUS:
      self._batterystatus = message

    self.draw()

  def _networkevent(self,mid,context,message):
    self._networkip = message

    self.draw()
    

class SystemWindow(AppSubscriber, PygameWnd):

  def __init__(self, mq, surface):
    AppSubscriber.__init__(self,mq)
    PygameWnd.__init__(self, screen=surface)

    self.subscribe_message(MSG_TOUCH_INPUT, None, self._touch)
    self.subscribe_message(MSG_KEY_INPUT, None, self._key)

    wndrect = pygame.Rect(0,
                          0,
                          self._wndpos.width,
                          Config.statusbar.height)
    self._headerwnd = HeaderBar(mq, rect=wndrect)
    
    wndrect = pygame.Rect(0,
                          Config.statusbar.height,
                          self._wndpos.width,
                          self._wndpos.height - Config.statusbar.height)
    self._appwnd = PygameLauncher(mq, rect=wndrect)
    self._appwnd.focused = True

    self.add_child(self._headerwnd)
    self.add_child(self._appwnd)
    
    self._headerwnd.draw()

  def _key(self,msgid, context, message):
    self.keyinput(message)

  def _touch(self, msgid, context, message):
    self.touch(message)
  
  def do_work(self):
    # give timeslice to launcher window
    self._appwnd.work()

    # give timeslice to header window
    self._headerwnd.work()

    self._headerwnd.copy_to(self)
    self._appwnd.copy_to(self)
    
