import random
import threading

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.core.audio import SoundLoader

from kivy.uix.image import Image

from kivy.graphics import Line

LEN_RANGE = 10000
WIN_COUNT = 1000000
PERSONS = ["ZXOLAD", "PECHENKA"]

Window.clearcolor = (0.22, 0.17, 0.3, 1.0)
Window.size = (400, 600)

LabelBase.register(name='pixel', fn_regular='assets/font.ttf')


class AnimatingImage(Image):
    def __init__(self, atlas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = 0.0
        self.rate = 0.2
        self.frame = 1
        self.atlas = atlas
        self.update(0.3)
    def update(self, dt):
        self.time += dt
        if (self.time > self.rate):
            self.time -= self.rate
            self.source = f"atlas://{self.atlas}/frame" + str(self.frame)
            self.frame = self.frame + 1
            if (self.frame > 2):
                self.frame = 1

class MainApp(App):
    def __init__(self):
        super().__init__()
        self.magic_thread = None
        self.magic_run = False

        self.counters = {}
        self.view_units = {}        # elems for viewing
        self.view_counters = {}     #

        for person in PERSONS:
            self.counters[person] = 0
            self.view_counters[person] = Label(text=str(0), font_name="pixel")
            # self.view_units[person] = Label(
            #     text="-->",
            #     pos_hint={
            #         'center_x': .1,
            #         'center_y': .5 + PERSONS.index(person) * 0.04
            #     }
            # )
            self.view_units[person] = AnimatingImage(
                atlas=f"assets/turtles/t_{(random.randint(1, len(PERSONS)))}",
                size_hint=(.22, .1),
                pos_hint={
                        'center_x': .1,
                        'center_y': .5 + PERSONS.index(person) * 0.1
                    }
            )

        self.start_button = Button(
            size_hint=(.32, .12),
            pos_hint={'center_x': .5, 'center_y': .2},
            background_normal='assets/start_button_1.png',
            background_down='assets/start_button_2.png'
        )

        sound = SoundLoader.load('assets/theme.mp3')
        if sound:
            sound.loop = True
            sound.volume = 0.3
            sound.play()

    def build(self):
        self.main_box = FloatLayout()

        self.start_button.bind(on_press=self.start_magic)

        names_box = BoxLayout(orientation='horizontal', pos_hint={'center_x': .5, 'center_y': .38})
        counter_box = BoxLayout(orientation='horizontal', pos_hint={'center_x': .5, 'center_y': .33})

        finish = Image(
            source='assets/finish.png',
            size_hint=(.92, .92),
            pos_hint={'center_x': .84, 'center_y': .55},
            )
        self.main_box.add_widget(finish)

        for person in PERSONS:
            names_box.add_widget(Label(text=person, font_name="pixel"))
            counter_box.add_widget(self.view_counters[person])
            self.main_box.add_widget(self.view_units[person])

        self.main_box.add_widget(names_box)
        self.main_box.add_widget(counter_box)
        self.main_box.add_widget(self.start_button)
        #main_box.add_widget(finish)

        #self.main_box.add_widget(Image(source="assets/win.png"))

        return self.main_box

    def start_magic(self, button):
        if not self.magic_run:
            self.magic_thread = threading.Thread(target=self.make_magic, daemon=True)
            self.magic_thread.start()

            button.background_normal = 'assets/start_button_2.png'
            button.background_down = 'assets/start_button_1.png'
        else:
            self.magic_run = False
            button.background_normal = 'assets/start_button_1.png'
            button.background_down = 'assets/start_button_2.png'

    def make_magic(self):
        for person in PERSONS:
            Clock.schedule_interval(self.view_units[person].update, 1.0 / 60.0)
        # .source = f"assets/t_{(PERSONS.index(person) % (len(PERSONS) - 1)) + 1}_1.png"

        self.magic_run = True
        max_len = len(PERSONS) * LEN_RANGE

        while self.magic_run:
            num = random.randint(0, max_len) / LEN_RANGE
            if num.is_integer():
                self.counters[PERSONS[int(num - 1)]] += random.randint(0, 5) #5 if PERSONS[int(num - 1)] == "ZXOLAD" else
            else:
                self.counters[PERSONS[int(num)]] += random.randint(0, 5)

            for person in PERSONS:
                self.view_counters[person].text = str(self.counters[person])
                y = self.view_units[person].pos_hint['center_y']

                self.view_units[person].pos_hint = {
                    'center_x': self.counters[person]/WIN_COUNT,
                    'center_y': y
                }

                if self.counters[person] >= WIN_COUNT:
                    self.magic_run = False
                    break

        for person in PERSONS:
            self.counters[person] = 0
            Clock.unschedule(self.view_units[person].update)


if __name__ == '__main__':
    app = MainApp()
    app.run()

