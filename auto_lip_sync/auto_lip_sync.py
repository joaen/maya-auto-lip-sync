'''
Name: auto_lip_sync

Description: A tool used for generating automated lip sync animation on a facial rig in Autodesk: Maya.
 
Author: Joar Engberg 2021

Installation:
1. Add the auto_lip_sync folder or auto_lip_sync.py to your Maya scripts folder (Username\Documents\maya*version*\scripts).
2. Download the dependencies needed to run this tool (Download the dependencies from: https://github.com/joaen/maya_auto_lip_sync/releases/tag/v1.0.0 or read the Dependencies section further down).
3. To start the auto lipsync tool in Maya simply execute the following lines of code in the script editor or add them as a shelf button:

import auto_lip_sync
auto_lip_sync.start()

'''
import shutil
import os
import sys
import json
import subprocess
import webbrowser

from maya import OpenMaya, OpenMayaUI, mel, cmds
from shiboken2 import wrapInstance
from collections import OrderedDict 
from PySide2 import QtCore, QtGui, QtWidgets

# Import Textgrid. If the module doesn't exist let the user decide if they want to download the dependencies zip.
try:
    import textgrid
except ImportError:
    confirm = cmds.confirmDialog(title="Missing dependencies", message="To be able to run this tool you need to download the required dependencies. Do you want go to the download page?", button=["Yes","Cancel"], defaultButton="Yes", cancelButton="Cancel", dismissString="Cancel")
    if confirm == "Yes":
        webbrowser.open_new("https://github.com/joaen/maya_auto_lip_sync/releases/tag/v1.0.0")
    else:
        pass


class PoseConnectWidget(QtWidgets.QWidget):
    def __init__(self, label, parent=None):
        super(PoseConnectWidget, self).__init__(parent)
        self.combo_label = label
        self.create_ui_widgets()
        self.create_ui_layout()

    def create_ui_widgets(self):
        self.save_pose_combo = QtWidgets.QComboBox()
        self.pose_key_label = QtWidgets.QLabel(self.combo_label)
        self.pose_key_label.setFixedWidth(30)
        self.pose_key_label.setStyleSheet("border: 1px solid #303030;")
    
    def create_ui_layout(self):
        combo_row = QtWidgets.QHBoxLayout(self)
        combo_row.addWidget(self.pose_key_label)
        combo_row.addWidget(self.save_pose_combo)
        combo_row.setContentsMargins(0, 0, 0, 0)
    
    def set_text(self, value):
        self.save_pose_combo.addItems(value)

    def get_text(self):
        return self.save_pose_combo.currentText()
    
    def clear_box(self):
        self.save_pose_combo.clear()


class LipSyncDialog(QtWidgets.QDialog):

    WINDOW_TITLE = "Auto lip sync"
    USER_SCRIPT_DIR = cmds.internalVar(userScriptDir=True)
    OUTPUT_FOLDER_PATH = USER_SCRIPT_DIR+"output"
    INPUT_FOLDER_PATH = USER_SCRIPT_DIR+"input"
    MFA_PATH = USER_SCRIPT_DIR+"montreal-forced-aligner/bin"

    sound_clip_path = ""
    text_file_path = ""
    pose_folder_path = ""
    active_controls = []

    phone_dict = {
        "AA0": "AI", "AA1": "AI", "AA2": "AI", "AE0": "AI", "AE1": "AI", "AE2": "AI",
        "AH0": "AI", "AH1": "AI", "AH2": "AI", "AO0": "AI", "AO1": "AI", "AO2": "AI",
        "AW0": "AI", "AW1": "AI", "AW2": "AI", "AY0": "AI", "AY1": "AI", "AY2": "AI",
        "EH0": "E", "EH1": "E", "EH2": "E", "ER0": "O", "ER1": "O", "ER2": "O", "EY0": "E",
        "EY1": "E", "EY2": "E", "IH0": "AI", "IH1": "AI", "IH2": "AI", "IY0": "E", "IY1": "E",
        "IY2": "E", "OW0": "O", "OW1": "O", "OW2": "O", "OY0": "O", "OY1": "O", "OY2": "O",
        "UH0": "O", "UH1": "O", "UH2": "O", "UW0": "O", "UW1": "O", "UW2": "O", "B": "MBP",
        "CH": "etc", "D": "etc", "DH": "etc", "F": "FV", "G": "etc", "HH": "E", "JH": "E",
        "K": "etc", "L": "L", "M": "MBP", "N": "etc", "NG": "etc", "P": "MBP", "R": "etc",
        "S": "etc", "SH": "etc", "T": "etc", "TH": "etc", "V": "FV", "W": "etc", "Y": "E",
        "Z": "E", "ZH": "etc", "sil": "rest", "None": "rest", "sp": "rest", "spn": "rest", "": "rest"
    }

    phone_path_dict = OrderedDict([
        ("AI", ""),
        ("O", ""),
        ("E", ""),
        ("U", ""),
        ("etc", ""),
        ("L", ""),
        ("WQ", ""),
        ("MBP", ""),
        ("FV", ""),
        ("rest", "")
    ])

    def __init__(self):

        main_window = OpenMayaUI.MQtUtil.mainWindow()
        if sys.version_info.major < 3:
            maya_main_window = wrapInstance(long(main_window), QtWidgets.QWidget) # type: ignore
        else:
            maya_main_window = wrapInstance(int(main_window), QtWidgets.QWidget)
        
        super(LipSyncDialog, self).__init__(maya_main_window)

        self.widget_list = []
        self.counter = 0
        self.maya_color_list = [13, 18, 14, 17]
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(380, 100)
        self.create_ui_widgets()
        self.create_ui_layout()
        self.create_ui_connections()
 
    def create_ui_widgets(self):
        self.sound_text_label = QtWidgets.QLabel("Input wav.file:")
        self.sound_filepath_line = QtWidgets.QLineEdit()
        self.sound_filepath_button = QtWidgets.QPushButton()
        self.sound_filepath_button.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.sound_filepath_line.setText(self.sound_clip_path)

        self.text_input_label = QtWidgets.QLabel("Input txt.file:")
        self.text_filepath_line = QtWidgets.QLineEdit()
        self.text_filepath_button = QtWidgets.QPushButton()
        self.text_filepath_button.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.text_filepath_line.setText(self.text_file_path)

        self.pose_folder_label = QtWidgets.QLabel("Pose folder:")
        self.pose_filepath_line = QtWidgets.QLineEdit()
        self.pose_filepath_button = QtWidgets.QPushButton()
        self.pose_filepath_button.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.pose_filepath_line.setText(self.pose_folder_path)

        self.generate_keys_button = QtWidgets.QPushButton("Generate keyframes")
        self.generate_keys_button.setStyleSheet("background-color: lightgreen; color: black")
        self.save_pose_button = QtWidgets.QPushButton("Save pose")
        self.help_button = QtWidgets.QPushButton("?")
        self.help_button.setFixedWidth(25)
        self.load_pose_button = QtWidgets.QPushButton("Load pose")
        self.close_button = QtWidgets.QPushButton("Close")

        self.separator_line = QtWidgets.QFrame(parent=None)
        self.separator_line.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator_line.setFrameShadow(QtWidgets.QFrame.Sunken)

    def create_ui_layout(self):
        sound_input_row = QtWidgets.QHBoxLayout()
        sound_input_row.addWidget(self.sound_text_label)
        sound_input_row.addWidget(self.sound_filepath_line)
        sound_input_row.addWidget(self.sound_filepath_button)

        text_input_row = QtWidgets.QHBoxLayout()
        text_input_row.addWidget(self.text_input_label)
        text_input_row.addWidget(self.text_filepath_line)
        text_input_row.addWidget(self.text_filepath_button)

        pose_input_row = QtWidgets.QHBoxLayout()
        pose_input_row.addWidget(self.pose_folder_label)
        pose_input_row.addWidget(self.pose_filepath_line)
        pose_input_row.addWidget(self.pose_filepath_button)

        pose_buttons_row = QtWidgets.QHBoxLayout()
        pose_buttons_row.addWidget(self.load_pose_button)
        pose_buttons_row.addWidget(self.save_pose_button)

        bottom_buttons_row = QtWidgets.QHBoxLayout()
        bottom_buttons_row.addWidget(self.generate_keys_button)
        bottom_buttons_row.addWidget(self.close_button)
        bottom_buttons_row.addWidget(self.help_button)


        # Add connection between pose file and phoneme
        pose_widget_layout = QtWidgets.QVBoxLayout()
        for key in list(self.phone_path_dict.keys()):
            pose_connect_widget = PoseConnectWidget(key)
            pose_widget_layout.addWidget(pose_connect_widget)
            pose_connect_widget.set_text(self.get_pose_paths())
            self.widget_list.append(pose_connect_widget)
            
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(sound_input_row)
        main_layout.addLayout(text_input_row)
        main_layout.addWidget(self.separator_line)
        main_layout.addLayout(pose_input_row)
        main_layout.addLayout(pose_buttons_row)
        main_layout.addLayout(pose_widget_layout)
        main_layout.addLayout(bottom_buttons_row)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

    def create_ui_connections(self):
        self.sound_filepath_button.clicked.connect(self.input_sound_dialog)
        self.text_filepath_button.clicked.connect(self.input_text_dialog)
        self.pose_filepath_button.clicked.connect(self.pose_folder_dialog)
        self.save_pose_button.clicked.connect(self.save_pose_dialog)
        self.load_pose_button.clicked.connect(self.load_pose_dialog)
        self.close_button.clicked.connect(self.close_window)
        self.generate_keys_button.clicked.connect(self.generate_animation)
        self.help_button.clicked.connect(self.open_readme)

    def pose_folder_dialog(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select pose folder path", "")
        if folder_path:
            self.pose_filepath_line.setText(folder_path)
            self.pose_folder_path = folder_path
            self.refresh_pose_widgets()

    def input_sound_dialog(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select sound clip", "", "Wav (*.wav);;All files (*.*)")
        if file_path:
            self.sound_filepath_line.setText(file_path[0])
            self.sound_clip_path = file_path[0]

    def save_pose_dialog(self):
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, "Save pose file", self.pose_folder_path, "Pose file (*.json);;All files (*.*)")
        if file_path:
            self.save_pose(file_path[0])
            print("Saved pose: "+file_path[0])

    def load_pose_dialog(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Save pose file", self.pose_folder_path, "Pose file (*.json);;All files (*.*)")
        if file_path:
            self.load_pose(file_path[0])
            print("Loaded pose: "+file_path[0])

    def input_text_dialog(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select dialog transcript", "", "Text (*.txt);;All files (*.*)")
        if file_path:
            self.text_filepath_line.setText(file_path[0])
            self.text_file_path = file_path[0]

    def find_textgrid_file(self):
        path = self.OUTPUT_FOLDER_PATH
        textgrid_files = [os.path.join(dirpath, f)
            for dirpath, dirnames, files in os.walk(path)
            for f in files if f.endswith(".TextGrid")]
        return textgrid_files[0]

    def open_readme(self):
        webbrowser.open_new("https://github.com/joaen/maya_auto_lip_sync/blob/main/README.md")

    def generate_animation(self):
        number_of_operations = 12
        current_operation = 0
        p_dialog = QtWidgets.QProgressDialog("Analyzing the input data and generating keyframes...", "Cancel", 0, number_of_operations, self)
        p_dialog.setWindowFlags(p_dialog.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
        p_dialog.setWindowFlags(p_dialog.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        p_dialog.setCancelButton(None)
        p_dialog.setWindowTitle("Progress...")
        p_dialog.setValue(0)
        p_dialog.setWindowModality(QtCore.Qt.WindowModal)
        p_dialog.show()
        QtCore.QCoreApplication.processEvents()

        self.create_clean_input_folder()
        self.update_phone_paths()
        p_dialog.setValue(current_operation + 1)

        try:
            self.import_sound()
        except:
            cmds.warning("Could not import sound file.")
        p_dialog.setValue(current_operation + 1)

        # Run force aligner
        p = subprocess.Popen(
            ["cmd.exe",
            "/c", "cd {} & mfa_align.exe {} ../librispeech-lexicon.txt ../pretrained_models/english.zip {}".format(self.MFA_PATH, self.INPUT_FOLDER_PATH, self.OUTPUT_FOLDER_PATH)]
            , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        for line in iter(p.stdout.readline, ""):
            print(line)
            current_operation += 1
            p_dialog.setValue(current_operation)
        p.wait()

        try:
            self.create_keyframes()
            print("Successfully generated keyframes.")
            p_dialog.setValue(number_of_operations)
            p_dialog.close()
        except:
            p_dialog.setValue(number_of_operations)
            p_dialog.close()
            OpenMaya.MGlobal_displayError("Could not generate keys: Make sure your input data and poses are correctly set-up.")
        
        self.delete_input_folder()

    def import_sound(self):
        cmds.sound(file=self.sound_clip_path, name="SoundFile")
        gPlayBackSlider = mel.eval("$tmpVar=$gPlayBackSlider")
        cmds.timeControl( gPlayBackSlider, edit=True, sound="SoundFile")

    def delete_input_folder(self):
        try:
            shutil.rmtree(self.INPUT_FOLDER_PATH)
            shutil.rmtree(self.OUTPUT_FOLDER_PATH)
        except:
            pass

    def create_clean_input_folder(self):

        self.delete_input_folder()

        # Create folder
        os.mkdir(self.INPUT_FOLDER_PATH)
        sound_source = self.sound_clip_path
        text_source = self.text_file_path
        destination = self.INPUT_FOLDER_PATH

        # Copy files
        shutil.copy(sound_source, destination)
        shutil.copy(text_source, destination)

        # Rename text file so it matches sound file (Shutil copy doesn't return path in Python2)
        sound_name = ""
        for file in os.listdir(destination):
            if file.endswith(".wav"):
                sound_name = file.split(".")[0]
                
        for file in os.listdir(destination):
            if file.endswith(".txt"):
                old_name = self.INPUT_FOLDER_PATH+"/"+file
                new_name = self.INPUT_FOLDER_PATH+"/"+sound_name+".txt"
                os.rename(old_name, new_name)

    def create_keyframes(self):
            textgrid_path = self.find_textgrid_file()
            tg = textgrid.TextGrid.fromFile(textgrid_path)
            iterations = len(tg[1])

            for i in range(iterations):
                min_time = str(tg[1][i].minTime)
                max_time = str(tg[1][i].maxTime)
                phone = tg[1][i].mark


                # Get the phone pose paths from the dict and load the correlated pose 
                key_value = self.phone_dict.get(phone)
                for k in self.phone_path_dict:
                    if key_value in k:
                        pose_path = self.phone_path_dict.get(k)
                self.load_pose(pose_path)
                cmds.setKeyframe(self.active_controls, time=[min_time+"sec", max_time+"sec"])
                cmds.keyTangent(self.active_controls, inTangentType="spline", outTangentType="spline")

    def save_pose(self, pose_path):
        controllers = cmds.ls(sl=True)
        controller_dict = OrderedDict()
        attr_dict = OrderedDict()

        for ctrl in controllers:
            keyable_attr_list = cmds.listAttr(ctrl, keyable=True, unlocked=True)

            for attr in keyable_attr_list:
                attr_value = cmds.getAttr(ctrl+"."+attr)
                attr_dict[attr] = attr_value

            controller_dict[ctrl] = attr_dict
            attr_dict = {}
        save_path = pose_path

        with open(save_path,"w") as jsonFile:
            json.dump(controller_dict, jsonFile, indent=4)

    def load_pose(self, file_path):
        pose_data = json.load(open(file_path))
        self.active_controls = []
        for ctrl, input in pose_data.iteritems():
            for attr, value in input.iteritems():
                cmds.setAttr(ctrl+"."+attr, value)
            self.active_controls.append(ctrl)

    def get_pose_paths(self):
        pose_list = []
        folder_path = self.pose_folder_path
        try:
            for file in os.listdir(folder_path):
                if file.endswith(".json"):
                    pose_list.append(folder_path+"/"+file)
            return pose_list
        except:
            return pose_list

    def refresh_pose_widgets(self):
        for w in self.widget_list:
            w.clear_box()
            w.set_text(self.get_pose_paths())

    def update_phone_paths(self):
        for index, key in enumerate(self.phone_path_dict):
            self.phone_path_dict[key] = self.widget_list[index].get_text()

    def close_window(self):
        self.close()
        self.deleteLater()


def start():
    global lip_sync_ui
    try:
        lip_sync_ui.close() # type: ignore
        lip_sync_ui.deleteLater() # type: ignore
    except:
        pass
    lip_sync_ui = LipSyncDialog()
    lip_sync_ui.show()

if __name__ == "__main__":
    start()
