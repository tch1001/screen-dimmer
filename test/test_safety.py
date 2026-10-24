import importlib.machinery
import importlib.util
from pathlib import Path
import unittest


def load_script(name, filename):
    loader = importlib.machinery.SourceFileLoader(name, str(Path(__file__).resolve().parents[1] / filename))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


safety = load_script("dimmer_safety", "dimmer-safety")


class DoubleAltTests(unittest.TestCase):
    def setUp(self):
        self.detector = safety.DoubleAlt({64, 108})

    def feed(self, *events):
        return [self.detector.feed(*event) for event in events]

    def test_both_alt_keys_and_mixed_pair(self):
        for first, second in ((64, 64), (108, 108), (64, 108)):
            with self.subTest(first=first, second=second):
                self.setUp()
                self.assertEqual(self.feed(("RawKeyPress", first, 1.0),
                                           ("RawKeyRelease", first, 1.1),
                                           ("RawKeyPress", second, 1.2)), [False, False, True])

    def test_holding_and_repeat_do_not_reset(self):
        self.assertEqual(self.feed(("RawKeyPress", 64, 1.0),
                                   ("RawKeyPress", 64, 1.1),
                                   ("RawKeyPress", 64, 1.2)), [False] * 3)

    def test_alt_tab_cancels_sequence(self):
        self.assertFalse(any(self.feed(("RawKeyPress", 64, 1.0),
                                      ("RawKeyPress", 23, 1.1),
                                      ("RawKeyRelease", 64, 1.2),
                                      ("RawKeyPress", 64, 1.3))))

    def test_slow_taps_do_not_reset(self):
        self.assertFalse(any(self.feed(("RawKeyPress", 64, 1.0),
                                      ("RawKeyRelease", 64, 1.1),
                                      ("RawKeyPress", 64, 1.6))))

    def test_two_alt_keys_held_together_do_not_reset(self):
        self.assertFalse(any(self.feed(("RawKeyPress", 64, 1.0),
                                      ("RawKeyPress", 108, 1.1))))

    def test_other_event_types_do_not_reuse_previous_key_event(self):
        self.assertFalse(any(self.feed(("RawKeyPress", 64, 1.0),
                                      ("KeyRelease", 64, 1.1),
                                      ("RawKeyPress", 64, 1.2))))


if __name__ == "__main__":
    unittest.main()
