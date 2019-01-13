## Tieflader - Riding slow, riding low

Tieflader - "low-loader" creates layered PSD files from image files dropped
to it's load bed. 
It really is just a GUI for the outstanding libaries 
<a href="https://github.com/mdboom/pytoshop">pytoshop</a> and 
<a href="https://pillow.readthedocs.io/">Pillow</a> 
and a few others. The GUI is build in 
<a href="https://www.qt.io/qt-for-python">Qt for Python</a> aka `PySide2`. 


### Let's ride
  - Slowly steer your web rider towards the
    <b> <a href="https://github.com/tappi287/tieflader/releases">Download Releases</a></b>
    page and download a executable for your OS/platform.
    
    ##
    
    ##### System Requirements
    - [x] Mac OS X 10.10 Yosemite*
    - [x] Windows >= 7
    - [ ] Adobe Photoshop is *not* required

        *`Pillow` *would like you too. Image libraries require* 
        `Intel/AMD x64 CPU` 
        *They have added those to the 
        fruity machines haven't they? Steve?*
##

### Current Limitations
  - Image scaling does not respect aspect ratios, the current version will
  *not* preserve the aspect ratios of input images and forcefully scale
  everything to the size you have set for the Psd document.
  - Just like in Photoshop itself, image down scaling is done without 
  proper gamma conversion. <a href="http://entropymine.com/imageworsener/gamma/">
  Read more about this very common issue
  </a>

##

#### Running Tieflader from your local Python Interpreter
1. Clone this repository
2. Goto <a href="https://python.org">python.org</a> and get Python interpreter 3.7.1 for your OS
3. `<path to python>/python -m pip install pipenv` to install <a href="https://pipenv.readthedocs.io/">pipenv</a>
4. `<path to this project>/pipenv update` (the path where you cloned this project and the pipfile lives)
5. `pipenv shell` to activate your newly created virtual environment
6. from the pipenv shell `python tieflader.py` to run this app


#### Building Tieflader with PyInstaller
1. Make sure you can run the app following the instructions above
2. From your venv/pipenv shell run `pyinstaller tieflader_win.spec`
   to eg. build a windows executable directory or `pyinstaller tieflader_osx.spec`
   to build an OSX app package
   

