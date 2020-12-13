import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty, ConfigParserProperty

from kivy.graphics import Color, Rectangle, Point, Line, Ellipse

import time


class MainScatter(Scatter):
    end_point_1_prop = ListProperty([])
    end_point_2_prop = ListProperty([])

    def on_end_point_1_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line":
                child.update_line(1, value)

    def on_end_point_2_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line":
                child.update_line(2, value)


class ChordPoint(Widget):
    name = StringProperty()

    def __init__(self, **kwargs):
        self.size = (50, 50)

        super(ChordPoint, self).__init__(**kwargs)

        with self.canvas:
            Color(1., 0, 0)
            self.outer = Rectangle(size=self.size, pos=self.pos)
            Color(1., 1., 1.)
            self.inner = Rectangle(size=(44, 44), pos=(self.pos[0] + 3, self.pos[1] + 3))

        self.bind(pos=self.update_point)
        
    def update_point(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.pos[0] + 3, self.pos[1] + 3)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        self.center = (touch.x, touch.y)
        if self.name == "end_point_1":
            self.parent.end_point_1_prop = [touch.x, touch.y]
        elif self.name == "end_point_2":
            self.parent.end_point_2_prop = [touch.x, touch.y]
    
    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        return True


class MainLine(Widget):
    name = StringProperty()
    def __init__(self, points, **kwargs):
        super(MainLine, self).__init__(**kwargs)

        with self.canvas:
            Color(1., 0, 0)
            self.outer = Line(points=points, width=2.0)
            Color(1., 1., 1.)
            self.inner = Line(points=points, width=1.0)

    def update_line(self, point, value):
        if point == 1:
            self.outer.points = value + self.outer.points[2:]
            self.inner.points = value + self.outer.points[2:]
        elif point == 2:
            self.outer.points = self.outer.points[:2] + value
            self.inner.points = self.outer.points[:2] + value

        
    def collide_point(self, x, y):
        # Have to make this custom to be in the line
        pass

    # def update_point(self, *args):
    #     self.outer_point.pos = self.pos
    #     self.inner_point.pos = (self.pos[0] + 3, self.pos[1] + 3)

    # def on_touch_down(self, touch):
    #     if self.collide_point(*touch.pos):
    #         touch.grab(self)
    #         return True

    # def on_touch_move(self, touch):
    #     if touch.grab_current is not self:
    #         return
    #     self.pos = (touch.x, touch.y)
    
    # def on_touch_up(self, touch):
    #     if touch.grab_current is not self:
    #         return
    #     touch.ungrab(self)
    #     return True
            



class MainMenuScreen(Screen):
    pass


class CameraScreen(Screen):

    def capture(self):

        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = "IMG_{}.png".format(timestr)
        camera.export_to_png(file_name)

        self.manager.transition.direction = "left"
        self.manager.current = "spline_screen"
        self.manager.get_screen('spline_screen').img_src = file_name


class SplineScreen(Screen):
    img_src = StringProperty("")
    
    def add_chord(self):
        print(self.ids)
        win = self.get_parent_window()
        print(win, win.width / 2, win.height / 2)
        end_point_1_coords = (win.width * 0.25, win.height / 2)
        end_point_2_coords = (win.width * 0.75, win.height / 2)

        main_line = MainLine(name="main_line", points=list(end_point_1_coords+end_point_2_coords))
        end_point_1 = ChordPoint(name="end_point_1", center=end_point_1_coords) # pos_hint={"center_x":win.width * 0.25 / win.width, "center_y": win.height / 2 / win.height})
        end_point_2 = ChordPoint(name="end_point_2", center=end_point_2_coords) # pos_hint={"center_x":win.width * 0.25 / win.width, "center_y": win.height / 2 / win.height}) #

        self.ids.scatter.add_widget(main_line)
        self.ids.scatter.add_widget(end_point_1)
        self.ids.scatter.add_widget(end_point_2)


    # def on_state(self, togglebutton):
    #     if togglebutton.state == "down":
    #         self.add_chord1 = Button(
    #             text="1", 
    #             size_hint=(0.1, 0.1), 
    #             pos_hint={"x": 0, "y": 0.225}, 
    #         )
    #         self.add_chord2 = Button(
    #             text="2", 
    #             size_hint=(0.1, 0.1), 
    #             pos_hint={"x": 0.125, "y": 0.225}
    #         )
    #         self.add_chord3 = Button(
    #             text="3", 
    #             size_hint=(0.1, 0.1), 
    #             pos_hint={"x": 0.25, "y": 0.225}
    #         )
    #         self.add_widget(self.add_chord1)
    #         self.add_widget(self.add_chord2)
    #         self.add_widget(self.add_chord3)
    #     else:
    #         self.remove_widget(self.add_chord1)
    #         self.remove_widget(self.add_chord2)
    #         self.remove_widget(self.add_chord3)
    
class SM(ScreenManager):
    pass


kv = Builder.load_file("SailApp.kv")


class MainApp(App):
    Title = "Sail App"
    icon = "SMlogo.jpg"

    def build(self):
        return kv


if __name__ == '__main__':
    MainApp().run()
