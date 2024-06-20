import win32api
import win32con
from threading import Thread


def key_down(key: int):
    win32api.keybd_event(key, 0, 0, 0)

def key_up(key: int):
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

def release_keys():
    # Release all pressed keys
    key_up(ord('W'))
    key_up(ord('S'))
    key_up(ord('A'))
    key_up(ord('D'))