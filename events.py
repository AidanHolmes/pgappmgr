# A simplified events handling class for touch screen and keyboard inputs
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

import evdev
import select

class DeviceEvents(object):
  def __init__(self):
    # Register all devices for input
    self._devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

    self._got_x = False
    self._got_y = False
    # Cache touch inputs
    self._input = {'type':'touch','press':0,'x':0,'y':0}
    
  def get_event(self):
    evt = None
    # Loop and process first input found. First devices
    # will get priority until all messages exhausted
    for device in self._devices:
      try:
        evt = device.read_one()
        if evt is not None and (evt.type == evdev.ecodes.EV_ABS or evt.type == evdev.ecodes.EV_KEY):
          # event received which is key or abs input
          break
      except BlockingIOError:
        pass

    return self._filter_event(evt)

  def get_blocking_event(self,timeout=None):
    devices = {dev.fd: dev for dev in self._devices}
    while True:
      r, w, x = select.select(devices, [], [], timeout)
      if len(r) <=0:
        return None
      evt = devices[r[0]].read_one()
      
      if evt is not None and (evt.type == evdev.ecodes.EV_ABS or evt.type == evdev.ecodes.EV_KEY):
        # event received which is key or abs input
        break

    return self._filter_event(evt)

  def _filter_event(self, evt):
    # Check if any devices have input
    if evt is None:
      return None
    
    if evt.type == evdev.ecodes.EV_KEY and evt.code == evdev.ecodes.BTN_TOUCH:
      if self._input['press'] != evt.value:
        self._input['press'] = evt.value
        return self._input.copy()
    elif evt.type == evdev.ecodes.EV_ABS:
      if evt.code == evdev.ecodes.ABS_X:
        self._input['x'] = evt.value
        self._got_x = True
      elif evt.code == evdev.ecodes.ABS_Y:
        self._input['y'] = evt.value
        self._got_y = True
    elif evt.type == evdev.ecodes.EV_KEY:
      input = {}
      input['type'] = 'key'
      input['code'] = evt.code
      input['press'] = evt.value
      try:
        input['key'] = evdev.ecodes.KEY[evt.code]
      except KeyError:
        input['key'] = ''
      return input

    if self._got_y and self._got_x:
      self._got_y = False
      self._got_x = False
      self._input['type'] = 'touch'
      self._input['press'] = 1
      return self._input.copy()

    return None        
