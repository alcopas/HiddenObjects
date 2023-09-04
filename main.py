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
from kivy.uix.scrollview import ScrollView


DEBUG = False

class MainMenuScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        app.game_state.load_hidden_objects()
        #if app.game_state.music and app.game_state.music_enabled and not app.game_state.music.state == 'play':
            #app.game_state.music.play()
          
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
        #app.game_state.set_level_music(app.game_state.level_music_tracks[0])
        for level in app.game_state.hidden_objects:
            for item in level:
                item["found"] = False
        app.root.current = 'levels'  # Gehe zur Levelauswahl zurück   ChatGPT

class GameScreen(Screen): 
    def on_enter(self):        
        hog = self.ids['game_area']
        status_area = self.ids['status_area']
        app = App.get_running_app()
        if app.game_state.music and app.game_state.music_enabled and not app.game_state.music.state == 'play':
            app.game_state.music.play()
        if app.game_state.music and not app.game_state.music_enabled:
            app.game_state.music.stop()
        prefix = app.game_state.get_prefix()
        app.game_state.set_source_image()        
        our_size = (150, 150)

        status_area.clear_widgets()

        # Adding the back button directly to the status_area
        bb = Button(text="Zurück", size_hint_y=None, height=100)
        bb.on_press = self.bb_press
        status_area.add_widget(bb)

        # Create ScrollView and VBox for scrollable content
        scroll_view = ScrollView(do_scroll_x=False, size_hint_y=0.85) # Make it occupy the rest of the status_area height
        vbox = BoxLayout(orientation='vertical', size_hint_y=None)
        vbox.bind(minimum_height=vbox.setter('height'))  # Adjust height dynamically

        last_added = -1
        for item in app.game_state.hidden_objects[app.game_state.game_level]:
            if item["id"] > last_added:
                bl = BoxLayout(size_hint_y=None, height=our_size[1])
                last_added = item["id"]
                img_filename = f'{prefix}{item["name"]}.png' if not item["found"] else f'{prefix}{item["name"]}_gs.png'
                img = Image(source=img_filename, size=our_size, size_hint=(None,None), keep_ratio=True)
                app.game_state.widget_refs[f"img_{item['name']}"] = img 
                bl.add_widget(img)                
                vbox.add_widget(bl)   

        # Add vbox to scroll_view and add scroll_view to status_area
        scroll_view.add_widget(vbox)
        status_area.add_widget(scroll_view)

        hog.check_all_found()

    def bb_press(self):
        app = App.get_running_app()
        app.root.current = 'levels'

    def on_leave(self):
        app = App.get_running_app()
        if app.game_state.music:
            app.game_state.music.stop()

class OptionsScreen(Screen):
    def toggle_music(self):
        app = App.get_running_app()
        app.game_state.music_enabled = not app.game_state.music_enabled
        self.update_music_button_text()
        app.game_state.save_hidden_objects()


    def toggle_soundfx(self):
        app = App.get_running_app()
        app.game_state.soundfx_enabled = not app.game_state.soundfx_enabled
        self.update_soundfx_button_text()
        app.game_state.save_hidden_objects()

    def update_music_button_text(self):
        app = App.get_running_app()
        music_button = self.ids['music_button']
        if app.game_state.music_enabled:
            music_button.text = 'Musik: On'
        else:
            music_button.text = 'Musik: Off'

    def update_soundfx_button_text(self):
        app = App.get_running_app()
        soundfx_button = self.ids['soundfx_button']
        if app.game_state.soundfx_enabled:
            soundfx_button.text = 'Sound-Effekte: On'
        else:
            soundfx_button.text = 'Sound-Effekte: Off'

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self):
        app = App.get_running_app()
        app.game_state.load_hidden_objects()
        if app.game_state.music:
            app.game_state.music.stop()  # Stop any currently playing music
            app.game_state.music.unload()  # Unload the current music file
        app.game_state.music = SoundLoader.load('intro_music.piano.mp3')  # Load the intro music
        if app.game_state.music and app.game_state.music_enabled:
            app.game_state.music.play()

class LevelSelecterScreen(Screen):
    rectangle_colors = ListProperty([]) 
    def back_button_press(self):
        app = App.get_running_app()
        app.root.current = 'menu'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_rectangle_colors() 

    def on_enter(self):
        self.update_rectangle_colors()

    def update_rectangle_colors(self):
        app = App.get_running_app()
        rectangle_colors = []
        for level in range(len(app.game_state.hidden_objects)):
            # test is all items are found
            if all(obj["found"] for obj in app.game_state.hidden_objects[level]): #this should only be true if all items are found
                rectangle_colors.append([1, 0, 0, 0.2])  # Red color for incomplete levels
            else:
                rectangle_colors.append([1, 1, 1, 0.4])  # grau für unkomplete Levels
        self.rectangle_colors = rectangle_colors  # Update the property
      
    def select_level_press(self, selected_level):        
        app = App.get_running_app()        
        app.game_state.game_level = int(selected_level)
        app.root.current = 'game'
    
    def on_house_click(self, instance, touch):
        # Get the touch coordinates
        touch_x, touch_y = touch.pos

        # Define the coordinates and sizes of clickable areas
        area1_x, area1_y, area1_width, area1_height = 1041, 0, 293, 231 #Teich, Level 0
        area2_x, area2_y, area2_width, area2_height = 63, 368, 200, 472 #Zimmer, Level 1
        area3_x, area3_y, area3_width, area3_height = 853, 0, 129, 290 #Garten, Level 2

        app = App.get_running_app()

        # Check if the touch coordinates are within the first area
        if area1_x <= touch_x <= area1_x + area1_width and area1_y <= touch_y <= area1_y + area1_height:
            app.game_state.game_level = 0 
            app.root.current = 'game'

        if area2_x <= touch_x <= area2_x + area2_width and area2_y <= touch_y <= area2_y + area2_height:
            app.game_state.game_level = 1 
            app.root.current = 'game'

        if area3_x <= touch_x <= area3_x + area3_width and area3_y <= touch_y <= area3_y + area3_height:
            app.game_state.game_level = 2 
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
        if not self.parent:
            return super().on_transform(*args)

        w, h = self.parent.size
        sw, sh = self.children[0].width * self.scale, self.children[0].height * self.scale

        self.x = min(max(self.x, w - sw), 0)
        self.y = min(max(self.y, h - sh), 0)

        return super().on_transform(*args)

class HiddenObjectGame(Widget):
    source_image = StringProperty('image.jpg')  # Use the image format you have, either .jpg or .png
    app = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app() 
        self.app.game_state.bind(source_image=self.update_image_source)

        # Set scale to 1.5 for initial zoom-in
        self.scatter = BoundedScatter(do_rotation=False, do_translation=True, size_hint=(None, None), scale=1.3, scale_min=1)
        self.image = Image(source=self.source_image, size_hint=(None, None), size=(1600, 1200))
        self.sound_effect_1 = SoundLoader.load('correct_sound.mp3')  # Great! You added a sound effect!

        # Ensure scatter size is set to the image's size
        self.scatter.size = self.image.size

        self.scatter.add_widget(self.image)
        self.add_widget(self.scatter)

    def update_image_source(self, instance, value):
        self.image.source = value

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
            if self.app.game_state.soundfx_enabled: self.sound_effect_1.play()
        self.check_all_found()
           
class GameState(EventDispatcher):
    music = None
    game_level = None
    widget_refs = None 
    hidden_objects = []
    source_image = StringProperty('image.jpg')
    soundfx_enabled = True
    music_enabled = True

    level_music_tracks = [
        'teich.mp3',  # Music for level 0
        'level2_music.mp3',  # Music for level 1
        'level3_music.mp3',  # Music for level 2
    ]

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
        if self.game_level >= 0 and self.game_level < len(self.level_music_tracks):
            if self.game_level == 0:
                self.source_image = "./images/teich/teich.png"
            elif self.game_level == 1:
                self.source_image = "./images/zimmer/zimmer.png"
            elif self.game_level == 2:
                self.source_image = "./images/garten/garten.png"

            music_track = self.level_music_tracks[self.game_level]
            self.set_level_music(music_track)
        #else:
            #self.source_image = 'image.jpg' ChatGPT hat forgeschlagen, braucht man das???
    
    def set_level_music(self, music_track):
        # Stop any currently playing music
        if self.music:
            self.music.stop()
            self.music.unload()
       
       # Load and play the music for the current level
        self.music = SoundLoader.load(music_track)
        if self.music and self.music_enabled:
            self.music.play()

    def save_hidden_objects(self):
        data_to_save = {
            "hidden_objects": self.hidden_objects,
            "soundfx_enabled": self.soundfx_enabled,
            "music_enabled": self.music_enabled,
        }

        with open('hidden_objects.pkl', 'wb') as file:
            pickle.dump(data_to_save, file)

    def load_hidden_objects(self):
        try:
            with open('hidden_objects.pkl', 'rb') as file:
                loaded_data = pickle.load(file)
                if isinstance(loaded_data, dict):  # Checking if loaded data is a dictionary
                    self.hidden_objects = loaded_data.get("hidden_objects", [])
                    self.soundfx_enabled = loaded_data.get("soundfx_enabled", True)
                    self.music_enabled = loaded_data.get("music_enabled", True)
                else:
                    # You can add logging here to inform about an old save format
                    pass
        except (FileNotFoundError, pickle.UnpicklingError, AttributeError, EOFError):
            # Handle multiple exceptions: 
            # - FileNotFoundError for missing file
            # - UnpicklingError for issues during unpickling
            # - AttributeError for missing attributes in loaded data
            # - EOFError for an unexpectedly empty file
            pass

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
            if app.game_state.music_enabled: app.game_state.music.play()   #ChatGPT

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

