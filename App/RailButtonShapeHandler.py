# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing rail buttons"""

__title__ = "FreeCAD Rail Button Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from App.Constants import RAIL_BUTTON_AIRFOIL
import FreeCAD
import Part
import math

from App.Utilities import _err
from DraftTools import translate

class RailButtonShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        self._railButtonType = obj.RailButtonType

        self._outerDiameter = float(obj.OuterDiameter)
        self._innerDiameter = float(obj.InnerDiameter)
        self._topThickness = float(obj.TopThickness)
        self._bottomThickness = float(obj.BottomThickness)
        self._thickness = float(obj.Thickness)
        self._length = float(obj.Length)

        self._obj = obj

    def isValidShape(self):
        # Perform some general validations
        if self._outerDiameter <= 0:
            _err(translate('Rocket', "Outer diameter must be greater than zero"))
            return False
        if self._innerDiameter <= 0:
            _err(translate('Rocket', "Inner diameter must be greater than zero"))
            return False
        if self._outerDiameter <= self._innerDiameter:
            _err(translate('Rocket', "Outer diameter must be greater than the inner diameter"))
            return False
        if self._topThickness <= 0:
            _err(translate('Rocket', "Top thickness must be greater than zero"))
            return False
        if self._bottomThickness <= 0:
            _err(translate('Rocket', "Bottom thickness must be greater than zero"))
            return False
        if self._thickness <= 0:
            _err(translate('Rocket', "Thickness must be greater than zero"))
            return False
        if self._thickness <= (self._topThickness + self._bottomThickness):
            _err(translate('Rocket', "Top and bottom thickness can not excedd the total thickness"))
            return False

        if self._railButtonType == RAIL_BUTTON_AIRFOIL:
            if self._length <= 0:
                _err(translate('Rocket', "Length must be greater than zero for airfoil rail buttons"))
                return False

            if self._length <= self._outerDiameter:
                _err(translate('Rocket', "Length must be greater than the outer diameter for airfoil rail buttons"))
                return False

        return True

    def _drawButton(self):
        # For now, only round buttons
        spool = Part.makeCylinder(self._innerDiameter / 2.0, self._thickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))

        spoolTop = Part.makeCylinder(self._outerDiameter / 2.0, self._topThickness, FreeCAD.Vector(0,0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        spool = spool.fuse(spoolTop)

        # spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._thickness - self._topThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0))
        spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._bottomThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
        spool = spool.fuse(spoolBottom)

        return spool

    def _airfoil(self, base, thickness, diameter, length):
        # Calculate the tangent points
        radius = diameter/2.0
        theta = math.pi - math.atan2(length - radius, radius)
        x = -(radius * math.cos(theta))
        y = radius * math.sin(theta)

        v1 = FreeCAD.Vector(-x,y,base)
        v2 = FreeCAD.Vector(-x,-y,base)
        v3 = FreeCAD.Vector(radius,0,base)
        v4 = FreeCAD.Vector(radius - length,0,base)

        arc = Part.Arc(v1,v3,v2)
        line1 = Part.LineSegment(v1, v4)
        line2 = Part.LineSegment(v2, v4)
        shape = Part.Shape([arc, line1, line2])
        wire = Part.Wire(shape.Edges)
        face = Part.Face(wire)
        airfoil = face.extrude(FreeCAD.Vector(0, 0, thickness))

        return airfoil

    def _drawAirfoil(self):
        spool = self._airfoil(0.0, self._thickness, self._innerDiameter, (self._length - (self._outerDiameter - self._innerDiameter)))

        spoolTop = Part.makeCylinder(self._outerDiameter / 2.0, self._topThickness, FreeCAD.Vector(0,0,self._thickness - self._topThickness), FreeCAD.Vector(0,0,1))
        spoolTop = self._airfoil(self._thickness - self._topThickness, self._topThickness, self._outerDiameter, self._length)
        spool = spool.fuse(spoolTop)

        spoolBottom = Part.makeCylinder(self._outerDiameter / 2.0, self._bottomThickness, FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,0,1))
        spoolBottom = self._airfoil(0.0, self._bottomThickness, self._outerDiameter, self._length)
        spool = spool.fuse(spoolBottom)

        return spool
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            if self._railButtonType == RAIL_BUTTON_AIRFOIL:
                self._obj.Shape = self._drawAirfoil()
            else:
                self._obj.Shape = self._drawButton()
            self._obj.Placement = self._placement
        except (ZeroDivisionError, Part.OCCError):
            _err(translate('Rocket', "Rail button parameters produce an invalid shape"))
            return