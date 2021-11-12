import random
import win32api
import win32con
import winsound
import time
import ctypes
import json
import sys
import threading
import values

from overlay_label import OverlayLabel


LMB = win32con.VK_LBUTTON
F4 = win32con.VK_F4
F10 = win32con.VK_F10

def beep():
    winsound.Beep(2000, 100)


def beep_exit():
    winsound.Beep(500, 500)

X = 0
Y = 1
gun_type = 0
gun_name = 'None'
timer = 0
smooth = 5
sensitivity = 0
fov = 0
lost = 0
milliseconds = 0 

with open('settings') as json_file:
    data = json.load(json_file)
    sensitivity = float(data['sensitivity'])
    fov = float(data['fov'])




def change_gun() -> None:
    global gun_type
    global timer

    KeyMin = 0

    AssaultRifleKeyValue = win32api.GetKeyState(0x61)
    if AssaultRifleKeyValue < KeyMin:
        gun_type = values.AssaultRifle
        gun_name = 'Assault Rifle'
        timer = values.AssaultRifleTime
    LR300RifleKeyValue = win32api.GetKeyState(0x62)
    if LR300RifleKeyValue < KeyMin:
        gun_type = values.LR300Rifle
        gun_name = 'LR300'
        timer = values.LR300RifleTime
    ThompsonKeyValue = win32api.GetKeyState(0x63)
    if ThompsonKeyValue < KeyMin:
        gun_type = values.Thompson
        gun_name = 'Thompson'
        timer = values.ThompsonTime
    MP5KeyValue = win32api.GetKeyState(0x64)
    if MP5KeyValue < KeyMin:
        gun_type = values.MP5
        gun_name = 'MP5A4'
        timer = values.MP5Time
    CustomSMGKeyValue = win32api.GetKeyState(0x65)
    if CustomSMGKeyValue < KeyMin:
        gun_type = values.CustomSMG
        gun_name = 'CustomSMG'
        timer = values.CustomSMGTime
    M249KeyValue = win32api.GetKeyState(0x66)
    if M249KeyValue < KeyMin:
        gun_type = values.M249
        gun_name = 'M249'
        timer=values.M249Time
    return

def menu():
    global gun_type
    global timer

    count = 1

    for gun in values.guns:
        print(f'Numpad Key: {count} - {gun}')
        count += 1
    print("0 - None")
    print("\nMade By Dylan")

def iskeypressed():
    LeftClickKeyValue = win32api.GetKeyState(0x01)
    RightClickKeyValue = win32api.GetKeyState(0x02)
    if LeftClickKeyValue < 0 and RightClickKeyValue < 0:
        return True

def ispressednumbar():
    global gun_type

    NumpadZeroKeyValue = win32api.GetKeyState(0x60)
    if NumpadZeroKeyValue < 0:
        gun_type = 0
        loop()
    
def move(x,y):
    global lost
    ctypes.windll.user32.mouse_event(0x0001, x, y, 0,0)
    milliseconds2 = int(round(time.time() * 1000))
    lost +=(milliseconds2-milliseconds)/1000

def mousedown(gun_type,timer):
    global milliseconds
    global lost

    lost = 0

    for recoilValues in gun_type:
        realx=((recoilValues[X]/2)/sensitivity)
        realy=((recoilValues[Y]/2)/sensitivity)

        milliseconds = int(round(time.time() * 1000))

        for x in range(8):
            movex=(realx/8)
            movey=(realy/8)
            move(int(movex),int(movey))
            time.sleep((timer/8))

        millissecond2 = int(round(time.time() * 1000))

        # print((milliseconds2-milliseconds)/1000)
        lost = 0
        # lostx=(realx%4)
        # losty=(realy%4)
        # move(int(lostx),int(losty))
        if not iskeypressed():
            return
        # time.sleep(timer-lost)
        lost = 0

def construct_overlay(overlay, weapons_list, current_weapon_index, no_recoil):
    recoil_data = "ON" if gun_type != 0 else "OFF"
    bg_data = "#acffac" if gun_type != 0 else "#ffacac"
    recoil_string = "NoRecoil: {}".format(recoil_data)
    weapon_string = "Weapon: {}".format(gun_name)
    length = max(len(recoil_string), len(weapon_string))
    overlay_string = "{}\n{}".format(recoil_string.ljust(length), weapon_string.ljust(length))
    overlay.set_bg(bg_data)
    overlay.set_text(overlay_string)

def loop():
    overlay = OverlayLabel()
    overlay.set_size(20, 2)
    while gun_type == 0:
        change_gun()
    while gun_type != 0:
        gun_type()
        ispressednumbar()
        if iskeypressed():
            mousedown(gun_type,timer)
menu()
loop()
