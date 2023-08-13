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
DEBUG = False

class MainMenuScreen(Screen):
    pass

class GameScreen(Screen):
    pass


class IntroSlideshow(BoxLayout):
    #orientation = 'vertical'
    slides = ListProperty(["Slide1.jpg", "Slide2.jpg", "Slide3.jpg"])
    current_slide = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Creating IntroSlideshow") if DEBUG else None
        self.register_event_type('on_slide_end')
        self.bind(current_slide=self.check_slide_end)
        Clock.schedule_once(self.next_slide, 3)

    def check_slide_end(self, instance, value):
        print(f"check_slide_end called with value: {value}") if DEBUG else None
        if value == len(self.slides) - 1:
            print("Scheduling on_slide_end dispatch.") if DEBUG else None
            Clock.schedule_once(lambda dt: self.dispatch('on_slide_end'), 2)
        elif value > len(self.slides) - 1:
            print("Adjusting current_slide to last slide.") if DEBUG else None
            self.current_slide = len(self.slides) - 1

    def on_slide_end(self):
        self.parent.show_menu()

    def skip(self):
        self.current_slide = len(self.slides) - 1

    def next_slide(self, dt):
        if self.current_slide < len(self.slides) - 1:
            self.current_slide += 1
            Clock.schedule_once(self.next_slide, 2)

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("IntroScreen initialized") if DEBUG else None
    
    def on_enter(self):
        print ("PRINTING IDS") if DEBUG else None
        print(self.ids) if DEBUG else None
        self.ids.intro_slideshow.current_slide = 0  # reset slide
        
    def show_menu(self):
        self.manager.current = 'menu'

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
        
        self.scatter = BoundedScatter(do_rotation=False, do_translation=True, size_hint=(None, None), scale_min=1)
        self.image = Image(source="image.jpg", size_hint=(None, None), size=(3840, 2160))
        
        self.scatter.add_widget(self.image)
        self.add_widget(self.scatter)
        self.scatter.size = self.image.size
        self.scatter.center = self.center
        self.game_level = 0
        self.hidden_objects = [
            [
                {"position": (2110, 630), "size": (190, 350), "name":"Umbrella", "id":0, "found":False},
                {"position": (2310, 630), "size": (190, 350), "name":"Umbrella", "id":0, "found":False},
                {"position": (210, 60), "size": (190, 350), "name":"Shoe", "id":1, "found":True}  # Example coordinates and size
            ],
            [
               {"position": (2110, 630), "size": (190, 350), "name":"Mouse"},
               {"position": (210, 60), "size": (190, 350), "name":"Ball"}   # Example coordinates and size
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
        for obj in self.hidden_objects[self.game_level]:
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
    
    def build(self):
        Builder.load_file('layout.kv')
        sm = ScreenManager()
        
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(MainMenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))

        #sm.current = 'intro'

        return sm
    
if __name__ == "__main__":
    HiddenObjectApp().run()
