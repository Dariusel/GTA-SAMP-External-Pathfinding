import sys, os

# Import pygame without import message
class Null():
    def write(self, a):
        pass

nullwrite = Null()
oldstdout = sys.stdout
sys.stdout = nullwrite
from pygame import mixer
sys.stdout = oldstdout

def play_sound(sound_path: str):
    mixer.init()

    mixer.music.load(sound_path)
    mixer.music.play()