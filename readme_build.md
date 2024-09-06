### Build on windows:
```bash
pip3 install -r requirements_windows.txt
pip3 install pyinstaller
pyinstaller  --onefile --hidden-import win32timezone --version-file=version_info.txt .\windows_client.py
```

### Build on linux:
```bash
pip3 install -r requirements_linux.txt
pip3 install pyinstaller
pyinstaller --onefile --name=linux_client linux_client.py
```