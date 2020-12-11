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
from kivy.properties import ObjectProperty, StringProperty

from kivy.graphics import Color, Rectangle, Point, Line, Ellipse

import time


class ChordPoint(Widget):

    point = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ChordPoint, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        print(touch.pos)
        if self.collide_point(touch.x, touch.y):
            print(touch)
            return True
        # with self.canvas:
        #     Color(1, 1, 0)
        #     d = 30.
        #     Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

class AddChord(Widget):
    def on_touch_down(self, touch):
        win = self.get_parent_window()
        ud = touch.ud
        ud['group'] = g = str(touch.uid)
        pointsize = 5

        with self.canvas:
            Color(0, 1, 1, mode='hsv', group=g)
            ud['lines'] = [
                Rectangle(pos=(touch.x, 0), size=(1, win.height), group=g),
                Rectangle(pos=(0, touch.y), size=(win.width, 1), group=g),
                Point(points=(touch.x, touch.y), source='particle.png',
                      pointsize=pointsize, group=g)]

        ud['label'] = Label(size_hint=(None, None))
        self.update_touch_label(ud['label'], touch)
        self.add_widget(ud['label'])
        touch.grab(self)
        return True

    def update_touch_label(self, label, touch):
        label.text = 'ID: %s\nPos: (%d, %d)\nClass: %s' % (
            touch.id, touch.x, touch.y, touch.__class__.__name__)
        label.texture_update()
        label.pos = touch.pos
        label.size = label.texture_size[0] + 20, label.texture_size[1] + 20


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
        
    def on_state(self, togglebutton):
        if togglebutton.state == "down":
            self.add_chord1 = Button(
                text="1", 
                size_hint=(0.1, 0.1), 
                pos_hint={"x": 0, "y": 0.225}, 
            )
            self.add_chord2 = Button(
                text="2", 
                size_hint=(0.1, 0.1), 
                pos_hint={"x": 0.125, "y": 0.225}
            )
            self.add_chord3 = Button(
                text="3", 
                size_hint=(0.1, 0.1), 
                pos_hint={"x": 0.25, "y": 0.225}
            )
            self.add_widget(self.add_chord1)
            self.add_widget(self.add_chord2)
            self.add_widget(self.add_chord3)
        else:
            self.remove_widget(self.add_chord1)
            self.remove_widget(self.add_chord2)
            self.remove_widget(self.add_chord3)
    
    def add_chord(self):
        print(self.ids)
        win = self.get_parent_window()
        print(win, win.width / 2, win.height / 2)
        point = ChordPoint(size=(50, 50), pos=(win.width / 2, win.height / 2))#pos_hint={"x": 0.5, "y": 0.5}) #
        point.canvas.add(Color(1., 1., 1.))
        point.canvas.add(Ellipse(size=(50, 50), pos=point.pos))#pos=(win.width / 2, win.height / 2))) # ##pos_hint={"x": 0.5, "y": 0.5}))
        self.ids.scatter.add_widget(point)


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
