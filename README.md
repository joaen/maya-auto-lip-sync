# Automated lip sync tool for Maya

 A tool used for generating automated lip sync animation on a facial rig in Autodesk: Maya. The script is compatible with Autodesk: Maya 2017 or later (Windows).

 ![](https://joaen.github.io/images/auto-lip-sync.gif)

## Installation:
1. Add the ***auto_lip_sync*** folder or ***auto_lip_sync.py*** to your Maya scripts folder (Username\Documents\maya\*version*\scripts).
2. Download the dependencies needed to run this tool (Download the [Dependencies.zip](https://github.com/joaen/maya_auto_lip_sync/releases/tag/v1.0.0) or read the *Dependencies* section further down).
3. To start the auto lipsync tool in Maya simply execute the following lines of code in the script editor or add them as a shelf button:

```python
import auto_lip_sync
auto_lip_sync.start()
```

## Dependencies
To be able to run this tool you need to download the dependencies which are required to run this tool (Or move the *INSTALLER.bat* to your Maya scripts folder and run it).

* Montreal Forced Aligner version 1.0.1 Win64, by Michael McAuliffe/Montreal Corpus Tools (MIT/Apache). Unzip this folder in your Maya scripts folder:
https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.0.1/montreal-forced-aligner_win64.zip

* Textgrid parser by Kyle Gorman (MIT). Download and move the textgrid folder to your Maya scripts folder:
https://github.com/kylebgorman/textgrid

* Librispeech English pronunciations by Daniel Povey/OpenSLR (Public Domain). Download and place this file inside your montreal-forced-aligner folder:
https://www.openslr.org/resources/11/librispeech-lexicon.txt


## System and file format requirements
* This tool only have support for English input sound and text files.
* Maya 2017+ and Windows is required to run this tool.
* Input transcript file have to be a .txt file or .lab file.
* Input sound file only have support for 16 kHz, single channel .Wav files. You may need to resample your sound file to meet the requirements. I recommend using the free and open-source software Audacity: https://www.audacityteam.org/ 

## How to use the tool
1. Use the *Save pose* function to create 10 separate facial poses (one for each phonome). 
2. Load the folder where the pose files are saved and assign a unique pose to each phonomes in the dropdown boxes.
3. Select a soundclip with a voice-line and a textfile where the voice-line is written down in english.
4. Click *Generate animation* and wait until the process is done. (The length of the audio clip will affect how long it takes to process)

## Preston Blair phoneme series
To be able to generate facial animations you need to create 10 different mouth poses based on the Preston Blair phoneme series.

![](https://github.com/joaen/joaen.github.io/blob/main/images/PrestonBlairPhonemes.png)

## How to save a pose
1. Select the rig controllers you wish to save the attributes from.
2. Click *Save pose* and choose which path you want to save the pose file to.

## How to load a pose
1. Click *Load pose* and select which pose file you wish to load.
2. The stored pose will be applied to the rig controllers referenced in the pose file.

