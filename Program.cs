using System.Runtime.InteropServices;

namespace Dimmer;

static class Program
{
    [STAThread]
    static void Main(string[] args)
    {
        int opacity = 50; // default 50% dimming

        if (args.Length > 0)
        {
            if (args[0] == "--help" || args[0] == "-h")
            {
                Console.WriteLine("dimmer.exe [opacity]");
                Console.WriteLine();
                Console.WriteLine("  opacity  Dimming level from 1 (barely dim) to 95 (nearly black).");
                Console.WriteLine("           Default: 50");
                Console.WriteLine();
                Console.WriteLine("Press Ctrl+C in this console to stop dimming.");
                Console.WriteLine("Press Ctrl+Alt+Delete to access Task Manager if the screen is too dark.");
                return;
            }

            if (!int.TryParse(args[0], out opacity) || opacity < 1 || opacity > 95)
            {
                Console.Error.WriteLine("Error: opacity must be an integer from 1 to 95.");
                return;
            }
        }

        Console.WriteLine($"Dimming screen to {opacity}% opacity. Press Ctrl+C to stop.");

        ApplicationConfiguration.Initialize();

        var overlay = new OverlayForm(opacity / 100.0);

        Console.CancelKeyPress += (sender, e) =>
        {
            e.Cancel = false;
            overlay.Invoke(() => overlay.Close());
        };

        Application.Run(overlay);
    }
}

class OverlayForm : Form
{
    // Win32 constants for click-through transparent window
    private const int WS_EX_LAYERED = 0x80000;
    private const int WS_EX_TRANSPARENT = 0x20;
    private const int WS_EX_TOOLWINDOW = 0x80;
    private const int WS_EX_NOACTIVATE = 0x08000000;

    [DllImport("user32.dll")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

    [DllImport("user32.dll")]
    private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

    private const int GWL_EXSTYLE = -20;

    public OverlayForm(double opacity)
    {
        // Borderless, topmost, covers all screens
        FormBorderStyle = FormBorderStyle.None;
        TopMost = true;
        ShowInTaskbar = false;
        BackColor = System.Drawing.Color.Black;
        Opacity = opacity;
        StartPosition = FormStartPosition.Manual;

        // Cover the entire virtual screen (all monitors)
        var bounds = SystemInformation.VirtualScreen;
        Location = new System.Drawing.Point(bounds.X, bounds.Y);
        Size = new System.Drawing.Size(bounds.Width, bounds.Height);
    }

    protected override void OnHandleCreated(EventArgs e)
    {
        base.OnHandleCreated(e);

        // Make the window click-through and hide from Alt+Tab
        int exStyle = GetWindowLong(Handle, GWL_EXSTYLE);
        exStyle |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE;
        SetWindowLong(Handle, GWL_EXSTYLE, exStyle);
    }

    protected override CreateParams CreateParams
    {
        get
        {
            var cp = base.CreateParams;
            cp.ExStyle |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE;
            return cp;
        }
    }
}
