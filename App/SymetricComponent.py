#***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Class for rocket components"""

__title__ = "FreeCAD Rocket Components"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from abc import abstractmethod
import math

from App.interfaces.BoxBounded import BoxBounded
from App.interfaces.RadialParent import RadialParent

from App.ShapeComponent import ShapeComponent
from App.util.BoundingBox import BoundingBox
from App.util.Coordinate import Coordinate

# Class for an axially symmetric rocket component generated by rotating
# a function y=f(x) >= 0 around the x-axis (eg. tube, cone, etc.)

class SymetricComponent(ShapeComponent, BoxBounded, RadialParent):

    DEFAULT_RADIUS = 0.025

    def __init__(self, obj):
        super().__init__(obj)

    def getInstanceBoundingBox(self):
        instanceBounds = BoundingBox();

        instanceBounds.update(Coordinate(self.getLength(), 0,0));

        r = max(self.getForeRadius(), self.getAftRadius())
        instanceBounds.update(Coordinate(0,r,r))
        instanceBounds.update(Coordinate(0,-r,-r))

        return instanceBounds

    """
        Return the component radius at position x.
    """
    @abstractmethod
    def getRadius(self, x):
        pass

    @abstractmethod
    def getForeRadius(self):
        pass

    @abstractmethod
    def isForeRadiusAutomatic(self):
        pass

    @abstractmethod
    def getAftRadius(self):
        pass

    @abstractmethod
    def isAftRadiusAutomatic(self):
        pass

    def getOuterRadius(self, x):
        self.getRadius(x)

    def getInnerRadius(self, x):
        self.getRadius(x)

    """
        Adds component bounds at a number of points between 0...length.
    """
    def getComponentBounds(self):
        list = []
        for n in range(6): # 0-5
            x = n * self._obj.Length / 5
            r = self.getRadius(x)
            self.addBound(list, x, r)

        return list
