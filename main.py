from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty
)
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.cache import Cache
from kivy.core.audio import SoundLoader
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
from kivy.uix.checkbox import CheckBox

DEBUG = False

class MainMenuScreen(Screen):

    def on_leave(self):
        app = App.get_running_app()
        if app.music:
            app.music.stop()

class GameScreen(Screen):
    game_level = NumericProperty(0)
    def on_enter(self):
        hog = self.ids['game_area']
        last_added = -1
        for item in hog.hidden_objects[self.game_level]:
            if item["id"] > last_added:
                bl = BoxLayout()
                last_added = item["id"]
                bl.id = last_added
                img = Image(source=f'{item["name"]}.png', size=(100,100), size_hint=(None,None), keep_ratio=True)
                bl.add_widget(img)
                cb = CheckBox()
                cb.active = hog.is_item_found(item["name"])
                cb.readonly = True
                bl.add_widget(cb)
                status_area = self.ids['status_area']
                status_area.add_widget(bl)    

class OptionsScreen(Screen):
    pass    

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self):
        app = App.get_running_app()
        if app.music:
            app.music.play()

class LevelSelecterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def select_level_press(self, selected_level):        
        app = App.get_running_app()        
        GameScreen.game_level = int(selected_level)
        app.root.current = 'game'

class CustomCarousel(Carousel):

    def on_touch_move(self, touch):
        # Check if the current index is the last slide and if the touch is moving to the left
        if self.index == len(self.slides) - 1 and touch.dx < 0:
            self.parent.manager.current = 'menu'
            return True
        return super(CustomCarousel, self).on_touch_move(touch)

class BoundedScatter(Scatter):
    def on_transform(self, *args):
        # Ensure the child (the image) is entirely inside the window.
        # Get window size
        w, h = Window.size

        # Get the size of the image inside the Scatter after applying the scale
        iw, ih = self.children[0].size
        sw, sh = iw * self.scale, ih * self.scale  # Scaled width and height
        
        # Adjust x position
        if self.x > 0:
            self.x = 0
        if self.right < w:
            self.x = w - sw

        # Adjust y position
        if self.y > 0:
            self.y = 0
        if self.top < h:
            self.y = h - sh

        super().on_transform(*args)

class HiddenObjectGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
        self.scatter = BoundedScatter(do_rotation=False, do_translation=True, size_hint=(None, None), scale_min=1)
        self.image = Image(source="image.jpg", size_hint=(None, None), size=(3840, 2160))
        
        self.scatter.add_widget(self.image)
        self.add_widget(self.scatter)
        self.scatter.size = self.image.size
        self.scatter.center = self.center
        self.hidden_objects = [
            [
                {"position": (2110, 630), "size": (190, 350), "name":"umbrella", "id":0, "found":False},
                {"position": (2310, 630), "size": (190, 350), "name":"Umbrella", "id":0, "found":False},
                {"position": (210, 60), "size": (190, 350), "name":"shoe", "id":1, "found":True}  # Example coordinates and size
            ],
            [
               {"position": (2110, 630), "size": (190, 350), "name":"mouse", "id":0, "found":False},
               {"position": (210, 60), "size": (190, 350), "name":"ball", "id":1, "found":False}   # Example coordinates and size
            ]
            
            ]        
        

    def flash_screen(self, color=(1, 0, 0, 1)):  # Default color is red
        flash = Widget(size=Window.size, pos=(0, 0))
        
        with flash.canvas:
            Color(*color)
            self.flash_rect = Rectangle(size=flash.size, pos=flash.pos)

        self.add_widget(flash)

        anim = Animation(opacity=0, duration=0.3)  # Flash for 0.3 seconds

        def remove_flash(*args):
            self.remove_widget(flash)

        anim.bind(on_complete=remove_flash)
        anim.start(flash)
    
    def is_item_found(self, item_name):
        for obj in self.hidden_objects[GameScreen.game_level]:
            if obj["name"] == item_name and obj["found"]:
                return True
        return False
    
    def on_touch_up(self, touch):
        if self.scatter.collide_point(*touch.pos):
            # Convert touch location to Scatter's local coordinates
            local_touch = self.scatter.to_local(*touch.pos, relative=False)

            app = App.get_running_app()
            # Convert local_touch from Scatter's coordinates to the image's current scale and position
            img_x = local_touch[0] - self.image.x
            img_y = local_touch[1] - self.image.y
            
            for obj in self.hidden_objects[self.game_level]:
                x, y = obj["position"]
                w, h = obj["size"]
                item_name = obj["name"]
                
                
                if x < img_x < x + w and y < img_y < y + h:
                    # print("Hidden object found!")
                    # self.hidden_objects.remove(obj)
                    self.flash_screen()
                    break
            
            return super().on_touch_up(touch)

class HiddenObjectApp(App):
    
    music = None
    def build(self):
        self.music = SoundLoader.load('intro_music.mp3')
        Builder.load_file('layout.kv')
        sm = ScreenManager()
        
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(LevelSelecterScreen(name='levels'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(OptionsScreen(name='options'))

        sm.current = 'intro'

        return sm
    
if __name__ == "__main__":
    HiddenObjectApp().run()
