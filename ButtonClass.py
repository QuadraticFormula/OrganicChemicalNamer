import pygame as py
from typing import Tuple
py.init()

class Button:
    def __init__(
            self,
            position: Tuple[int, int],
            size: Tuple[int, int],
            on_click_function: callable = None,
            on_click_args: tuple = tuple(),
            on_click_kwargs: dict = {},
            ):

        # Button dimensions and position
        self.size = size
        self.position = position
        self.rect = py.Rect(self.position, self.size)

        # State Setup
        self.state = 'idle'
        self.clicked = False
        self.just_clicked = False

        # Button Setup
        self.on_click_function = on_click_function
        self.on_click_args = on_click_args
        self.on_click_kwargs = on_click_kwargs

    def update_mouse(self):
        if self.just_clicked:
            self.just_clicked = False
        if not py.mouse.get_pressed()[0]:
            self.clicked = False
        elif not self.clicked:
            self.just_clicked = True
            self.clicked = True

        # print(py.mouse.get_pressed()[0])

    def update_state(self):
        if self.state == 'just_clicked':
            self.state = 'clicked'
        elif not (self.state == 'clicked' and self.clicked):
            if not self.rect.collidepoint(py.mouse.get_pos()):
                self.state = 'idle'
            elif self.just_clicked:
                self.state = 'just_clicked'
            else:
                self.state = 'hovered'


    def update(self):
        self.update_mouse()
        self.update_state()

        if self.state == 'just_clicked':
            self.on_click_function(*self.on_click_args, **self.on_click_kwargs)
