"""Run under xvfb-run and dbus-run-session; never changes the real display."""
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from test_safety import load_script, safety

indicator = load_script("dimmer_indicator", "dimmer-indicator")


class ResetIntegrationTests(unittest.TestCase):
    def test_safety_signal_clears_percentage_and_radio_selection(self):
        with tempfile.TemporaryDirectory(prefix="dimmer-test-") as runtime, \
             patch.dict(indicator.os.environ, {"XDG_RUNTIME_DIR": runtime}), \
             patch.object(indicator.DimmerIndicator, "_read_outputs", return_value={"DP-1": "0.80"}), \
             patch.object(indicator.DimmerIndicator, "_xrandr") as change:
            app = indicator.DimmerIndicator()
            try:
                menu = app.indicator.get_menu()
                fifty = next(item for item in menu.get_children() if item.get_label() == "50% dim")
                fifty.set_active(True)
                self.assertEqual(app.indicator.get_label(), "50%")
                self.assertEqual(app._active_opacity, 50)
                change.reset_mock()

                query = ("DP-1 connected primary 1920x1080+0+0\n"
                         "HDMI-1 connected 1280x720+1920+0\n"
                         "DP-2 connected (normal left inverted right)\n"
                         "DP-3 disconnected\n")
                with patch.object(safety.subprocess, "check_output", return_value=query), \
                     patch.object(safety.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as reset:
                    safety.restore_brightness()
                    self.assertEqual([call.args[0] for call in reset.call_args_list], [
                        ("xrandr", "--output", "DP-1", "--brightness", "1.0"),
                        ("xrandr", "--output", "HDMI-1", "--brightness", "1.0"),
                    ])
                deadline = time.monotonic() + 3
                context = indicator.GLib.MainContext.default()
                while app._active_opacity != 0 and time.monotonic() < deadline:
                    context.iteration(False)
                    time.sleep(0.01)
                self.assertEqual(app._active_opacity, 0)
                self.assertTrue(app._off_item.get_active())
                self.assertFalse(fifty.get_active())
                self.assertEqual(app.indicator.get_label(), "Off")
                change.assert_not_called()  # Must not restore the old 0.80 snapshot.

                fifty.set_active(True)
                self.assertEqual(app._active_opacity, 50)
                change.assert_called_once_with("--output", "DP-1", "--brightness", "0.50")
            finally:
                app._bus.signal_unsubscribe(app._reset_subscription)
                app.indicator.set_status(indicator.AppIndicator.IndicatorStatus.PASSIVE)
                app._lock.close()


if __name__ == "__main__":
    unittest.main()
