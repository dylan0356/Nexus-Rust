import random
import win32api
import win32con
import winsound
import time
import ctypes
import ctypes.wintypes
import json
import sys
import threading
import values
import subprocess

from pynput import keyboard
from overlay_label import OverlayLabel

hwid = str(str(subprocess.check_output('wmic csproduct get uuid')).strip().replace(r"\r", "").split(r"\n")[1].strip())

print(hwid)

X = 0
Y = 1

def printSlow(text):
    for char in text:
        print(char, end="")
        sys.stdout.flush()
        time.sleep(.4)

#printSlow("Loading\n")

gun_type = 0
gun_name = 'None'
name_of_sight = 'Iron'
timer = 0
smoothing = 5
sensitivity = 0
fov = 0
lost = 0
start_time = 0 
smooth = 8
maxRandom = 0.08
minRandom = 0.01
movementsPerShot = 4
attachment = 0
currentwep = 0
scope = 0
barrel = 0
randomizer = 0
playerfov = 90
playersens = 0.3
enabled = True

LMB = win32con.VK_LBUTTON
RMB = win32con.VK_RBUTTON
F4 = win32con.VK_F4
F10 = win32con.VK_F10
ENTER = win32con.VK_RETURN

overlay = OverlayLabel()
overlay.set_size(30, 4)

def start():
    overlay = OverlayLabel()
    overlay.set_size(30, 3)

with open('settings') as json_file:
    data = json.load(json_file)
    sensitivity = float(data['sensitivity'])
    fov = float(data['fov'])

def beep():
    winsound.Beep(2000, 100)

def beep_exit():
    winsound.Beep(500, 500)

def is_lmb_pressed():
    return win32api.GetKeyState(LMB) < 0

def give_time():
    return int(round(time.time() * 1000))

def Randomize(val:float, perc:int):

    range = val * perc / 100

    if (range <= 0.5): return val
    if (range > 0.5): range = 1

    #result = 1 + (rand() % (int)range)
    result = 1 + (random.uniform(0,range))

    #if( (1 + (rand() % 1) > 0)) return val + result;
    if( (1 + (random.uniform(0,1)) > 0)): return val + result
    else: return val + (result * -1)

def QuerySleep(ms: int): # Sleep / Delay

    kernel32             = ctypes.WinDLL('kernel32', use_last_error=True)

    timerResolution = ctypes.wintypes.LARGE_INTEGER()
    wantedTime = ctypes.wintypes.LARGE_INTEGER()
    currentTime = ctypes.wintypes.LARGE_INTEGER()

    kernel32.QueryPerformanceFrequency(ctypes.byref(timerResolution)) 
    timerResolution.value //= 1000

    kernel32.QueryPerformanceCounter(ctypes.byref(currentTime))

    wantedTime = currentTime.value / timerResolution.value + ms
    currentTime = ctypes.c_longlong(0)
    while (currentTime.value < wantedTime):
    
        kernel32.QueryPerformanceCounter(ctypes.byref(currentTime))
        currentTime.value //= timerResolution.value

def Smoothing(delay, control_time, x: float, y: float):

    x_ = 0
    y_ = 0
    t_ = 0
    i = 1
    while i < int(control_time):

        xI = i * x / int(control_time)
        yI = i * y / int(control_time)
        tI = i * int(control_time) / int(control_time)

        mouse_move(int(xI) - int(x_), int(yI) - int(y_))
        QuerySleep(int(tI) - int(t_))
        x_ = xI; y_ = yI; t_ = tI

    QuerySleep(delay - control_time)

def getScope(val: float):

    if (scope == 1):
        return val * 1.2
    if (scope == 2):
        return val * 3.84
    return val

def tofovandsens(sens: float, fov: int, val: float):

    a = (0.5 * fov * val) / ( sens * 90)

    b = getScope(a)

    return b



    


class Timer():

    def timer():
        global starting_time
        starting_time = ctypes.wintypes.LARGE_INTEGER()

    def Elapsed():
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        ending_time = ctypes.wintypes.LARGE_INTEGER()
        elapsed_microseconds = ctypes.wintypes.LARGE_INTEGER()
        frequency = ctypes.wintypes.LARGE_INTEGER()

        kernel32.QueryPerformanceFrequency(ctypes.byref(frequency))
        kernel32.QueryPerformanceCounter(ctypes.byref(starting_time))
        
        kernel32.QueryPerformanceCounter(ctypes.byref(ending_time))

        elapsed_microseconds = ending_time.value - starting_time.value
        elapsed_microseconds *= 1000000
        elapsed_microseconds /= frequency.value

        return elapsed_microseconds

def change_gun() -> None:
    global gun_type
    global timer
    global gun_name
    global name_of_sight
    global scope

    KeyMin = 0

    AssaultRifleKeyValue = win32api.GetAsyncKeyState(0x61)
    if AssaultRifleKeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'Assault_Rifle':
        gun_type = values.Assault_Rifle_Iron
        gun_name = 'Assault_Rifle'
        timer = values.AssaultRifleTime
        print(f'Changed gun to {gun_name}')
        beep()
    LR300RifleKeyValue = win32api.GetAsyncKeyState(0x62)
    if LR300RifleKeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'LR300':
        gun_type = values.LR300Rifle
        gun_name = 'LR300'
        timer = values.LR300AssaultRifleTime
        print(f'Changed gun to {gun_name}')
        beep()
    ThompsonKeyValue = win32api.GetAsyncKeyState(0x63)
    if ThompsonKeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'Thompson':
        gun_type = values.Thompson
        gun_name = 'Thompson'
        timer = get_tick(values.ThompsonRPM)
        print(f'Changed gun to {gun_name}')
        beep()
    MP5KeyValue = win32api.GetAsyncKeyState(0x64)
    if MP5KeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'MP5_SMG':
        gun_type = values.MP5_SMG_Iron
        gun_name = 'MP5_SMG'
        timer = values.MP5A4Time
        print(f'Changed gun to {gun_name}')
        beep()
    CustomSMGKeyValue = win32api.GetAsyncKeyState(0x65)
    if CustomSMGKeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'CustomSMG':
        gun_type = values.CustomSMG
        gun_name = 'CustomSMG'
        timer = get_tick(values.CustomSMGRPM)
        print(f'Changed gun to {gun_name}')
        beep()
    M249KeyValue = win32api.GetAsyncKeyState(0x66)
    if M249KeyValue < KeyMin and win32api.GetAsyncKeyState(0x11) < 0 and gun_name != 'M249':
        gun_type = values.M249
        gun_name = 'M249'
        timer = get_tick(values.M249RPM)
        print(f'Changed gun to {gun_name}')
        beep()

    current_gun_name = gun_name
    iron = win32api.GetAsyncKeyState(0x67)
    if iron < KeyMin and win32api.GetAsyncKeyState(0x11) < 0:
        attachment = 0
        gun_type = values.set_attachment_pattern(current_gun_name,attachment)
        name_of_sight = 'Iron'
        print(f'Changed gun to {current_gun_name} with {name_of_sight}')
        beep()
    holo = win32api.GetAsyncKeyState(0x68)
    if holo < KeyMin and win32api.GetAsyncKeyState(0x11) < 0:
        attachment = 1
        scope = 1
        gun_type = values.set_attachment_pattern(current_gun_name,attachment)
        name_of_sight = 'Holo'
        print(f'Changed gun to {current_gun_name} with {name_of_sight}')
        beep()
    eight = win32api.GetKeyState(0x69)
    if eight < 0 and win32api.GetKeyState(0x11) < 0:
        attachment = 2
        scope = 2
        gun_type = values.set_attachment_pattern(current_gun_name,attachment)
        name_of_sight = '8x'
        print(f'Changed gun to {current_gun_name} with {name_of_sight}')
        beep()
    
    construct_overlay(overlay,gun_name,gun_type)

def get_tick(rpm):
    rps = rpm/60
    mstick = 1000.0/rps
    stick = round(mstick/1000, 3)
    return stick

def menu():
    global gun_type

    count = 1

    for gun in values.guns:
        print(f'Numpad Key: {count} - {gun}')
        count += 1
    print("0 - None")
    print("\nMade By Dylan")
    beep()
    

def iskeypressed():
    LeftClickKeyValue = win32api.GetAsyncKeyState(LMB) 
    RightClickKeyValue = win32api.GetAsyncKeyState(RMB)
    if LeftClickKeyValue < 0 and RightClickKeyValue < 0:
        return True

def ispressednumbar():
    global gun_type
    global gun_name

    NumpadZeroKeyValue = win32api.GetAsyncKeyState(0x60)
    if NumpadZeroKeyValue < 0:
        gun_type = 0
        gun_name = 'None'
        print('No gun selected')
        beep()
        loop()

def mouse_move(x, y):
    global lost

    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(x), int(y), 0, 0)
    end_time = give_time()
    lost += ( (end_time - start_time) / 1000 )

def mousedown(gun_type,timer):
    global start_time
    global lost

    lost = 0
    shot_tick = timer
    shot_index = 0
    count = 0
    shot_total = 0

    """ while iskeypressed(): #and count <= shot_total:

        if gun_name == 'Assault_Rifle':
            
            control_time = values.AK_Control
            gun_pattern = values.AK
            shot_total = len(gun_pattern)
            #Smoothing(Weapons::ak::delay, Weapons::ak::controltime.at(count), Randomize(tofovandsens(playersens, playerfov, Weapons::ak::pattern.at(count).x),randomizer), Randomize(tofovandsens(playersens, playerfov, Weapons::ak::pattern.at(count).y),randomizer));
            Smoothing(values.AK_DELAY, control_time[count], Randomize(tofovandsens(playersens, playerfov, gun_pattern[count][X]),randomizer), Randomize(tofovandsens(playersens, playerfov, gun_pattern[count][Y]),randomizer))

            count += 1 """


    while iskeypressed():

        if shot_index < len(gun_type) - 1:
            for recoilValue in gun_type:
                
                random_numX = random.uniform(0.93,1.08)
                random_numY = random.uniform(0.93,1.08)

                #randomRecoilX = random.uniform(recoilValue[X], recoilValue[Y] + maxRandom)
                #randomRecoilY = random.uniform(recoilValue[Y], recoilValue[Y] + maxRandom)

                RecoilX = recoilValue[X] * random_numX
                RecoilY = recoilValue[Y] * random_numY

                #RecoilX = randomizer(RecoilX)
                #RecoilY = randomizer(RecoilY)

                realx = ( round( (RecoilX / 2 ) ) / sensitivity)
                realy = ( round( (RecoilY / 2 ) ) / sensitivity)

                start_time = give_time()

                #smoothing function
                for count in range(smooth):

                    #smooth = randomizer(smooth)

                    xToMove = (realx / smooth)
                    yToMove = (realy / smooth)

                    mouse_move(int(xToMove), int(yToMove))

                    time.sleep(shot_tick / smooth)
                
                end_time = give_time()
                shot_index += 1
                if not iskeypressed():
                    return
    
def construct_overlay(overlay, gun_name, gun_type):
    recoil_data = "ON" if gun_type != 0 else "OFF"
    bg_data = "#acffac" if gun_type != 0 else "#ffacac"
    recoil_string = "NoRecoil: {}".format(recoil_data)
    weapon_string = "Weapon: {}".format(gun_name)
    attachment_string = "Scope: {}".format(name_of_sight)
    length = max(len(recoil_string), len(weapon_string), len(attachment_string))
    #overlay_string = "{}\n{}".format(recoil_string.ljust(length), weapon_string.ljust(length), attachment_string.ljust(length))
    overlay_string = f"\n{recoil_string.ljust(length)}\n{weapon_string.ljust(length)}\n{attachment_string.ljust(length)}"
    overlay.set_bg(bg_data)
    overlay.set_text(overlay_string)
    

def loop():
    
    while gun_type == 0:
        change_gun()
    while gun_type != 0:
        change_gun()
        ispressednumbar()
        if iskeypressed():
            mousedown(gun_type,timer)
menu()
loop()
start()
