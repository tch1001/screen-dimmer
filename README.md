# Dimmer

A lightweight Windows tool that dims your screen beyond the minimum brightness available in display settings. Works by placing a transparent black overlay on top of everything.

Useful for external monitors that don't go dim enough, or for comfortable use in very dark environments.

## Features

- Dims all monitors simultaneously
- Click-through overlay — interact with everything underneath normally
- Stays on top of all windows
- Hidden from Alt+Tab and the taskbar
- Ctrl+Alt+Delete always works (Windows secure desktop is unaffected)
- Single self-contained exe, no installation required

## Usage

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

### Stopping

- **Ctrl+C** in the terminal window to exit cleanly
- **Ctrl+Alt+Delete** to reach Task Manager if you can't see the terminal

## Building from source

Requires the [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0).

```powershell
dotnet publish -c Release -r win-x64 --self-contained -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true
```

The exe will be at `bin\Release\net8.0-windows\win-x64\publish\dimmer.exe`.

## How it works

The app creates a borderless, topmost, click-through WinForms window filled with black and set to the requested opacity. The `WS_EX_TRANSPARENT` and `WS_EX_LAYERED` extended window styles make it pass all mouse input through to the windows below.

## License

MIT
