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
"""Class for drawing nose cones"""

__title__ = "FreeCAD Nose Cones"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from DraftTools import translate

from Ui.TaskPanelDatabase import TaskPanelDatabase
from App.Constants import TYPE_CONE, TYPE_BLUNTED_CONE, TYPE_SPHERICAL, TYPE_ELLIPTICAL, TYPE_HAACK, TYPE_OGIVE, TYPE_BLUNTED_OGIVE, TYPE_SECANT_OGIVE, TYPE_VON_KARMAN, TYPE_PARABOLA, TYPE_PARABOLIC, TYPE_POWER
from App.Constants import STYLE_CAPPED, STYLE_HOLLOW, STYLE_SOLID
from App.Constants import COMPONENT_TYPE_NOSECONE

from App.Utilities import _toFloat, _valueWithUnits

class _NoseConeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Nose Cone Parameter"))

        self.tabWidget = QtGui.QTabWidget()
        self.tabGeneral = QtGui.QWidget()
        self.tabShoulder = QtGui.QWidget()
        self.tabWidget.addTab(self.tabGeneral, translate('Rocket', "General"))
        self.tabWidget.addTab(self.tabShoulder, translate('Rocket', "Shoulder"))

        layout = QVBoxLayout()
        layout.addWidget(self.tabWidget)
        self.setLayout(layout)

        self.setTabGeneral()
        self.setTabShoulder()

    def setTabGeneral(self):
        ui = FreeCADGui.UiLoader()

        # Select the type of nose cone
        self.noseConeTypeLabel = QtGui.QLabel(translate('Rocket', "Nose Cone Shape"), self)

        self.noseConeTypes = (TYPE_CONE,
                                TYPE_BLUNTED_CONE,
                                TYPE_SPHERICAL,
                                TYPE_ELLIPTICAL,
                                TYPE_OGIVE,
                                TYPE_BLUNTED_OGIVE,
                                TYPE_SECANT_OGIVE,
                                TYPE_PARABOLA,
                                TYPE_PARABOLIC,
                                TYPE_POWER,
                                TYPE_VON_KARMAN,
                                TYPE_HAACK)
        self.noseConeTypesCombo = QtGui.QComboBox(self)
        self.noseConeTypesCombo.addItems(self.noseConeTypes)

        # Select the type of sketch
        self.noseStyleLabel = QtGui.QLabel(translate('Rocket', "Style"), self)

        self.noseStyles = (STYLE_SOLID,
                                STYLE_HOLLOW,
                                STYLE_CAPPED)
        self.noseStylesCombo = QtGui.QComboBox(self)
        self.noseStylesCombo.addItems(self.noseStyles)

        # Get the nose cone parameters: length, width, etc...
        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(80)

        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setFixedWidth(80)
        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(80)
        self.thicknessInput.setEnabled(False)

        #
        # Type dependent parameters
        self.coefficientLabel = QtGui.QLabel(translate('Rocket', "Shape Parameter"), self)

        self.coefficientValidator = QtGui.QDoubleValidator(self)
        self.coefficientValidator.setBottom(0.0)

        self.coefficientInput = QtGui.QLineEdit(self)
        self.coefficientInput.setFixedWidth(80)
        self.coefficientInput.setValidator(self.coefficientValidator)
        self.coefficientInput.setEnabled(False)

        self.bluntedLabel = QtGui.QLabel(translate('Rocket', "Blunted Diameter"), self)

        self.bluntedInput = ui.createWidget("Gui::InputField")
        self.bluntedInput.unit = 'mm'
        self.bluntedInput.setFixedWidth(80)

        self.ogiveDiameterLabel = QtGui.QLabel(translate('Rocket', "Ogive Diameter"), self)

        self.ogiveDiameterInput = ui.createWidget("Gui::InputField")
        self.ogiveDiameterInput.unit = 'mm'
        self.ogiveDiameterInput.setFixedWidth(80)

        layout = QGridLayout()
        row = 0

        layout.addWidget(self.noseConeTypeLabel, row, 0, 1, 2)
        layout.addWidget(self.noseConeTypesCombo, row, 1)
        row += 1

        layout.addWidget(self.noseStyleLabel, row, 0)
        layout.addWidget(self.noseStylesCombo, row, 1)
        row += 1

        layout.addWidget(self.lengthLabel, row, 0)
        layout.addWidget(self.lengthInput, row, 1)
        row += 1

        layout.addWidget(self.diameterLabel, row, 0)
        layout.addWidget(self.diameterInput, row, 1)
        row += 1

        layout.addWidget(self.thicknessLabel, row, 0)
        layout.addWidget(self.thicknessInput, row, 1)
        row += 1

        layout.addWidget(self.coefficientLabel, row, 0)
        layout.addWidget(self.coefficientInput, row, 1)
        row += 1

        layout.addWidget(self.ogiveDiameterLabel, row, 0)
        layout.addWidget(self.ogiveDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.bluntedLabel, row, 0)
        layout.addWidget(self.bluntedInput, row, 1)
        # row += 1

        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabGeneral.setLayout(layout)

    def setTabShoulder(self):
        ui = FreeCADGui.UiLoader()

        self.shoulderLabel = QtGui.QLabel(translate('Rocket', "Shoulder"), self)

        self.shoulderCheckbox = QtGui.QCheckBox(self)
        self.shoulderCheckbox.setCheckState(QtCore.Qt.Unchecked)

        self.shoulderDiameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.shoulderDiameterInput = ui.createWidget("Gui::InputField")
        self.shoulderDiameterInput.unit = 'mm'
        self.shoulderDiameterInput.setFixedWidth(80)
        self.shoulderDiameterInput.setEnabled(False)

        self.shoulderLengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.shoulderLengthInput = ui.createWidget("Gui::InputField")
        self.shoulderLengthInput.unit = 'mm'
        self.shoulderLengthInput.setFixedWidth(80)
        self.shoulderLengthInput.setEnabled(False)

        self.shoulderThicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.shoulderThicknessInput = ui.createWidget("Gui::InputField")
        self.shoulderThicknessInput.unit = 'mm'
        self.shoulderThicknessInput.setFixedWidth(80)
        self.shoulderThicknessInput.setEnabled(False)

        layout = QGridLayout()
        row = 0

        layout.addWidget(self.shoulderLabel, row, 0, 1, 2)
        layout.addWidget(self.shoulderCheckbox, row, 1)
        row += 1

        layout.addWidget(self.shoulderLengthLabel, row, 0)
        layout.addWidget(self.shoulderLengthInput, row, 1)
        row += 1

        layout.addWidget(self.shoulderDiameterLabel, row, 0)
        layout.addWidget(self.shoulderDiameterInput, row, 1)
        row += 1

        layout.addWidget(self.shoulderThicknessLabel, row, 0)
        layout.addWidget(self.shoulderThicknessInput, row, 1)

        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.tabShoulder.setLayout(layout)

class TaskPanelNoseCone:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._noseForm = _NoseConeDialog()
        self._db = TaskPanelDatabase(obj, COMPONENT_TYPE_NOSECONE)
        self._dbForm = self._db.getForm()

        self.form = [self._noseForm, self._dbForm]
        self._noseForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_NoseCone.svg"))
        
        self._noseForm.noseConeTypesCombo.currentTextChanged.connect(self.onNoseType)
        self._noseForm.noseStylesCombo.currentTextChanged.connect(self.onNoseStyle)

        self._noseForm.lengthInput.textEdited.connect(self.onLengthChanged)
        self._noseForm.bluntedInput.textEdited.connect(self.onBluntedChanged)
        self._noseForm.diameterInput.textEdited.connect(self.onDiameterChanged)
        self._noseForm.thicknessInput.textEdited.connect(self.onThicknessChanged)
        self._noseForm.coefficientInput.textEdited.connect(self.onCoefficientChanged)
        self._noseForm.ogiveDiameterInput.textEdited.connect(self.onOgiveDiameterChanged)

        self._noseForm.shoulderCheckbox.stateChanged.connect(self.onShoulderChanged)
        self._noseForm.shoulderDiameterInput.textEdited.connect(self.onShoulderDiameterChanged)
        self._noseForm.shoulderLengthInput.textEdited.connect(self.onShoulderLengthChanged)
        self._noseForm.shoulderThicknessInput.textEdited.connect(self.onShoulderThicknessChanged)

        self._db.dbLoad.connect(self.onLookup)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.NoseType = str(self._noseForm.noseConeTypesCombo.currentText())
        self._obj.NoseStyle = str(self._noseForm.noseStylesCombo.currentText())
        self._obj.Length = self._noseForm.lengthInput.text()
        self._obj.BluntedDiameter = self._noseForm.bluntedInput.text()
        self._obj.Diameter = self._noseForm.diameterInput.text()
        self._obj.Thickness = self._noseForm.thicknessInput.text()
        self._obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        self._obj.OgiveDiameter = self._noseForm.ogiveDiameterInput.text()
        self._obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        self._obj.ShoulderDiameter = self._noseForm.shoulderDiameterInput.text()
        self._obj.ShoulderLength = self._noseForm.shoulderLengthInput.text()
        self._obj.ShoulderThickness = self._noseForm.shoulderThicknessInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._noseForm.noseConeTypesCombo.setCurrentText(self._obj.NoseType)
        self._noseForm.noseStylesCombo.setCurrentText(self._obj.NoseStyle)
        self._noseForm.lengthInput.setText(self._obj.Length.UserString)
        self._noseForm.bluntedInput.setText(self._obj.BluntedDiameter.UserString)
        self._noseForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._noseForm.thicknessInput.setText(self._obj.Thickness.UserString)
        self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
        self._noseForm.ogiveDiameterInput.setText(self._obj.OgiveDiameter.UserString)
        self._noseForm.shoulderCheckbox.setChecked(self._obj.Shoulder)
        self._noseForm.shoulderDiameterInput.setText(self._obj.ShoulderDiameter.UserString)
        self._noseForm.shoulderLengthInput.setText(self._obj.ShoulderLength.UserString)
        self._noseForm.shoulderThicknessInput.setText(self._obj.ShoulderThickness.UserString)

        self._setTypeState()
        self._setStyleState()
        self._setShoulderState()
        
    def _setCoeffientState(self):
        value = self._obj.NoseType
        if value == TYPE_HAACK or value == TYPE_PARABOLIC:
            self._noseForm.coefficientInput.setEnabled(True)
        elif value == TYPE_POWER:
            self._noseForm.coefficientInput.setEnabled(True)
        elif value == TYPE_VON_KARMAN:
            self._obj.Coefficient = 0.0
            self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.coefficientInput.setEnabled(False)
        elif value == TYPE_PARABOLA:
            self._obj.Coefficient = 0.5
            self._noseForm.coefficientInput.setText("%f" % self._obj.Coefficient)
            self._noseForm.coefficientInput.setEnabled(False)
        else:
            self._noseForm.coefficientInput.setEnabled(False)
        
    def _setBluntState(self):
        value = self._obj.NoseType
        if value in [TYPE_BLUNTED_CONE, TYPE_BLUNTED_OGIVE]:
            self._noseForm.bluntedInput.setEnabled(True)
        else:
            self._noseForm.bluntedInput.setEnabled(False)
        
    def _setOgiveDiameterState(self):
        value = self._obj.NoseType
        if value == TYPE_SECANT_OGIVE:
            self._noseForm.ogiveDiameterInput.setEnabled(True)
        else:
            self._noseForm.ogiveDiameterInput.setEnabled(False)
        
    def _setLengthState(self):
        value = self._obj.NoseType
        if value == TYPE_SPHERICAL:
            self._obj.Length = float(self._obj.Diameter) / 2.0
            self._noseForm.lengthInput.setText("%f" % self._obj.Length)
            self._noseForm.lengthInput.setEnabled(False)
        else:
            self._noseForm.lengthInput.setEnabled(True)
        
    def _setTypeState(self):
        self._setCoeffientState()
        self._setBluntState()
        self._setOgiveDiameterState()
        self._setLengthState()

    def onNoseType(self, value):
        self._obj.NoseType = value
        self._setTypeState()

        self._obj.Proxy.execute(self._obj)

    def _setStyleState(self):
        value = self._obj.NoseStyle
        if value == STYLE_HOLLOW or value == STYLE_CAPPED:
            self._noseForm.thicknessInput.setEnabled(True)

            if self._noseForm.shoulderCheckbox.isChecked():
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.thicknessInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)
        
    def onNoseStyle(self, value):
        self._obj.NoseStyle = value
        self._setStyleState()

        self._obj.Proxy.execute(self._obj)
        
    def onLengthChanged(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onBluntedChanged(self, value):
        try:
            self._obj.BluntedDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onDiameterChanged(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)

            self._setLengthState() # Update for spherical noses
        except ValueError:
            pass
        
    def onThicknessChanged(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onCoefficientChanged(self, value):
        self._obj.Coefficient = _toFloat(value)
        self._obj.Proxy.execute(self._obj)
        
    def onOgiveDiameterChanged(self, value):
        try:
            self._obj.OgiveDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass

    def _setShoulderState(self):
        if self._obj.Shoulder:
            self._noseForm.shoulderDiameterInput.setEnabled(True)
            self._noseForm.shoulderLengthInput.setEnabled(True)

            selectedText = self._noseForm.noseStylesCombo.currentText()
            if selectedText == STYLE_HOLLOW or selectedText == STYLE_CAPPED:
                self._noseForm.shoulderThicknessInput.setEnabled(True)
            else:
                self._noseForm.shoulderThicknessInput.setEnabled(False)
        else:
            self._noseForm.shoulderDiameterInput.setEnabled(False)
            self._noseForm.shoulderLengthInput.setEnabled(False)
            self._noseForm.shoulderThicknessInput.setEnabled(False)
        
    def onShoulderChanged(self, value):
        self._obj.Shoulder = self._noseForm.shoulderCheckbox.isChecked()
        self._setShoulderState()

        self._obj.Proxy.execute(self._obj)
        
    def onShoulderDiameterChanged(self, value):
        try:
            self._obj.ShoulderDiameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onShoulderLengthChanged(self, value):
        try:
            self._obj.ShoulderLength = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onShoulderThicknessChanged(self, value):
        try:
            self._obj.ShoulderThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLookup(self):
        result = self._db.getLookupResult()

        self._obj.NoseType = str(result["shape"])
        self._obj.NoseStyle = str(result["style"])
        self._obj.Length = _valueWithUnits(result["length"], result["length_units"])
        self._obj.BluntedDiameter = _valueWithUnits("0", "mm")
        self._obj.Diameter = _valueWithUnits(result["diameter"], result["diameter_units"])
        self._obj.Thickness = _valueWithUnits(result["thickness"], result["thickness_units"])
        # self._obj.Coefficient = _toFloat(self._noseForm.coefficientInput.text())
        self._obj.ShoulderDiameter = _valueWithUnits(result["shoulder_diameter"], result["shoulder_diameter_units"])
        self._obj.ShoulderLength = _valueWithUnits(result["shoulder_length"], result["shoulder_length_units"])
        self._obj.Shoulder = (self._obj.ShoulderDiameter > 0.0) and (self._obj.ShoulderLength >= 0)
        self._obj.ShoulderThickness = self._obj.Thickness
        self.update()
        self._obj.Proxy.execute(self._obj) 
        
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self._obj.Proxy.execute(self._obj) 
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
