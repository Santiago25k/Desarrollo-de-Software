# app/input/mouse.py
import pyautogui
import time
import random

# Optimizacion basica
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0

hold_time = 0.04
post_move_delay = 0.0
delta_factor = 0.5


def move_to(x, y):
    """Mueve el mouse instantaneamente"""
    pyautogui.moveTo(x, y, duration=0)


def click_left(hold_time=0.001):
    """Click izquierdo con hold"""
    pyautogui.mouseDown()
    time.sleep(hold_time)
    pyautogui.mouseUp()


def click_cell(cell, hold_time=0.001, jitter=15):
    """
    Click en el centro de una celda con micro-random humano
    jitter: desvio en pixeles (+-)
    """
    x, y, w, h = cell

    cx = x + w // 2 + random.randint(-jitter, jitter)
    cy = y + h // 2 + random.randint(-jitter, jitter)

    move_to(cx, cy)
    time.sleep(0.001)  # NO lo saques aun
    click_left(hold_time)
