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

DEBUG = False

class MainMenuScreen(Screen):

    def on_leave(self):
        app = App.get_running_app()
        if app.music:
            app.music.stop()

class GameScreen(Screen):
    game_level = NumericProperty(0)
    widget_refs = {} 
    def on_enter(self):
        hog = self.ids['game_area']
        hog.game_screen = self 
        prefix = ''
        if self.game_level == 0:
            #pass
            hog.source_image = "./images/teich/teich.png"
            prefix = './images/teich/'
        elif self.game_level == 1:
            hog.source_image = "./images/zimmer/zimmer.png"
            prefix = './images/zimmer/'
        elif self.game_level == 2:
            hog.source_image = "garten.png"
        last_added = -1
        our_size = (100, 100) if len(hog.hidden_objects[self.game_level]) < 6 else (50,50)
        # TODO: make this math better
        for item in hog.hidden_objects[self.game_level]:
            if item["id"] > last_added:
                bl = BoxLayout()
                last_added = item["id"]
                bl.id = last_added
                img = Image(source=f'{prefix}{item["name"]}.png', size=our_size, size_hint=(None,None), keep_ratio=True)
                self.widget_refs[f"img_{item['name']}"] = img 
                bl.add_widget(img)
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
        game_screen = app.root.get_screen('game')  # Get the instance of GameScreen
        game_screen.game_level = int(selected_level)
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
    source_image = StringProperty('image.jpg')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(source_image=self.update_image_source)
        self.app = App.get_running_app()        
        self.scatter = BoundedScatter(do_rotation=False, do_translation=True, size_hint=(None, None), scale_min=1)
        self.image = Image(source=self.source_image, size_hint=(None, None), size=(1600, 1200))
        self.game_screen = None
        self.scatter.add_widget(self.image)
        self.add_widget(self.scatter)
        self.scatter.size = self.image.size
        self.scatter.center = self.center
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
                {"position": (988, 457), "size": (38, 51), "name":"hamster_m", "id":8, "found":False},
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
        
    def update_image_source(self, instance, value):
        self.image.source = value

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
        for obj in self.hidden_objects[self.game_screen.game_level]:
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
            
            for obj in self.hidden_objects[self.game_screen.game_level]:
                x, y = obj["position"]
                w, h = obj["size"]
                item_name = obj["name"]             
                
                if x < img_x < x + w and y < img_y < y + h:
                    # print("Hidden object found!")
                    # self.hidden_objects.remove(obj)
                    obj["found"] = True
                    self.update_object_found(obj["name"])
                    #self.flash_screen()
                    break
            
            return super().on_touch_up(touch)

    def update_object_found(self, object_name):
        prefix = ''
        if self.game_screen.game_level == 0:
            prefix = './images/teich/'
        elif self.game_screen.game_level == 1:
            prefix = './images/zimmer/'
        elif self.game_screen.game_level == 2:
            prefix = './images/something/'

        greyscale_img_path = f'{prefix}{object_name}_gs.png'
        

        img_widget = self.game_screen.widget_refs.get(f'img_{object_name}')
        if img_widget:
            img_widget.source = greyscale_img_path

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
