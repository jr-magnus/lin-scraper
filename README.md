# LIN scraper
Simple python app for downloading whole board sets in .lin format from 
tournaments and team matches on BBO.

## How to run

#### Requirements
Run this command before running the script to satisfy the requirements:
```bash
pip3 install -r requirements.txt
```

EasyGUI library might need tkinter installed (complains about it only after
running the code). Use your favorite package manager. In Debian based 
system f.e.:
```bash
sudo apt-get install python3-tk
```

After you successfully run the code, the rest should be self-explanatory.

#### Executable
In order to create an executable (if you need that for some reason) 
I recommend [PyInstaller](http://www.pyinstaller.org/). I successfully 
tested this on both my Xubuntu 20.04 and Windows 10 (for a friend).

## Expected further development

 - Asynchronous calls for downloading final LIN files (a WIP on this can be found in a separate branch)
 - Beautify and rework GUI (might need more sophisticated library than 
   EasyGUI)
 - CLI option
