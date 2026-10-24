# Dimmer

A lightweight tool that dims your screen beyond the minimum brightness available in display settings. Windows uses a transparent black overlay; Linux/X11 uses XRandR software brightness.

Useful for external monitors that don't go dim enough, or for comfortable use in very dark environments.

## Features

- Dims all monitors simultaneously
- Click-through overlay — interact with everything underneath normally
- Stays on top of all windows
- Hidden from Alt+Tab and the taskbar
- Ctrl+Alt+Delete always works (Windows secure desktop is unaffected)
- Single self-contained exe, no installation required

## Usage

### Linux (X11)

No build is required. `xrandr` is included with most X11 desktops (the package is `x11-xserver-utils` on Ubuntu and Debian).

```bash
chmod +x dimmer-linux
./dimmer-linux [opacity]
```

Examples:

```bash
# Default 50% dimming on every connected display
./dimmer-linux

# Dim only an external monitor
./dimmer-linux 70 --output HDMI-1
```

Press **Ctrl+C** to stop and restore each display's previous brightness. Run `xrandr --query` to see output names.

#### GNOME top-bar indicator

The AppIndicator adds a brightness icon to the top bar, with **Off**, **10%**, **25%**, **50%**, **70%**, and **80% dim** choices. If the display becomes uncomfortably dark, press and release either **Alt** key twice within 450 milliseconds to restore full brightness immediately.

Install the dependencies on Ubuntu/Debian:

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 \
    x11-xserver-utils x11-xkb-utils xinput
```

GNOME also needs AppIndicator support; Ubuntu includes the Ubuntu AppIndicators extension. Enable it in the Extensions app if the icon is missing.

Start the shortcut helper and indicator from a terminal in your X11 desktop session:

```bash
./dimmer-safety &
./dimmer-indicator &
```

For automatic startup, put `dimmer-indicator` and `dimmer-safety` on your desktop session's `PATH` (for example, in `~/.local/bin`), then copy both supplied `.desktop` files into `~/.config/autostart/`. If your desktop does not include that directory in `PATH`, set each launcher's `Exec` to the installed script's absolute path. Keep the safety helper running while using the dimmer.

The `dimmer-safety` helper implements the emergency shortcut independently of the top-bar UI, so it remains available even if the indicator stops responding. It listens on the X11 root window without opening a test window. A double-Alt reset restores full brightness and sets the AppIndicator menu to **Off**, clearing its percentage label. Holding Alt or using an Alt shortcut does not count as a double press. You can also run `dimmer-safety --reset` from a terminal.

The Linux version requires an X11 session. On Ubuntu, select **Ubuntu on Xorg** from the gear menu on the login screen. XRandR brightness is not available to native Wayland applications in a compositor-independent way.

### Windows

```
dimmer.exe [opacity]
```

| Argument | Description |
|----------|-------------|
| `opacity` | Dimming level from 1 (barely dim) to 95 (nearly black). Default: 50 |

### Examples

```powershell
# Default 50% dimming
.\dimmer.exe

# Subtle dimming
.\dimmer.exe 20

# Very dark
.\dimmer.exe 80
```

#### Stopping

- **Ctrl+C** in the terminal window to exit cleanly
- **Ctrl+Alt+Delete** to reach Task Manager if you can't see the terminal

## Building the Windows version from source

Requires the [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0).

```powershell
dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true
```

The exe will be at `bin\Release\net8.0-windows\win-x64\publish\dimmer.exe`.

## How it works

On Windows, the app creates a borderless, topmost, click-through WinForms window filled with black and set to the requested opacity. The `WS_EX_TRANSPARENT` and `WS_EX_LAYERED` extended window styles make it pass all mouse input through to the windows below.

On Linux/X11, `dimmer-linux` applies an XRandR brightness multiplier to each connected output. It records the existing values first and restores them on normal exit, Ctrl+C, terminal closure, or termination.

## Linux checks

The tests mock display changes. The indicator test also uses an isolated X server and session bus; install `xvfb`, `xauth`, and `dbus` to run it.

```bash
bash test/dimmer-linux-test.sh
/usr/bin/python3 -m unittest discover -s test -p test_safety.py -v
NO_AT_BRIDGE=1 GIO_USE_VFS=local /usr/bin/dbus-run-session -- xvfb-run -a \
    /usr/bin/python3 -m unittest discover -s test -p test_indicator_reset.py -v
```

## License

MIT
