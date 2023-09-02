import pickle
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, ListProperty, StringProperty
)
from kivy.event import EventDispatcher
from kivy.uix.scatter import Scatter
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition

DEBUG = False

class MainMenuScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        app.game_state.load_hidden_objects()
        # Update the button properties here based on the current game state
        button = self.ids['continue_button']
        if self.is_all_found():
            button.text = 'Game Over'
            button.background_color = (0.5, 0.5, 0.5, 1)
            button.disabled = True
        else:
            button.text = 'Spiel fortsetzen'
            button.background_color = (0.494, 1, 0.973, 1)
            button.disabled = False

    def is_all_found(self):
        app = App.get_running_app()
        for level in app.game_state.hidden_objects:
            if not all(obj["found"] for obj in level):
                return False
        return True
    
    def on_leave(self):
        app = App.get_running_app()
        if app.game_state.music:
            app.game_state.music.stop()
    def start_new_game(self):
        app = App.get_running_app()
        app.game_state.game_level = 0  # Setze das Level auf 0 oder einen anderen Anfangswert
        for level in app.game_state.hidden_objects:
            for item in level:
                item["found"] = False
        app.root.current = 'levels'  # Gehe zur Levelauswahl zurück   ChatGPT

class GameScreen(Screen): 
    def on_enter(self):        
        hog = self.ids['game_area']
        status_area = self.ids['status_area']
        app = App.get_running_app()
        prefix = app.game_state.get_prefix()
        app.game_state.set_source_image()        
        our_size = (100, 100) if len(app.game_state.hidden_objects[app.game_state.game_level]) < 6 else (50,50)
        # TODO: make this math better
        status_area.clear_widgets()
        bl = BoxLayout()
        bb = Button()
        bb.text = "Zurück"
        bb.on_press = self.bb_press
        self.sound_effect_2 = SoundLoader.load('click_sound.mp3')
        bl.add_widget(bb)
        status_area.add_widget(bl) 
        last_added = -1
        for item in app.game_state.hidden_objects[app.game_state.game_level]:
            if item["id"] > last_added:
                bl = BoxLayout()
                last_added = item["id"]
                img_filename = f'{prefix}{item["name"]}.png' if not item["found"] else f'{prefix}{item["name"]}_gs.png'
                img = Image(source=img_filename, size=our_size, size_hint=(None,None), keep_ratio=True)
                app.game_state.widget_refs[f"img_{item['name']}"] = img 
                bl.add_widget(img)                
                status_area.add_widget(bl)    
        hog.check_all_found()

    def bb_press(self):
        app = App.get_running_app()
        app.root.current = 'levels'

class OptionsScreen(Screen):
    pass    

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self):
        app = App.get_running_app()
        if app.game_state.music:
            app.game_state.music.stop()  # Stop any currently playing music
            app.game_state.music.unload()  # Unload the current music file
        app.game_state.music = SoundLoader.load('intro_music.piano.mp3')  # Load the intro music
        if app.game_state.music:
            app.game_state.music.play()

class LevelSelecterScreen(Screen):
    def back_button_press(self):
        app = App.get_running_app()
        app.root.current = 'menu'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
      
    def select_level_press(self, selected_level):        
        app = App.get_running_app()        
        app.game_state.game_level = int(selected_level)
        app.root.current = 'game'
        #self.select_level_press = [
            #["position":, "size":, "name":, "level_teich" ??????]
        #]
    
class CustomCarousel(Carousel):

    def on_touch_move(self, touch):
        # Check if the current index is the last slide and if the touch is moving to the left
        if self.index == len(self.slides) - 1 and touch.dx < 0:
            self.parent.manager.current = 'menu'
            return True
        return super(CustomCarousel, self).on_touch_move(touch)

class BoundedScatter(Scatter):

    def on_transform(self, *args):
        if not self.parent:
            return super().on_transform(*args)

        w, h = self.parent.size
        sw, sh = self.children[0].width * self.scale, self.children[0].height * self.scale

        self.x = min(max(self.x, w - sw), 0)
        self.y = min(max(self.y, h - sh), 0)

        return super().on_transform(*args)

class HiddenObjectGame(Widget):
    source_image = StringProperty('image.jpg')  #should this change to .png ?
    app = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app() 
        self.app.game_state.bind(source_image=self.update_image_source)

        self.scatter = BoundedScatter(do_rotation=False, do_translation=True, size_hint=(None, None), scale_min=1)
        self.image = Image(source=self.source_image, size_hint=(None, None), size=(1600, 1200))
        self.sound_effect_1 = SoundLoader.load('correct_sound.mp3') #I added a correct sound B)

        # Ensure scatter size is set to the image's size
        self.scatter.size = self.image.size

        self.scatter.add_widget(self.image)
        self.add_widget(self.scatter)



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
        for obj in self.app.game_state.hidden_objects[self.app.game_state.game_level]:
            if obj["name"] == item_name and obj["found"]:
                return True
        return False
    
    def on_touch_up(self, touch):
        if self.scatter.collide_point(*touch.pos):
            # Convert touch location to Scatter's local coordinates
            local_touch = self.scatter.to_local(*touch.pos, relative=False)
            # Convert local_touch from Scatter's coordinates to the image's current scale and position
            img_x = local_touch[0] - self.image.x
            img_y = local_touch[1] - self.image.y
            
            for obj in self.app.game_state.hidden_objects[self.app.game_state.game_level]:
                x, y = obj["position"]
                w, h = obj["size"]                
                if x < img_x < x + w and y < img_y < y + h:
                    for item in self.app.game_state.hidden_objects[self.app.game_state.game_level]:
                        if item["name"] == obj["name"]:
                            item["found"] = True
                    self.update_object_found(obj["name"])
                    self.app.game_state.save_hidden_objects()
                    #self.flash_screen()
                    break
            
            return super().on_touch_up(touch)
        
    def check_all_found(self):
        all_found = all(obj["found"] for obj in self.app.game_state.hidden_objects[self.app.game_state.game_level])
        game_area = self.parent.parent.ids['game_area']
        if all_found:            
            congratulation_label = Label(
                text="Glückwunsch! Du hast alle Gegenstände Gefunden!",
                font_size='20sp',
                size_hint=(None, None),  # Use None for fixed size
                size=(400, 30),  # Set the size of the label
                pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Position in the center of the screen
            )
            self.app.game_state.widget_refs["congrats_label"] = congratulation_label
            game_area.parent.parent.add_widget(congratulation_label) # add to the game_screen
            # Transition to the outro screen without animation
            self.app.all_levels_complete = self.check_all_levels_complete()  # Check if all levels are complete
            if self.app.all_levels_complete:
                app = App.get_running_app()
                app.root.transition = SlideTransition(direction='left')
                app.root.current = 'outro'
        else:
            cl = self.app.game_state.widget_refs.get("congrats_label")
            if cl:
                game_area.parent.parent.remove_widget(cl)
    
    def check_all_levels_complete(self):
    # Check if all levels are complete (all objects are found in all levels) ChatGPT
        for level in self.app.game_state.hidden_objects:
            if not all(obj["found"] for obj in level):
                return False
        return True

    def update_object_found(self, object_name):
        prefix = self.app.game_state.get_prefix()
        greyscale_img_path = f'{prefix}{object_name}_gs.png'  
        img_widget = self.app.game_state.widget_refs.get(f'img_{object_name}')
        if img_widget:
            img_widget.source = greyscale_img_path
        if self.sound_effect_1:
            self.sound_effect_1.play()
        self.check_all_found()
           
class GameState(EventDispatcher):
    music = None
    game_level = None
    widget_refs = None 
    hidden_objects = []
    source_image = StringProperty('image.jpg')
    def __init__(self, **kwargs):
        
        self.sound_effect_2 = SoundLoader.load('click_sound.mp3')
        self.music = SoundLoader.load('intro_music.piano.mp3')
        self.game_level = 0
        self.widget_refs = {}
        self.hidden_objects = [
            [
                {"position": (485, 98), "size": (38, 10), "name":"brief_teich", "id":0, "found":False},
                {"position": (60, 184), "size": (19, 16), "name":"muenze", "id":1, "found":False},
                {"position": (875, 361), "size": (29, 42), "name":"frosch_teich", "id":2, "found":False},
                {"position": (904, 347), "size": (34, 46), "name":"frosch_teich", "id":2, "found":False},
                {"position": (945, 592), "size": (25, 29), "name":"muschel", "id":3, "found":False},
                {"position": (1568, 486), "size": (30, 29), "name":"blume", "id":4, "found":False},
                {"position": (1533, 1050), "size": (22, 25), "name":"strohhalm", "id":5, "found":False},
                {"position": (1555, 1028), "size": (20, 46), "name":"strohhalm", "id":5, "found":False},
                {"position": (1053, 867), "size": (101, 43), "name":"schildkroete", "id":6, "found":False},
                {"position": (590, 967), "size": (13, 18), "name":"eichhoernchen", "id":7, "found":False},
                {"position": (603, 959), "size": (23, 44), "name":"eichhoernchen", "id":7, "found":False},
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
            ],
            [
                {"position": (59, 602), "size": (84, 67), "name":"kuchen", "id":0, "found":False},
                {"position": (19, 286), "size": (68, 90), "name":"topf", "id":1, "found":False},
                {"position": (532, 338), "size": (37, 47), "name":"erdbeere", "id":2, "found":False},
                {"position": (1326, 476), "size": (69, 139), "name":"zwerg", "id":3, "found":False},
                {"position": (1541, 578), "size": (59, 26), "name":"karotte", "id":4, "found":False},
                {"position": (1224, 1087), "size": (21, 23), "name":"ei", "id":5, "found":False},
                {"position": (365, 1071), "size": (45, 47), "name":"hibiscus", "id":6, "found":False},
                {"position": (826, 153), "size": (52, 31), "name":"kamm", "id":7, "found":False},
                {"position": (508, 968), "size": (65, 57), "name":"waschbaer", "id":8, "found":False},
                {"position": (617, 938), "size": (45, 42), "name":"brot", "id":9, "found":False}
            ]            
        ]  
    def get_prefix(self):
        prefix = ''
        if self.game_level == 0:
            prefix = './images/teich/'
        elif self.game_level == 1:
            prefix = './images/zimmer/'
        elif self.game_level == 2:
            prefix = './images/garten/'
        return prefix
    
    def set_source_image(self):
        if self.game_level == 0:
            self.source_image = "./images/teich/teich.png"
        elif self.game_level == 1:
            self.source_image = "./images/zimmer/zimmer.png"
        elif self.game_level == 2:
            self.source_image = "./images/garten/garten.png"

    def save_hidden_objects(self):
        with open('hidden_objects.pkl', 'wb') as file:
            pickle.dump(self.hidden_objects, file)

    def load_hidden_objects(self):
        try:
            with open('hidden_objects.pkl', 'rb') as file:
                self.hidden_objects = pickle.load(file)
        except FileNotFoundError:
            pass  # Handle missing file if needed #ChatGPT

class OutroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self):
        app = App.get_running_app()
        if app.game_state.music:
            app.game_state.music.stop()  # Stop any currently playing music
            app.game_state.music.unload()  # Unload the current music file
        app.game_state.music = SoundLoader.load('piano_outro.mp3')  # Load the outro music
        if app.game_state.music:
            app.game_state.music.play()   #ChatGPT

class HiddenObjectApp(App):
    game_state = None
    all_levels_complete = False
    def build(self):
        self.game_state = GameState()
        Builder.load_file('layout.kv')
        sm = ScreenManager()
        
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(LevelSelecterScreen(name='levels'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(OptionsScreen(name='options'))
        sm.add_widget(OutroScreen(name='outro'))

        sm.current = 'intro'

        return sm
    
if __name__ == "__main__":
    HiddenObjectApp().run()
