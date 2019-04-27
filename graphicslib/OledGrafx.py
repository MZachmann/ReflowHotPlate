# These are high level display routines so don't have to call the same
# methods repeatedly in other applications

from graphicslib import OledDisplay
from graphicslib import FontArial11
from graphicslib import FontDrawer

# a simple hook to disable this module if there's no display connected
_HasGraphics = True

# the high level graphics class
class OledGrafx :
    def __init__(self, isFor1306) :
        if OledGrafx.HasGrafx :
            self.oled = OledDisplay.OledDisplay(isFor1306)
            self.oled.init_display()
            self.oled.clear()
            self.oled.display()
            self.font11 = FontArial11.FontArial11()
            self.drawer = FontDrawer.FontDrawer(self.font11, self.oled)

    @property
    def HasGrafx() :
        global _HasGraphics
        return _HasGraphics

    def PrintStrings(self, first=None, second=None, third=None, fourth=None) :
        if not OledGrafx.HasGrafx :
            return
        if(first is not None) :
            self.oled.clear()
            self.drawer.DrawString(first, 0, 0)
        if(second is not None) :
            self.drawer.DrawString(second, 0, self.font11.height)
        if(third is not None) :
            self.drawer.DrawString(third, 0, self.font11.height*2)
        if(fourth is not None) :
            self.drawer.DrawString(fourth, 0, self.font11.height*3)
        self.oled.display()


