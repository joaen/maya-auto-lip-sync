@echo off
cls
:start
echo:
set movebat="Move the INSTALLER.bat to your Maya scripts folder before you run it. C:\Users\user\Documents\maya\version\scripts."
powershell -command "write-host -fore Black -back Yellow %movebat%"
echo:
echo This installation will download the required dependencies (~150MB)
echo:
set closewin="Close this window if you want to abort the installation, or press any key to start the installation."
powershell -command "write-host -fore Green %closewin%"
echo:
pause

:createfolder
if exist textgrid\ goto install
powershell -command "New-Item -Name 'textgrid' -ItemType 'directory'| Out-Null"

:install
cls
echo:
echo DOWNLOADING DEPENDENCIES ...
echo:

:textgrid
if exist ./textgrid/textgrid.py goto libri
powershell -command "$progressPreference = 'silentlyContinue'; Invoke-WebRequest https://raw.githubusercontent.com/kylebgorman/textgrid/master/textgrid/textgrid.py -OutFile ./textgrid/textgrid.py"
powershell -command "$progressPreference = 'silentlyContinue'; Invoke-WebRequest https://raw.githubusercontent.com/kylebgorman/textgrid/master/textgrid/__init__.py -OutFile ./textgrid/__init__.py"
powershell -command "$progressPreference = 'silentlyContinue'; Invoke-WebRequest https://raw.githubusercontent.com/kylebgorman/textgrid/master/textgrid/exceptions.py -OutFile ./textgrid/exceptions.py"

:libri
if exist librispeech-lexicon.txt goto mfa
powershell -command "$progressPreference = 'silentlyContinue'; Invoke-WebRequest https://www.openslr.org/resources/11/librispeech-lexicon.txt -OutFile librispeech-lexicon.txt"

:mfa
if exist montreal-forced-aligner.zip goto unzip
powershell -command "$progressPreference = 'silentlyContinue'; Invoke-WebRequest https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.0.1/montreal-forced-aligner_win64.zip -OutFile montreal-forced-aligner_win64.zip"

:unzip
if exist montreal-forced-aligner\ goto fail
cls
echo:
echo EXTRACTING ZIP FILE ...
echo:
powershell -command "Expand-Archive -Path montreal-forced-aligner_win64.zip"
powershell -command "Move-Item -Path ./montreal-forced-aligner_win64/montreal-forced-aligner -Destination %CD%"
powershell -command "Move-Item -Path librispeech-lexicon.txt -Destination ./montreal-forced-aligner/"
powershell -command "Remove-Item montreal-forced-aligner_win64"
powershell -command "Remove-Item montreal-forced-aligner_win64.zip"
goto end

:fail
cls
echo:
set failtext="INSTALLATION FAILED! Files already exsist."
powershell -command "write-host -fore Red %failtext%"
timeout 5

:end
cls
echo:
set donetext="DONE! Feel free to delete this .bat file."
powershell -command "write-host -fore Green %donetext%"
timeout 5
