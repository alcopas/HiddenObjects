from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty
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
from kivy.graphics.instructions import ColorMatrix

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
        if self.game_level == 0:
            hog.source_image = "Teich.png"
        elif self.game_level == 1:
            hog.source_image = "Zimmer.png"
        elif self.game_level == 2:
            hog.source_image = "Garten.png"

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
    scatter = ObjectProperty(None)
    image = ObjectProperty(None)
    source_image = StringProperty('image.jpg')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

        
        
        self.hidden_objects = [
            [
                {"position": (485, 98), "size": (38, 10), "name":"brief_teich", "id":0, "found":False},
                {"position": (60, 184), "size": (19, 16), "name":"münze", "id":1, "found":False},
                {"position": (875, 361), "size": (29, 42), "name":"frosch_teich", "id":2, "found":False},
                {"position": (904, 347), "size": (34, 46), "name":"frosch_teich", "id":2, "found":False},
                {"position": (945, 592), "size": (25, 29), "name":"muschel", "id":3, "found":False},
                {"position": (1568, 486), "size": (30, 29), "name":"blume", "id":4, "found":False},
                {"position": (1533, 1050), "size": (22, 25), "name":"strohhalm", "id":5, "found":False},
                {"position": (1555, 1028), "size": (20, 46), "name":"strohhalm", "id":5, "found":False},
                {"position": (1053, 867), "size": (101, 43), "name":"schildkröte", "id":6, "found":False},
                {"position": (590, 967), "size": (13, 18), "name":"eichhörnchen", "id":7, "found":False},
                {"position": (603, 959), "size": (23, 44), "name":"eichhörnchen", "id":7, "found":False},
                {"position": (988, 457), "size": (38, 51), "name":"hamster_m", "id":8, "found":False}
                {"position": (1046, 480), "size": (37, 56), "name":"hamster_w", "id":9, "found":False}

            
            ],
            [
               {"position": (448, 783), "size": (26, 42), "name":"frosch", "id":0, "found":False},
                {"position": (567, 644), "size": (23, 7), "name":"brief", "id":1, "found":False},
                {"position": (7, 586), "size": (80, 37), "name":"rose", "id":2, "found":False},
                {"position": (423, 1139), "size": (29, 17), "name":"pinguin", "id":3, "found":False},
                {"position": (399, 1181), "size": (24, 17), "name":"kette", "id":4, "found":False},
                {"position": (23, 225), "size": (45, 48), "name":"hase", "id":5, "found":False},
                {"position": (323, 395), "size": (21, 25), "name":"cupcake", "id":6, "found":False},
                {"position": (522, 526), "size": (24, 17), "name":"socke", "id":7, "found":False},
                {"position": (533, 543), "size": (17, 18), "name":"socke", "id":7, "found":False},
                {"position": (1131, 0), "size": (64, 54), "name":"kerze", "id":8, "found":False},
                {"position": (1576, 933), "size": (24, 29), "name":"regenbogenball", "id":9, "found":False},
                {"position": (1046, 1010), "size": (24, 22), "name":"katze", "id":10, "found":False}
            ]
            
            ]        
        

    def flash_screen(self, color=(0, 1, 0, 1)):  # green
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
            
            for obj in self.hidden_objects[GameScreen.game_level]:
                x, y = obj["position"]
                w, h = obj["size"]
                item_name = obj["name"]
                
                
                if x < img_x < x + w and y < img_y < y + h:
                    # print("Hidden object found!")
                    # self.hidden_objects.remove(obj)
                    self.flash_screen()
                    break
            
            return super().on_touch_up(touch)
        class HiddenObjectGame(Widget):
    # ... (other code)

    def is_item_found(self, item_name):
        for obj in self.hidden_objects[self.game_level]:
            if obj["name"] == item_name:
                return obj["found"]
        return False

    def toggle_item(self, item_name):
        for obj in self.hidden_objects[self.game_level]:
            if obj["name"] == item_name:
                obj["found"] = not obj["found"]
                break


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
