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
    end_point_1_top_prop = ListProperty([])
    end_point_2_top_prop = ListProperty([])
    depth_point_top_prop = ListProperty([])
    depth_point_intercept_top_prop = ListProperty([])

    end_point_1_mid_prop = ListProperty([])
    end_point_2_mid_prop = ListProperty([])
    depth_point_mid_prop = ListProperty([])
    depth_point_intercept_mid_prop = ListProperty([])

    end_point_1_btm_prop = ListProperty([])
    end_point_2_btm_prop = ListProperty([])
    depth_point_btm_prop = ListProperty([])
    depth_point_intercept_btm_prop = ListProperty([])

    def on_end_point_1_top_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_top":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "depth_point_top":
                child.translate_point(1, value)

    def on_end_point_2_top_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_top":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "depth_point_top":
                child.translate_point(2, value)

    def on_depth_point_top_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_line_top":
                child.update_line(self.depth_point_intercept_top_prop, value)

    def on_end_point_1_mid_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_mid":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "depth_point_mid":
                child.translate_point(1, value)

    def on_end_point_2_mid_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_mid":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "depth_point_mid":
                child.translate_point(2, value)

    def on_depth_point_mid_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_line_mid":
                child.update_line(self.depth_point_intercept_mid_prop, value)
                
    def on_end_point_1_btm_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_btm":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "depth_point_btm":
                child.translate_point(1, value)

    def on_end_point_2_btm_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_btm":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "depth_point_btm":
                child.translate_point(2, value)

    def on_depth_point_btm_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_line_btm":
                child.update_line(self.depth_point_intercept_btm_prop, value)


class EndPoint(Widget):
    name = StringProperty()

    def __init__(self, **kwargs):
        # Set size before calling super
        self.size = (50, 50)
        # Call super
        super(EndPoint, self).__init__(**kwargs)
        # Draw shapes
        with self.canvas:
            if "top" in self.name:
                Color(1., 0, 0)
            elif "mid" in self.name:
                Color(0, 1., 0)
            elif "btm" in self.name:
                Color(0, 0, 1.)
            self.outer = Rectangle(size=self.size, pos=self.pos)
            Color(1., 1., 1.)
            self.inner = Rectangle(size=(44, 44), pos=(self.pos[0] + 3, self.pos[1] + 3))
        # Bind update point method to pos
        self.bind(pos=self.update_point)
        
    def update_point(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.pos[0] + 3, self.pos[1] + 3)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        # Checks we are touching the right thing
        if touch.grab_current is not self:
            return
        
        # Keeps coords within the scatter image bounds
        p_x, p_y = self.parent.size
        if touch.x < 0:
            x = 0
        elif touch.x > p_x:
            x = p_x
        else:
            x = touch.x
        
        if touch.y < 0:
            y = 0
        elif touch.y > p_y:
            y = p_y
        else:
            y = touch.y

        # Set widget position
        self.center = (x, y)

        # Sets and propogates changed coords
        # Try and rethink this - boil it down to a one liner.
        if self.name == "end_point_1_top":
            self.parent.end_point_1_top_prop = [x, y]
        elif self.name == "end_point_2_top":
            self.parent.end_point_2_top_prop = [x, y]
        elif self.name == "end_point_1_mid":
            self.parent.end_point_1_mid_prop = [x, y]
        elif self.name == "end_point_2_mid":
            self.parent.end_point_2_mid_prop = [x, y]
        elif self.name == "end_point_1_btm":
            self.parent.end_point_1_btm_prop = [x, y]
        elif self.name == "end_point_2_btm":
            self.parent.end_point_2_btm_prop = [x, y]
    
    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        return True


class DepthPoint(Widget):
    name = StringProperty()

    def __init__(self, **kwargs):
        # Set size before calling super
        self.size = (50, 50)
        # Call super
        super(DepthPoint, self).__init__(**kwargs)
        # Draw shapes
        with self.canvas:
            if "top" in self.name:
                Color(1., 0, 0)
            elif "mid" in self.name:
                Color(0, 1., 0)
            elif "btm" in self.name:
                Color(0, 0, 1.)                
            self.outer = Rectangle(size=self.size, pos=self.pos)
            Color(1., 1., 1.)
            self.inner = Rectangle(size=(44, 44), pos=(self.pos[0] + 3, self.pos[1] + 3))
        # Bind update point method to pos
        self.bind(pos=self.update_point)
        
    def update_point(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.pos[0] + 3, self.pos[1] + 3)

    def translate_point(self, *args):
        print('in translate')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        
        # Try and rethink this - boil it down to a one liner.
        if self.name == "depth_point_top":
            A = self.parent.end_point_1_top_prop
            B = self.parent.end_point_2_top_prop
        elif self.name == "depth_point_mid":
            A = self.parent.end_point_1_mid_prop
            B = self.parent.end_point_2_mid_prop          
        elif self.name == "depth_point_btm":
            A = self.parent.end_point_1_btm_prop
            B = self.parent.end_point_2_btm_prop

        # Vertical Case
        if A[0] == B[0]:
            # Intercept point
            D = [A[0], touch.y]
            int_x = A[0]
            # End bounds
            if A[1] <= B[1]:
                if touch.x <= D[0]:
                    x = D[0]
                elif touch.x >= D[0] + (B[1] - A[1]):
                    x = D[0] + (B[1] - A[1])
                else:
                    x = touch.x
            elif A[1] > B[1]:
                if touch.x >= D[0]:
                    x = D[0]
                elif touch.x <= D[0] - (A[1] - B[1]):
                    D[0] - (A[1] - B[1])
                else:
                    x = touch.x
            # Side bounds
            if touch.y < min(A[1], B[1]):
                y = int_y = min(A[1], B[1])
            elif touch.y > max(A[1], B[1]):
                y = int_y = max(A[1], b[1])
            else:
                y = int_y = touch.y

        # Horizontal Case
        elif A[1] == B[1]:
            # Intercept point
            D = [touch.x, A[1]]
            int_y = A[1]
            # Side bounds
            if touch.x <= min(A[0], B[0]):
                x = int_x = min(A[0], B[0])
            elif touch.x >= max(A[0], B[0]):
                x = int_x = max(A[0], B[0])
            else:
                x = int_x = touch.x
            # End bounds
            if A[0] <= B[0]:
                if touch.y >= D[1]:
                    y = D[1]
                elif touch.y <= D[1] - (B[0] - A[0]):
                    y = D[1] - (B[0] - A[0])
                else:
                    y = touch.y
            elif A[0] > B[0]:
                if touch.y <= D[1]:
                    y = D[1]
                elif touch.y >= D[1] + (A[0] - B[0]):
                    y = D[1] + (A[0] - B[0])
                else:
                    y = touch.y
                
        # Normal Case
        else:
            # Length of chord - use to set up other end bound
            # length = ((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2) ** (1/2)
            # Calculating perpendicular intercept to main line
            slope = (B[1] - A[1]) / (B[0] - A[0])
            inv_slope = -1 / slope
            l1 = A[1] - slope * A[0]
            l2 = touch.y + touch.x / slope
            D = []
            D.append(slope * (l2 - l1) / (slope ** 2 + 1))
            D.append(slope * D[0] + l1)
            # Variables
            min_x = min(A[0], B[0])
            min_y = min(A[1], B[1])
            max_x = max(A[0], B[0])
            max_y = max(A[1], B[1])

            
            # Side Bounds
            if D[0] <= min_x:
                if min_x in A:
                    min_y = A[1]
                else:
                    min_y = B[1]
                int_x, int_y = min_x, min_y
                # Calculating perpendicular intercept to inverse bottom line
                inv_bottom_1 = min_y - inv_slope * min_x
                inv_bottom_2 = touch.y + touch.x / inv_slope
                D_MIN_INV = []
                D_MIN_INV.append(inv_slope * (inv_bottom_2 - inv_bottom_1) / (inv_slope ** 2 + 1))
                D_MIN_INV.append(inv_slope * D_MIN_INV[0] + inv_bottom_1)

                if D_MIN_INV[1] >= min_y:
                    x = min_x
                    y = min_y
                else:
                    x, y = D_MIN_INV

            elif D[0] >= max_x:
                if max_x in A:
                    max_y = A[1]
                else:
                    max_y = B[1]
                int_x, int_y = max_x, max_y
                # Calculating perpendicular intercept to inverse top line
                inv_top_1 = max_y - inv_slope * max_x
                inv_top_2 = touch.y + touch.x / inv_slope
                D_MAX_INV = []
                D_MAX_INV.append(inv_slope * (inv_top_2 - inv_top_1) / (inv_slope ** 2 + 1))
                D_MAX_INV.append(inv_slope * D_MAX_INV[0] + inv_top_1)

                if D_MAX_INV[1] >= max_y:
                    x = max_x
                    y = max_y
                else:
                    x, y = D_MAX_INV

            else:
                # End Bounds
                int_x, int_y = D
                if touch.y > D[1]:
                    if min_y in A:
                        min_x = A[0]
                    else:
                        min_x = B[0]
                    x, y = D
                # Inside of the bounds
                else:
                    x = touch.x
                    y = touch.y

        # Keeps coords within the scatter image bounds
        p_x, p_y = self.parent.size
        if x < 0:
            x = 0
        elif x > p_x:
            x = p_x
        else:
            x = x
        
        if y < 0:
            y = 0
        elif y > p_y:
            y = p_y
        else:
            y = y

        # Set related depth point scatter property
        # Try and rethink this - boil it down to a one liner.
        if self.name == "depth_point_top":
            self.parent.depth_point_intercept_top_prop = [int_x, int_y]
            self.parent.depth_point_top_prop = [x, y]
        elif self.name == "depth_point_mid":
            self.parent.depth_point_intercept_mid_prop = [int_x, int_y]
            self.parent.depth_point_mid_prop = [x, y]
        elif self.name == "depth_point_btm":
            self.parent.depth_point_intercept_btm_prop = [int_x, int_y]
            self.parent.depth_point_btm_prop = [x, y]
            
        # Set widget position
        self.center = (x, y)
    
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
            if "top" in self.name:
                Color(1., 0, 0)
            elif "mid" in self.name:
                Color(0, 1., 0)
            elif "btm" in self.name:
                Color(0, 0, 1.)
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

    # def on_touch_down(self, touch):

    # def on_touch_move(self, touch):
    
    # def on_touch_up(self, touch):

class DepthLine(MainLine):
    def update_line(self, intercept, value):
        self.inner.points = intercept + value
        self.outer.points = intercept + value


######################################################################################################
#                                              Screens                                               #
######################################################################################################


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
    
    def add_chord(self, btn_name):
        print(self.children[1].children[0].children)
        print(btn_name)

        garbage = []

        for child in self.children[1].children[0].children:
            if hasattr(child, "name") and btn_name in child.name:
                garbage.append(child)

        if len(garbage) > 0:
            for widget in garbage:
                self.ids.scatter.remove_widget(widget)
        else:
            # Getting arbitrary starting point for coord
            win = self.get_parent_window()
            end_point_1_coords = (win.width * 0.25, win.height * 0.50)
            end_point_2_coords = (win.width * 0.75, win.height * 0.50)
            depth_point_coords = (win.width * 0.50, win.height * 0.25)
            depth_point_intercept_coords = (win.width * 0.50, win.height * 0.50)
            # Instantiating the chord elements
            depth_line = DepthLine(name=f"depth_line_{btn_name}", points=list(depth_point_intercept_coords + depth_point_coords))
            main_line = MainLine(name=f"main_line_{btn_name}", points=list(end_point_1_coords + end_point_2_coords))
            end_point_1 = EndPoint(name=f"end_point_1_{btn_name}", center=end_point_1_coords) # pos_hint={"center_x":win.width * 0.25 / win.width, "center_y": win.height / 2 / win.height})
            end_point_2 = EndPoint(name=f"end_point_2_{btn_name}", center=end_point_2_coords) # pos_hint={"center_x":win.width * 0.25 / win.width, "center_y": win.height / 2 / win.height}) #
            depth_point = DepthPoint(name=f"depth_point_{btn_name}", center=depth_point_coords)
            # Adding chord elements to scatter
            self.ids.scatter.add_widget(depth_line)
            self.ids.scatter.add_widget(main_line)
            self.ids.scatter.add_widget(end_point_1)
            self.ids.scatter.add_widget(end_point_2)
            self.ids.scatter.add_widget(depth_point)
            # Setting the related scatter properties to initial element position
            if btn_name == "top":
                self.ids.scatter.end_point_1_top_prop = end_point_1_coords
                self.ids.scatter.end_point_2_top_prop = end_point_2_coords
                self.ids.scatter.depth_point_top_prop = depth_point_coords
                self.ids.scatter.depth_point_intercept_top_prop = depth_point_coords
            elif btn_name == "mid":
                self.ids.scatter.end_point_1_mid_prop = end_point_1_coords
                self.ids.scatter.end_point_2_mid_prop = end_point_2_coords
                self.ids.scatter.depth_point_mid_prop = depth_point_coords
                self.ids.scatter.depth_point_intercept_mid_prop = depth_point_coords
            elif btn_name == "btm":
                self.ids.scatter.end_point_1_btm_prop = end_point_1_coords
                self.ids.scatter.end_point_2_btm_prop = end_point_2_coords
                self.ids.scatter.depth_point_btm_prop = depth_point_coords
                self.ids.scatter.depth_point_intercept_btm_prop = depth_point_coords


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