from pgwindow import PygameApp, PygameTextWnd, Clock
import pygame
import time
import feedparser
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
    
AppInfo = {'iconname':'BBC Weather',
           'icon':'app.png',
           'description':'BBC Weather Reader',
           'class':'BBCWeather',
           'framerate':5}

class BBCWeather(PygameApp):
    def __init__(self, wndrect, screen):
        PygameApp.__init__(self, wndrect, screen)
        self._textwnd = PygameTextWnd(rect = wndrect)
        self._textwnd.position = (0, 0, None, None)
        self.add_child(self._textwnd)
        self.focused = True
        self._refresh = Clock(15*60) # 15 min refresh

        # Nottingham 3 day weather
        self._url = "https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/2641170"
        self._feedtitle = "3 Day Summary"
        self.textcolour = (10,10,10)
        
    def update_forecast(self):
        report = feedparser.parse(self._url)
        self._textwnd.clear_text()
        self._textwnd.add_text(self._feedtitle+"\n", 40, self.textcolour)
        for entry in report.entries:
            self._textwnd.add_text(entry.title + "\n\n", 25, self.textcolour)
        self.draw()
            
    def do_work(self):
        if self._refresh.tick():
            # Update feed
            self.update_forecast()

    def draw(self):
        self._textwnd.copy_to(self)
        
    def window_touch(self, x, y, pressed):
        return False

    def window_key(self, press, keyid, key):
        if press and key == 'KEY_RIGHT':
            pass
        return False
