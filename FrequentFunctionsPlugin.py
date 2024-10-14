import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance

from dataclasses import dataclass

VENDOR = "Hridiza Roy"
VERSION = "1.1"

ui_instance = None

# Required function to use the new Maya api
def maya_useNewAPI():
    pass

# Function to get Maya's main window for parenting the UI
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def create_button(text: str, callback):
    button = QtWidgets.QPushButton(text)
    button.clicked.connect(callback)

    return button

def create_column_header(text: str) -> QtWidgets.QLabel:
    font_size = 24

    stylesheet = f"font-size: {font_size}px; \
                font-weight: bold;"

    header = QtWidgets.QLabel(text)
    header.setStyleSheet(stylesheet)
    header.setAlignment(QtCore.Qt.AlignCenter)

    return header


def create_section(header: str, buttons: list) -> QtWidgets.QLayout:
    layout = QtWidgets.QVBoxLayout()
    layout.setAlignment(QtCore.Qt.AlignTop)

    header_label = create_column_header(header)
    layout.addWidget(header_label)

    for button in buttons:
        layout.addWidget(button)

    return layout


class FrequentFunctionsUI(QtWidgets.QDialog):
    @dataclass
    class UI_Section:
        header: str
        buttons: list


    def __init__(self, parent = maya_main_window()):
        super(FrequentFunctionsUI, self).__init__(parent)

        self.width = 600
        self.height = 400

        # Window properties
        self.setWindowTitle('Frequent Functions UI')
        self.setMinimumSize(self.width, self.height)
        self.setWindowFlags(QtCore.Qt.Window | \
                            QtCore.Qt.WindowMinimizeButtonHint | \
                            QtCore.Qt.WindowCloseButtonHint)

        # Create layout and buttons
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.sections = []

        # Different sections
        section_headers = ["Modeling", "Rigging", "UV/Texturing"]
        for header in section_headers:
            self.sections.append(self.UI_Section(header, []))


        # Modeling Buttons
        # Export
        export_button = create_button("Export selected", \
                                           self.export_selected)
        self.sections[0].buttons.append(export_button)

        # Duplicate special
        duplicate_special_button = create_button("Duplicate Special", \
                                                      self.duplicate_special)
        self.sections[0].buttons.append(duplicate_special_button)

        
        # Rigging buttons
        # Node Editor
        node_editor_button = create_button("Node Editor", \
                                                self.open_node_editor)
        self.sections[1].buttons.append(node_editor_button)

        # Create joints
        create_joints_button = create_button("Create joints", \
                                             self.create_joints)
        self.sections[1].buttons.append(create_joints_button)

        # Joint Hierarchy Window
        joint_hierarchy_button = create_button("Joint Hierarchy Window", \
                                               self.joint_hierarchy_window)
        self.sections[1].buttons.append(joint_hierarchy_button)

        # Outliner
        outliner_button = create_button("Outliner", self.outliner)
        self.sections[1].buttons.append(outliner_button)

        # Paint skin weights
        paint_weights_button = create_button("Paint weights", \
                                                self.paint_weights)
        self.sections[1].buttons.append(paint_weights_button)


        # UV/Texturing buttons
        # UV Editor
        uv_editor_button = create_button("UV Editor", self.open_uv_editor)
        self.sections[2].buttons.append(uv_editor_button)


        # Combine sections
        combined_layout = QtWidgets.QHBoxLayout()
        for section in self.sections:
            section_layout = create_section(section.header, section.buttons)
            combined_layout.addLayout(section_layout)

        # Add to parent layout
        self.layout.addLayout(combined_layout)

    
    def export_selected(self):
        try:
            # Make sure that something is selected
            selection = cmds.ls(selection = True)
            if not selection:
                om.MGlobal.displayError("No objects selected. \
                            Please select the objects you want to export.")
                return
            
            cmds.ExportSelection()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Export Special Dialog: {e}")
    
    def duplicate_special(self):
        try:
            cmds.DuplicateSpecialOptions()
        except Exception as e:
            om.MGlobal.displayError(f"Error applying Duplicate Special: {e}")

    def open_node_editor(self):
        try:
            cmds.NodeEditorWindow()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Node Editor: {e}")

    def create_joints(self):
        try:
            cmds.JointTool()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Joint Tool: {e}")

    def joint_hierarchy_window(self):
        try:
            cmds.HypergraphHierarchyWindow()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Joint Hierarchy Window: {e}")

    def outliner(self):
        try:
            cmds.OutlinerWindow()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Outliner: {e}")

    def paint_weights(self):
        try:
            cmds.ArtPaintSkinWeightsToolOptions()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening Paint weights tool: {e}")

    def open_uv_editor(self):
        try:
            cmds.TextureViewWindow()
        except Exception as e:
            om.MGlobal.displayError(f"Error opening UV Editor: {e}")


def show_frequent_functions_ui():
    global ui_instance

    if ui_instance is not None:
        ui_instance.close()
    
    ui_instance = FrequentFunctionsUI()
    ui_instance.show()


# Plugin command class
class FrequentFunctionsUICmd(om.MPxCommand):
    kPluginCmdName = "openFFUI"

    def __init__(self):
        super(FrequentFunctionsUICmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return FrequentFunctionsUICmd()

    def doIt(self, *args):
        show_frequent_functions_ui()


# Initialize the plugin
def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject, VENDOR, VERSION)

    try:
        mplugin.registerCommand(FrequentFunctionsUICmd.kPluginCmdName, \
                                FrequentFunctionsUICmd.cmdCreator)
        om.MGlobal.displayInfo("FrequentFunctionsUI Plugin loaded.")
    except:
        om.MGlobal.displayError("Failed to register FrequentFunctionsUI command.")

# Uninitialize the plugin
def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)

    try:
        mplugin.deregisterCommand(FrequentFunctionsUICmd.kPluginCmdName)
        om.MGlobal.displayInfo("FrequentFunctionsUI Plugin unloaded.")
    except:
        om.MGlobal.displayError("Failed to deregister FrequentFunctionsUI command.")
