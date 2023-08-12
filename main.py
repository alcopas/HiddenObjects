from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.uix.scatter import Scatter
from kivy.core.window import Window

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
        self.hidden_objects = [
            {"position": (2110, 630), "size": (190, 350)}  # Example coordinates and size

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

    def on_touch_up(self, touch):
        if self.scatter.collide_point(*touch.pos):
            # Convert touch location to Scatter's local coordinates
            local_touch = self.scatter.to_local(*touch.pos, relative=False)

            # Convert local_touch from Scatter's coordinates to the image's current scale and position
            img_x = local_touch[0] - self.image.x
            img_y = local_touch[1] - self.image.y
            
            for obj in self.hidden_objects:
                x, y = obj["position"]
                w, h = obj["size"]
                
                if x < img_x < x + w and y < img_y < y + h:
                    # print("Hidden object found!")
                    # self.hidden_objects.remove(obj)
                    self.flash_screen()
                    break
            
            return super().on_touch_up(touch)

class HiddenObjectApp(App):
    def build(self):
        return HiddenObjectGame()
    
if __name__ == "__main__":
    HiddenObjectApp().run()
