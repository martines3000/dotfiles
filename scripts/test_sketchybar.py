import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "profiles/macos/v2-paw/home/.config/sketchybar"


class BarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = pathlib.Path(self.temp.name)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        self.log = self.home / "calls.jsonl"
        self.env = {**os.environ, "HOME": str(self.home), "XDG_CACHE_HOME": str(self.home / "cache"),
                    "CONFIG_DIR": str(CONFIG), "PATH": f"{self.bin}:{os.environ['PATH']}",
                    "CALL_LOG": str(self.log), "NAME": "paw.state", "SENDER": "paw_changed"}
        self.mock("sketchybar", "import json,os,sys\nwith open(os.environ['CALL_LOG'],'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')")
        self.mock("paw", "import os\nprint(os.environ['MOCK_PAW'])")
        self.mock("brew", "import os,sys\nprint(os.environ.get('MOCK_BREW',''),end='')\nsys.exit(int(os.environ.get('BREW_EXIT','0')))")

    def mock(self, name, body):
        path = self.bin / name
        import sys
        path.write_text(f"#!{sys.executable}\n" + body + "\n")
        path.chmod(0o755)

    def run_plugin(self, name):
        return subprocess.run(["bash", str(CONFIG / "plugins" / name)], env=self.env,
                              capture_output=True, text=True)

    def test_workspace_display_mapping_and_focus_only_refresh(self):
        self.env["MOCK_PAW"] = json.dumps([
            {"name": "1", "focused": True, "visible": True, "arrangement": 2,
             "layout": "bsp", "windows": [{"app": "Finder", "focused": True, "floating": True}]},
            {"name": "2", "focused": False, "visible": False, "arrangement": 0,
             "layout": "stack", "windows": []}])
        result = self.run_plugin("paw.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = json.loads(self.log.read_text().splitlines()[-1])
        self.assertIn("display=2", args)
        self.assertIn("display=active", args)
        self.assertIn("label=float", args)
        empty = max(i for i, arg in enumerate(args) if arg == "paw.space.2")
        empty_args = args[empty + 1:]
        empty_args = empty_args[:empty_args.index("--set")]
        self.assertIn("label.drawing=off", empty_args)
        self.assertIn("icon.padding_right=10", empty_args)
        self.env["SENDER"] = "paw_focus"
        self.assertEqual(self.run_plugin("paw.sh").returncode, 0)
        args = json.loads(self.log.read_text().splitlines()[-1])
        self.assertNotIn("paw.space.1", args)
        self.assertIn("label=float", args)

    def test_invalid_workspace_click_is_rejected(self):
        self.env.update(SENDER="mouse.clicked", NAME="paw.space.1; quit")
        self.assertNotEqual(self.run_plugin("paw.sh").returncode, 0)
        self.assertFalse(self.log.exists())

    def test_brew_failure_preserves_stale_count_then_success_clears_it(self):
        cache = self.home / "cache/sketchybar/brew_outdated"
        self.env["MOCK_BREW"] = "one\ntwo\n"
        self.assertEqual(self.run_plugin("brew_refresh.sh").returncode, 0)
        self.assertEqual(cache.read_text().strip(), "2")
        self.env["BREW_EXIT"] = "1"
        self.assertEqual(self.run_plugin("brew_refresh.sh").returncode, 0)
        self.assertEqual(cache.read_text().strip(), "2!")
        self.env.update(NAME="brew", MOCK_BREW="", BREW_EXIT="0")
        self.assertEqual(self.run_plugin("brew.sh").returncode, 0)
        self.assertIn("label=2!", json.loads(self.log.read_text().splitlines()[-1]))
        self.assertEqual(self.run_plugin("brew_refresh.sh").returncode, 0)
        self.assertEqual(cache.read_text().strip(), "0")

    def test_brew_failure_without_cache_is_unknown(self):
        self.env["BREW_EXIT"] = "1"
        self.assertEqual(self.run_plugin("brew_refresh.sh").returncode, 0)
        self.assertEqual((self.home / "cache/sketchybar/brew_outdated").read_text().strip(), "?!")


if __name__ == "__main__":
    unittest.main()
