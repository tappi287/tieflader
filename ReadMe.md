## Tieflader - Riding slow, riding low

Tieflader - "low-loader" creates layered PSD files from image files dropped
to it's load bed. 
It really is just a GUI for the outstanding libaries 
<a href="https://github.com/mdboom/pytoshop">pytoshop</a> and 
<a href="https://pillow.readthedocs.io/">Pillow</a> 
and many others. The GUI is build in 
<a href="https://www.qt.io/qt-for-python">Qt for Python</a> aka `PySide2`. 


### Let's ride
  - slowly steer your web browsing device towards the
    <a href="https://github.com/tappi287/tiffy/releases">Releases</a> page and download a executable
    for your OS/platform


#### Running Tieflader from your local Python Interpreter
1. Clone this repository
2. Goto <a href="https://python.org">python.org</a> and get Python interpreter 3.7.1 for your OS
3. `path to python/python -m pip install pipenv` to install <a href="https://pipenv.readthedocs.io/">pipenv</a>
4. `path to this project/pipenv update` (the path where you cloned this project and the pipfile lives)
5. `pipenv shell` to activate your newly created virtual environment
6. from the pipenv shell `python tiffy.py` to run this app


#### Building Tiffy with PyInstaller
1. Make sure you can run the app following the instructions above
2. From your venv/pipenv shell run `pyinstaller tiffy_win.spec`
   to eg. build a windows executable directory or `pyinstaller tiffy_osx.spec`
   to build a OSX app package
   
   
##### System Requirements
 [ ] Mac OS X 10.10 Yosemite*
 [ ] Windows 7

*Pillow would like you too
