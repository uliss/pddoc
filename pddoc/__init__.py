# coding=utf-8

from .cairopainter import CairoPainter
from .colorformatter import ColorizingStreamHandler


class Point:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x: float):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y: float):
        self._y = y
