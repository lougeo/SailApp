import kivy
#kivy.require('2.0.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty

from kivy.graphics import Color, Rectangle, Point, Line, Ellipse, Bezier

from os.path import exists, join

import time
import math

if platform == "android":
    # from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    from jnius import JavaException, PythonJavaClass, autoclass, java_method
    request_permissions([
        Permission.CAMERA,
        Permission.READ_EXTERNAL_STORAGE, 
        Permission.WRITE_EXTERNAL_STORAGE,
    ])

def calculate_thickness(EP1, EP2, DP, INT):
    if len(EP1) > 0 and len(EP2) > 0 and len(DP) > 0 and len(INT) > 0:
        depth_len = math.sqrt((DP[0] - INT[0]) ** 2 + (DP[1] - INT[1]) ** 2)
        chord_len = math.sqrt((EP1[0] - EP2[0]) ** 2 + (EP1[1] - EP2[1]) ** 2)
        thickness = round(depth_len / chord_len, 3)
        return str(thickness)
    else:
        return "N/A"
    
def calculate_camber(EP1, EP2, DP, INT):
    if len(EP1) > 0 and len(EP2) > 0 and len(DP) > 0 and len(INT) > 0:
        ep1_len = math.sqrt((EP1[0] - INT[0]) ** 2 + (EP1[1] - INT[1]) ** 2)
        ep2_len = math.sqrt((EP2[0] - INT[0]) ** 2 + (EP2[1] - INT[1]) ** 2)
        chord_len = math.sqrt((EP1[0] - EP2[0]) ** 2 + (EP1[1] - EP2[1]) ** 2)
        if ep1_len <= ep2_len:
            camber = round(ep1_len / chord_len, 3)
        else:
            camber = round(ep2_len / chord_len, 3)
        return str(camber)
    else:
        return "N/A"

class MainScatter(Scatter):
    ###########################    CHORD PIECES    ###########################

    end_point_1_top_prop = ListProperty([])
    end_point_2_top_prop = ListProperty([])
    depth_point_top_prop = ListProperty([])
    depth_point_intercept_top_prop = ListProperty([])
    bezier_point_1_top_prop = ListProperty([])
    bezier_point_2_top_prop = ListProperty([])

    end_point_1_mid_prop = ListProperty([])
    end_point_2_mid_prop = ListProperty([])
    depth_point_mid_prop = ListProperty([])
    depth_point_intercept_mid_prop = ListProperty([])
    bezier_point_1_mid_prop = ListProperty([])
    bezier_point_2_mid_prop = ListProperty([])

    end_point_1_btm_prop = ListProperty([])
    end_point_2_btm_prop = ListProperty([])
    depth_point_btm_prop = ListProperty([])
    depth_point_intercept_btm_prop = ListProperty([])
    bezier_point_1_btm_prop = ListProperty([])
    bezier_point_2_btm_prop = ListProperty([])

    
    ###########################    RESULTS    ###########################

    top_thickness_prop = StringProperty()
    mid_thickness_prop = StringProperty()
    btm_thickness_prop = StringProperty()

    top_camber_prop = StringProperty()
    mid_camber_prop = StringProperty()
    btm_camber_prop = StringProperty()

    ###########################    METHODS    ###########################

    def on_transform(self, *args, **kwargs):
        super().on_transform(*args, **kwargs)
        for child in self.children:
            if hasattr(child, "name") and "point" in child.name:
                win = self.get_parent_window()
                btn_size = (win.width * 0.1 / self.scale, win.width * 0.1 / self.scale)
                # This is super hacky, but it won't update the pos unless the value has changed.
                # Value reset to proper center after widget is touched.
                btn_center = (child.center_x + 0.0001, child.center_y + 0.0001)
                child.size = btn_size
                child.center = btn_center
    # def on_transform_with_touch(self, *args):
    #     print("ON TRANSFORM WITH TOUCH")

    def add_chord(self, btn_name):
        garbage = []

        for child in self.children:
            if hasattr(child, "name") and btn_name in child.name:
                garbage.append(child)

        if len(garbage) > 0:
            for widget in garbage:
                self.remove_widget(widget)
        else:
            # Getting the window and setting initial size
            win = self.get_parent_window()
            scale = self.scale
            point_size = (win.width * 0.1 / scale, win.width * 0.1 / scale)
            # Getting the respective properties
            prop_coords = {}
            for prop in self.properties():
                if btn_name + "_prop" in prop:
                    prop_coords.update({prop.replace("_" + btn_name + "_prop", ""): getattr(self, prop)})
            # Deciding to use default of set coords
            if all(prop_coords.values()):
                # Set coords
                coords = prop_coords
            else:
                # Default coords
                if btn_name == "top":
                    max_height = 0.60
                    min_height = 0.35
                elif btn_name == "mid":
                    max_height = 0.50
                    min_height = 0.25
                elif btn_name == "btm":
                    max_height = 0.40
                    min_height = 0.15
                coords = {
                    "end_point_1": (win.width * 0.25, win.height * max_height),
                    "end_point_2": (win.width * 0.75, win.height * max_height),
                    "depth_point": (win.width * 0.50, win.height * min_height),
                    "depth_point_intercept": (win.width * 0.50, win.height * max_height),
                    "bezier_point_1": (win.width * 0.25, win.height * min_height),
                    "bezier_point_2": (win.width * 0.75, win.height * min_height),
                }
            # Instantiating the chord elements
            main_line = MainLine(name=f"main_line_{btn_name}", points=(coords.get("end_point_1") + coords.get("end_point_2")))
            end_point_1 = EndPoint(name=f"end_point_1_{btn_name}", size=point_size, center=coords.get("end_point_1"))
            end_point_2 = EndPoint(name=f"end_point_2_{btn_name}", size=point_size, center=coords.get("end_point_2"))
            depth_point = DepthPoint(name=f"depth_point_{btn_name}", size=point_size, center=coords.get("depth_point"))
            depth_line = DepthLine(name=f"depth_line_{btn_name}", points=(coords.get("depth_point_intercept") + coords.get("depth_point")))
            bezier_point_1 = BezierPoint(name=f"bezier_point_1_{btn_name}", size=point_size, center=coords.get("bezier_point_1"))
            bezier_point_2 = BezierPoint(name=f"bezier_point_2_{btn_name}", size=point_size, center=coords.get("bezier_point_2"))
            bezier_line_1 = BezierLine(name=f"bezier_line_1_{btn_name}", points=(coords.get("end_point_1") + coords.get("bezier_point_1") + coords.get("depth_point")))
            bezier_line_2 = BezierLine(name=f"bezier_line_2_{btn_name}", points=(coords.get("end_point_2") + coords.get("bezier_point_2") + coords.get("depth_point")))
            # Adding chord elements to scatter
            self.add_widget(depth_line)
            self.add_widget(main_line)
            self.add_widget(end_point_1)
            self.add_widget(end_point_2)
            self.add_widget(depth_point)
            self.add_widget(bezier_point_1)
            self.add_widget(bezier_point_2)
            self.add_widget(bezier_line_1)
            self.add_widget(bezier_line_2)
            # Setting the related scatter properties to initial element position
            if not all(prop_coords.values()):
                if btn_name == "top":
                    self.end_point_1_top_prop = coords.get("end_point_1")
                    self.end_point_2_top_prop = coords.get("end_point_2")
                    self.depth_point_top_prop = coords.get("depth_point")
                    self.depth_point_intercept_top_prop = coords.get("depth_point_intercept")
                    self.bezier_point_1_top_prop = coords.get("bezier_point_1")
                    self.bezier_point_2_top_prop = coords.get("bezier_point_2")
                elif btn_name == "mid":
                    self.end_point_1_mid_prop = coords.get("end_point_1")
                    self.end_point_2_mid_prop = coords.get("end_point_2")
                    self.depth_point_mid_prop = coords.get("depth_point")
                    self.depth_point_intercept_mid_prop = coords.get("depth_point_intercept")
                    self.bezier_point_1_mid_prop = coords.get("bezier_point_1")
                    self.bezier_point_2_mid_prop = coords.get("bezier_point_2")
                elif btn_name == "btm":
                    self.end_point_1_btm_prop = coords.get("end_point_1")
                    self.end_point_2_btm_prop = coords.get("end_point_2")
                    self.depth_point_btm_prop = coords.get("depth_point")
                    self.depth_point_intercept_btm_prop = coords.get("depth_point_intercept")
                    self.bezier_point_1_btm_prop = coords.get("bezier_point_1")
                    self.bezier_point_2_btm_prop = coords.get("bezier_point_2")
        

    ###########################    TOP    ###########################
    def on_end_point_1_top_prop(self, instance, value):
        self.top_thickness_prop = calculate_thickness(
            value, self.end_point_2_top_prop, self.depth_point_top_prop, self.depth_point_intercept_top_prop
        )
        self.top_camber_prop = calculate_camber(
            value, self.end_point_2_top_prop, self.depth_point_top_prop, self.depth_point_intercept_top_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_top":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_top":
                child.update_line(1, "ep", value)

    def on_end_point_2_top_prop(self, instance, value):
        self.top_thickness_prop = calculate_thickness(
            self.end_point_1_top_prop, value, self.depth_point_top_prop, self.depth_point_intercept_top_prop
        )
        self.top_camber_prop = calculate_camber(
            self.end_point_1_top_prop, value, self.depth_point_top_prop, self.depth_point_intercept_top_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_top":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "bezier_line_2_top":
                child.update_line(2, "ep", value)

    def on_depth_point_top_prop(self, instance, value):
        self.top_thickness_prop = calculate_thickness(
            self.end_point_1_top_prop, self.end_point_2_top_prop, value, self.depth_point_intercept_top_prop
        )
        self.top_camber_prop = calculate_camber(
            self.end_point_1_top_prop, self.end_point_2_top_prop, value, self.depth_point_intercept_top_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_point_top":
                child.center = value
            if hasattr(child, "name") and child.name == "depth_line_top":
                child.update_line(self.depth_point_intercept_top_prop, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_top":
                child.update_line(1, "dp", value)
            if hasattr(child, "name") and child.name == "bezier_line_2_top":
                child.update_line(2, "dp", value)
    
    def on_bezier_point_1_top_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_1_top":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_1_top":
                child.update_line(1, "bp", value)
                
    def on_bezier_point_2_top_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_2_top":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_2_top":
                child.update_line(2, "bp", value)


    ###########################    MID    ###########################
    def on_end_point_1_mid_prop(self, instance, value):
        self.mid_thickness_prop = calculate_thickness(
            value, self.end_point_2_mid_prop, self.depth_point_mid_prop, self.depth_point_intercept_mid_prop
        )
        self.mid_camber_prop = calculate_camber(
            value, self.end_point_2_mid_prop, self.depth_point_mid_prop, self.depth_point_intercept_mid_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_mid":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_mid":
                child.update_line(1, "ep", value)

    def on_end_point_2_mid_prop(self, instance, value):
        self.mid_thickness_prop = calculate_thickness(
            self.end_point_1_mid_prop, value, self.depth_point_mid_prop, self.depth_point_intercept_mid_prop
        )
        self.mid_camber_prop = calculate_camber(
            self.end_point_1_mid_prop, value, self.depth_point_mid_prop, self.depth_point_intercept_mid_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_mid":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "bezier_line_2_mid":
                child.update_line(2, "ep", value)

    def on_depth_point_mid_prop(self, instance, value):
        self.mid_thickness_prop = calculate_thickness(
            self.end_point_1_mid_prop, self.end_point_2_mid_prop, value, self.depth_point_intercept_mid_prop
        )
        self.mid_camber_prop = calculate_camber(
            self.end_point_1_mid_prop, self.end_point_2_mid_prop, value, self.depth_point_intercept_mid_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_point_mid":
                child.center = value
            if hasattr(child, "name") and child.name == "depth_line_mid":
                child.update_line(self.depth_point_intercept_mid_prop, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_mid":
                child.update_line(1, "dp", value)
            if hasattr(child, "name") and child.name == "bezier_line_2_mid":
                child.update_line(2, "dp", value)
                
    def on_bezier_point_1_mid_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_1_mid":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_1_mid":
                child.update_line(1, "bp", value)
                
    def on_bezier_point_2_mid_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_2_mid":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_2_mid":
                child.update_line(2, "bp", value)
    
    ###########################    BTM    ###########################
    def on_end_point_1_btm_prop(self, instance, value):
        self.btm_thickness_prop = calculate_thickness(
            value, self.end_point_2_btm_prop, self.depth_point_btm_prop, self.depth_point_intercept_btm_prop
        )
        self.btm_camber_prop = calculate_camber(
            value, self.end_point_2_btm_prop, self.depth_point_btm_prop, self.depth_point_intercept_btm_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_btm":
                child.update_line(1, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_btm":
                child.update_line(1, "ep", value)

    def on_end_point_2_btm_prop(self, instance, value):
        self.btm_thickness_prop = calculate_thickness(
            self.end_point_1_btm_prop, value, self.depth_point_btm_prop, self.depth_point_intercept_btm_prop
        )
        self.btm_camber_prop = calculate_camber(
            self.end_point_1_btm_prop, value, self.depth_point_btm_prop, self.depth_point_intercept_btm_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "main_line_btm":
                child.update_line(2, value)
            if hasattr(child, "name") and child.name == "bezier_line_2_btm":
                child.update_line(2, "ep", value)

    def on_depth_point_btm_prop(self, instance, value):
        self.btm_thickness_prop = calculate_thickness(
            self.end_point_1_btm_prop, self.end_point_2_btm_prop, value, self.depth_point_intercept_btm_prop
        )
        self.btm_camber_prop = calculate_camber(
            self.end_point_1_btm_prop, self.end_point_2_btm_prop, value, self.depth_point_intercept_btm_prop
        )
        for child in self.children:
            if hasattr(child, "name") and child.name == "depth_point_btm":
                child.center = value
            if hasattr(child, "name") and child.name == "depth_line_btm":
                child.update_line(self.depth_point_intercept_btm_prop, value)
            if hasattr(child, "name") and child.name == "bezier_line_1_btm":
                child.update_line(1, "dp", value)
            if hasattr(child, "name") and child.name == "bezier_line_2_btm":
                child.update_line(2, "dp", value)
                
    def on_bezier_point_1_btm_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_1_btm":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_1_btm":
                child.update_line(1, "bp", value)
                
    def on_bezier_point_2_btm_prop(self, instance, value):
        for child in self.children:
            if hasattr(child, "name") and child.name == "bezier_point_2_btm":
                child.center = value
            if hasattr(child, "name") and child.name == "bezier_line_2_btm":
                child.update_line(2, "bp", value)
                
    ###########################    RESULTS    ###########################

    def on_top_thickness_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[2].children[1].children[0].text = value
                
    def on_mid_thickness_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[1].children[1].children[0].text = value
                
    def on_btm_thickness_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[0].children[1].children[0].text = value

    def on_top_camber_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[2].children[0].children[0].text = value
                
    def on_mid_camber_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[1].children[0].children[0].text = value
                
    def on_btm_camber_prop(self, instance, value):
        for child in self.parent.parent.children[0].children:
            if hasattr(child, "name") and "results_card" in child.name:
                child.children[0].children[0].children[0].text = value

###########################################################################################################
#                                              POINTS                                                     #
###########################################################################################################

class EndPoint(Widget):
    name = StringProperty()

    def __init__(self, **kwargs):
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
            self.inner = Rectangle(size=(self.width * 0.9, self.height * 0.9), pos=(self.x + self.width * 0.05, self.y + self.height * 0.05))
        # Bind update point method to pos
        self.bind(pos=self.update_point_pos)
        self.bind(size=self.update_point_size)
        
    def update_point_size(self, *args):
        self.outer.size = self.size
        self.inner.size = (self.width * 0.9, self.height * 0.9)
        
    def update_point_pos(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.x + self.width * 0.05, self.y + self.height * 0.05)

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

        # TRANSLATING DEPTH POINT
        # Retrieve necessary original point data
        if "top" in self.name:
            ep_1 = self.parent.end_point_1_top_prop
            ep_2 = self.parent.end_point_2_top_prop
            dp = self.parent.depth_point_top_prop
            bp_1 = self.parent.bezier_point_1_top_prop
            bp_2 = self.parent.bezier_point_2_top_prop
        elif "mid" in self.name:
            ep_1 = self.parent.end_point_1_mid_prop
            ep_2 = self.parent.end_point_2_mid_prop
            dp = self.parent.depth_point_mid_prop
            bp_1 = self.parent.bezier_point_1_mid_prop
            bp_2 = self.parent.bezier_point_2_mid_prop
        elif "btm" in self.name:
            ep_1 = self.parent.end_point_1_btm_prop
            ep_2 = self.parent.end_point_2_btm_prop
            dp = self.parent.depth_point_btm_prop
            bp_1 = self.parent.bezier_point_1_btm_prop
            bp_2 = self.parent.bezier_point_2_btm_prop
        # Caluclate original slope
        if ep_2[0] == ep_1[0]:
            slope = math.pi / 2
        else:
            slope = (ep_2[1] - ep_1[1]) / (ep_2[0] - ep_1[0])
        # Calculate new intercept point from non moving end point
        if "1" in self.name:
            # Calculate new slope
            if ep_2[0] == x:
                new_slope = math.pi / 2
            else:
                new_slope = (ep_2[1] - y) / (ep_2[0] - x)
            # Calculate delta
            if ep_2[0] == ep_1[0]:
                delta = slope - math.atan(abs(new_slope))
            elif ep_2[0] == x:
                delta = new_slope - math.atan(abs(slope))
            else:
                delta = math.atan(abs((slope - new_slope) / (1 + (slope * new_slope))))
            # Determine sign of delta
            if new_slope < slope:
                delta = - delta
            # Calculate new depth point coords
            new_dp_x = (((dp[0] - ep_2[0]) * math.cos(delta)) - ((dp[1] - ep_2[1]) * math.sin(delta)) + ep_2[0])
            new_dp_y = (((dp[0] - ep_2[0]) * math.sin(delta)) + ((dp[1] - ep_2[1]) * math.cos(delta)) + ep_2[1])
            # Calculate new bezier point coords
            new_bp_1_x = (((bp_1[0] - ep_2[0]) * math.cos(delta)) - ((bp_1[1] - ep_2[1]) * math.sin(delta)) + ep_2[0])
            new_bp_1_y = (((bp_1[0] - ep_2[0]) * math.sin(delta)) + ((bp_1[1] - ep_2[1]) * math.cos(delta)) + ep_2[1])
            # Calculate new bezier point coords
            new_bp_2_x = (((bp_2[0] - ep_2[0]) * math.cos(delta)) - ((bp_2[1] - ep_2[1]) * math.sin(delta)) + ep_2[0])
            new_bp_2_y = (((bp_2[0] - ep_2[0]) * math.sin(delta)) + ((bp_2[1] - ep_2[1]) * math.cos(delta)) + ep_2[1])
            # Calculate new depth point intercept coords
            # Vertical case
            if ep_2[0] == ep_1[0]:
                new_dp_int_x = x
                new_dp_int_y = new_dp_y
            # Horizontal case
            elif new_slope == 0:
                new_dp_int_x = new_dp_x
                new_dp_int_y = y
            else:
                l1 = ep_2[1] - new_slope * ep_2[0]
                l2 = new_dp_y + new_dp_x / new_slope
                new_dp_int_x = new_slope * (l2 - l1) / (new_slope ** 2 + 1)
                new_dp_int_y = new_slope * new_dp_int_x + l1
        elif "2" in self.name:
            # Calculate new slope
            if ep_1[0] == x:
                new_slope = math.pi / 2
            else:
                new_slope = (y - ep_1[1]) / (x - ep_1[0])
            # Calculate delta
            if ep_2[0] == ep_1[0]:
                delta = slope - math.atan(abs(new_slope))
            elif ep_1[0] == x:
                delta = new_slope - math.atan(abs(slope))
            else:
                delta = math.atan(abs((slope - new_slope) / (1 + (slope * new_slope))))
            # Determine sign of delta
            if new_slope < slope:
                delta = - delta
            # Calculate new depth point coords
            new_dp_x = (((dp[0] - ep_1[0]) * math.cos(delta)) - ((dp[1] - ep_1[1]) * math.sin(delta)) + ep_1[0])
            new_dp_y = (((dp[0] - ep_1[0]) * math.sin(delta)) + ((dp[1] - ep_1[1]) * math.cos(delta)) + ep_1[1])
            # Calculate new bezier point 1 coords
            new_bp_1_x = (((bp_1[0] - ep_1[0]) * math.cos(delta)) - ((bp_1[1] - ep_1[1]) * math.sin(delta)) + ep_1[0])
            new_bp_1_y = (((bp_1[0] - ep_1[0]) * math.sin(delta)) + ((bp_1[1] - ep_1[1]) * math.cos(delta)) + ep_1[1])
            # Calculate new bezier point 2 coords
            new_bp_2_x = (((bp_2[0] - ep_1[0]) * math.cos(delta)) - ((bp_2[1] - ep_1[1]) * math.sin(delta)) + ep_1[0])
            new_bp_2_y = (((bp_2[0] - ep_1[0]) * math.sin(delta)) + ((bp_2[1] - ep_1[1]) * math.cos(delta)) + ep_1[1])
            # Calculate new depth point intercept coords
            # Vertical case
            if ep_2[0] == ep_1[0]:
                new_dp_int_x = x
                new_dp_int_y = new_dp_y
            # Horizontal case
            elif new_slope == 0:
                new_dp_int_x = new_dp_x
                new_dp_int_y = y
            else:
                l1 = ep_1[1] - new_slope * ep_1[0]
                l2 = new_dp_y + new_dp_x / new_slope
                new_dp_int_x = new_slope * (l2 - l1) / (new_slope ** 2 + 1)
                new_dp_int_y = new_slope * new_dp_int_x + l1
        else:
            print("Name error")
        
        # Set and propogate new depth point and depth point intercept coords
        if "top" in self.name:
            self.parent.depth_point_intercept_top_prop = [new_dp_int_x, new_dp_int_y]
            self.parent.depth_point_top_prop = [new_dp_x, new_dp_y]
            self.parent.bezier_point_1_top_prop = [new_bp_1_x, new_bp_1_y]
            self.parent.bezier_point_2_top_prop = [new_bp_2_x, new_bp_2_y]
        elif "mid" in self.name:
            self.parent.depth_point_intercept_mid_prop = [new_dp_int_x, new_dp_int_y]
            self.parent.depth_point_mid_prop = [new_dp_x, new_dp_y]
            self.parent.bezier_point_1_mid_prop = [new_bp_1_x, new_bp_1_y]
            self.parent.bezier_point_2_mid_prop = [new_bp_2_x, new_bp_2_y]
        elif "btm" in self.name:
            self.parent.depth_point_intercept_btm_prop = [new_dp_int_x, new_dp_int_y]
            self.parent.depth_point_btm_prop = [new_dp_x, new_dp_y]
            self.parent.bezier_point_1_btm_prop = [new_bp_1_x, new_bp_1_y]
            self.parent.bezier_point_2_btm_prop = [new_bp_2_x, new_bp_2_y]

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

        # Set widget position
        self.center = (x, y)
    
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
            self.inner = Rectangle(size=(self.width * 0.9, self.height * 0.9), pos=(self.x + self.width * 0.05, self.y + self.height * 0.05))
        # Bind update point method to pos
        self.bind(pos=self.update_point_pos)
        self.bind(size=self.update_point_size)
        
    def update_point_size(self, *args):
        self.outer.size = self.size
        self.inner.size = (self.width * 0.9, self.height * 0.9)
        
    def update_point_pos(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.x + self.width * 0.05, self.y + self.height * 0.05)

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
            x = touch.x
            D = [A[0], touch.y]
            int_x = A[0]
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
            y = touch.y
            D = [touch.x, A[1]]
            int_y = A[1]
            # Side bounds
            if touch.x <= min(A[0], B[0]):
                x = int_x = min(A[0], B[0])
            elif touch.x >= max(A[0], B[0]):
                x = int_x = max(A[0], B[0])
            else:
                x = int_x = touch.x
        
        # Normal Case
        else:
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

                x, y = D_MAX_INV

            else:
                # End Bounds
                int_x, int_y = D
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


class BezierPoint(Widget):
    name = StringProperty()

    def __init__(self, **kwargs):
        # Set size before calling super
        self.size = (50, 50)
        # Call super
        super(BezierPoint, self).__init__(**kwargs)
        with self.canvas:
            if "top" in self.name:
                Color(1., 0, 0)
            elif "mid" in self.name:
                Color(0, 1., 0)
            elif "btm" in self.name:
                Color(0, 0, 1.)
            self.outer = Rectangle(size=self.size, pos=self.pos)
            Color(1., 1., 1.)
            self.inner = Rectangle(size=(self.width * 0.9, self.height * 0.9), pos=(self.x + self.width * 0.05, self.y + self.height * 0.05))
        # Bind update point method to pos
        self.bind(pos=self.update_point_pos)
        self.bind(size=self.update_point_size)
        
    def update_point_size(self, *args):
        self.outer.size = self.size
        self.inner.size = (self.width * 0.9, self.height * 0.9)
        
    def update_point_pos(self, *args):
        self.outer.pos = self.pos
        self.inner.pos = (self.x + self.width * 0.05, self.y + self.height * 0.05)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        
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
        if "1" in self.name:
            if "top" in self.name:
                self.parent.bezier_point_1_top_prop = [x, y]
            elif "mid" in self.name:
                self.parent.bezier_point_1_mid_prop = [x, y]
            elif "btm" in self.name:
                self.parent.bezier_point_1_btm_prop = [x, y]
        elif "2" in self.name:
            if "top" in self.name:
                self.parent.bezier_point_2_top_prop = [x, y]
            elif "mid" in self.name:
                self.parent.bezier_point_2_mid_prop = [x, y]
            elif "btm" in self.name:
                self.parent.bezier_point_2_btm_prop = [x, y]
        else:
            print("Name Error")
            
        # Set widget position
        self.center = (x, y)
    
    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        return True

###########################################################################################################
#                                              LINES                                                      #
###########################################################################################################

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

class DepthLine(MainLine):
    def update_line(self, intercept, value):
        self.inner.points = intercept + value
        self.outer.points = intercept + value

class BezierLine(Widget):
    name = StringProperty()
    
    def __init__(self, points, **kwargs):
        super(BezierLine, self).__init__(**kwargs)
        with self.canvas:
            if "top" in self.name:
                Color(1., 0, 0)
            elif "mid" in self.name:
                Color(0, 1., 0)
            elif "btm" in self.name:
                Color(0, 0, 1.)
            self.bline = Bezier(points=points)
            
    def update_line(self, point, control, value):
        if point == 1:
            if control == "bp":
                self.bline.points = self.bline.points[:2] + value + self.bline.points[4:]
            elif control == "ep":
                self.bline.points = value + self.bline.points[2:]
            elif control == "dp":
                self.bline.points = self.bline.points[:4] + value
        elif point == 2:
            if control == "bp":
                self.bline.points = self.bline.points[:2] + value + self.bline.points[4:]
            elif control == "ep":
                self.bline.points = self.bline.points[:4] + value
            elif control == "dp":
                self.bline.points = value + self.bline.points[2:]

######################################################################################################
#                                             RESULTS WIDGET                                         #
######################################################################################################

class ResultsCard(GridLayout):
    name = StringProperty()
    full_screen = BooleanProperty(defaultvalue=False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            if not self.full_screen:
                self.pos_hint = {"x":0, "y":0.2}
                self.size_hint = (0.8, 0.8)
                self.full_screen = True
            else:
                self.pos_hint = {"x":0, "y":0.5}
                self.size_hint = (0.3, 0.5)
                self.full_screen = False


######################################################################################################
#                                              SCREENS                                               #
######################################################################################################


class MainMenuScreen(Screen):

    def open_camera(self):
        if platform == "android":
            from android.storage import primary_external_storage_path
            from android_camera import AndroidCamera

            timestr = time.strftime("%Y%m%d_%H%M%S")
            file_name = f"IMG_{timestr}.png"
            primary_dir = primary_external_storage_path()
            full_path = join(primary_dir, file_name)

            AndroidCamera().take_picture(self.camera_callback)
        else:
            self.manager.transition.direction = "left"
            self.manager.current = "camera_screen"
        
    def camera_callback(self, filepath):
        if(exists(filepath)):
            print("PICTURE SAVED")
            print(filepath)

            self.manager.transition.direction = "left"
            self.manager.current = "spline_screen"
            self.manager.get_screen('spline_screen').img_src = filepath
        else:
            print("PICTURE NOT SAVED")
            print(filepath)

class CameraScreen(Screen):
    """
    Only used in dev environment.
    """
    def capture(self):
        timestr = time.strftime("%Y%m%d_%H%M%S")
        file_name = f"IMG_{timestr}.png"
        camera = self.ids['camera']
        camera.export_to_png(file_name)
        self.manager.transition.direction = "left"
        self.manager.current = "spline_screen"
        self.manager.get_screen('spline_screen').img_src = file_name

class FileChooserScreen(Screen):
    
    def load(self, path, selection):
        file_name = selection[0]
        print(file_name)
        self.manager.transition.direction = "left"
        self.manager.current = "spline_screen"
        self.manager.get_screen('spline_screen').img_src = file_name

class SplineScreen(Screen):
    img_src = StringProperty("")

    
    def show_results(self):
        garbage = []
        for child in self.children[0].children:
            if hasattr(child, "name") and child.name == "results_card":
                garbage.append(child)
        if len(garbage) > 0:
            for widget in garbage:
                self.ids.spline_screen_util_btns.remove_widget(widget)
        else:
            # Instantiate and add results widget
            results_card = ResultsCard(name="results_card")
            results_card.ids.thickness_top_label.text = self.ids.scatter.top_thickness_prop
            results_card.ids.camber_top_label.text = self.ids.scatter.top_camber_prop
            results_card.ids.thickness_mid_label.text = self.ids.scatter.mid_thickness_prop
            results_card.ids.camber_mid_label.text = self.ids.scatter.mid_camber_prop
            results_card.ids.thickness_btm_label.text = self.ids.scatter.btm_thickness_prop
            results_card.ids.camber_btm_label.text = self.ids.scatter.btm_camber_prop

            self.ids.spline_screen_util_btns.add_widget(results_card)

class SM(ScreenManager):
    pass

kv = Builder.load_file("SailApp.kv")

class MainApp(App):
    Title = "Sail App"
    # icon = "SMlogo.jpg"

    def build(self):
        Window.bind(on_keyboard=self.key_input)
        return kv

    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            # Makes it so it doesn't crash, but need to figure out how to change screen
            return True
        else:
            return False
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass

if __name__ == '__main__':
    MainApp().run()