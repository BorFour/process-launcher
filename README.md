# Process launcher
Create groups with command lines and launch them all together!

## Credits

Using [Font Awesome's](https://fontawesome.com/license) icons!

## Dependencies

- **PyQt 5**: used to create all the widgets and the window
- **pipreqs**: used to install the Python3 requirements

### Linux
- **konsole**: terminal used to run the commands defined in the tables
- **wmctrl**: tool used to get the window ID of a process
- **xdotool**: tool used to minimize and restore the windows

## Install

### Python dependencies
```bash
pipreqs --force .
sudo pip3 install -r requirements.txt
```

### Deploy in your system
```bash
sudo -H pip3 install --upgrade .
```

## Run

### From the root of the project

```bash
./main.py <profile>.json
```

### Anywhere after installing it in the system

```bash
process_launcher <profile>.json
```
