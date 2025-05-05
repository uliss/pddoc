# coding=utf-8

from .cairopainter import CairoPainter
from .colorformatter import ColorizingStreamHandler

__version__ = "0.10.0"


class Point:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    def __str__(self):
        return "Point({x}, {y})".format(x=self._x, y=self._y)

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


class Rectangle:
    def __init__(self, pos: Point, width: float, height: float):
        self._pos = pos
        self._width = width
        self._height = height

    def __str__(self):
        return f"Rectangle({self.x}, {self.y} {self.width}x{self.height})"

    @staticmethod
    def from_points(p0: Point, p1: Point):
        x = min(p0.x, p1.x)
        y = min(p0.y, p1.y)
        w = max(p0.x, p1.x) - x
        h = max(p0.y, p1.y) - y

        return Rectangle(Point(x, y), w, h)

    @staticmethod
    def from_tuple(data: tuple[int, int, int, int]):
        return Rectangle(Point(data[0], data[1]), data[2], data[3])

    @property
    def x(self):
        return self._pos.x

    @x.setter
    def x(self, x: float):
        self._pos.x = x

    @property
    def y(self):
        return self._pos.y

    @y.setter
    def y(self, y: float):
        self._pos.y = y

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height: float):
        self._height = height

    def left(self):
        return self.x

    def right(self):
        return self.x + self.width

    def top(self):
        return self.y

    def bottom(self):
        return self.y + self.height

    def expand(self, left: int, right: int, top: int, bottom: int):
        self.x -= left
        self.y -= top
        self.width += left + right
        self.height += top + bottom
