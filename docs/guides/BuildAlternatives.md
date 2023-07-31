<a href="https://docs.python-guide.org/shipping/freezing/#freezing-your-code-ref">Freezing</a>
your code is creating a single-file executable file to distribute to end-users, that contains all of your application code as well as the Python interpreter.

Make sure pyinstaller is installed: In pycharm, goto 'Python Packages' and install pyinstaller.

To make a 'one-file' application from the source code:
```
path\to\pyinstaller.exe --onefile --paths path\to\venv\Lib\site-packages --noconsole file.py
```

Note that the --onefile mode slows down the startup of the app significantly (for pyinstaller)

Potential alternatives: 
<a href="https://github.com/Nuitka/Nuitka">Nuitka</a>
/ 
<a href="https://github.com/indygreg/PyOxidizer">PyOxidizer</a>

If it needs to be packaged as an installer instead of a (zip-)file, <a href="https://jrsoftware.org/isinfo.php">innosetup</a> 
could be an option