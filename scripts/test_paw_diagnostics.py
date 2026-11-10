import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

import paw_diagnostics


class PawDiagnosticsTests(unittest.TestCase):
    def test_summary_drops_private_strings_and_identifiers(self):
        private = "PRIVATE_SENTINEL_DO_NOT_EXPORT"
        with tempfile.TemporaryDirectory() as temporary:
            config = pathlib.Path(temporary) / "config.json5"
            config.write_text(private)
            def run(arguments):
                if arguments == ["paw", "status"]:
                    return 0, f"version: 0.1.0-beta.1+abcdef\ntrusted: yes\nwindows: 7\nstacks: 2\nconfig: {config}\nerror: {private}\nbindings: {private}\niconFont: {private}\n"
                if arguments == ["paw", "query", "--json"]:
                    return 0, json.dumps([{"name": private, "layout": "bsp", "visible": True, "displayID": 987654321, "windows": [{"app": private, "title": private}]}])
                if arguments[:2] == ["swift", "--version"]:
                    return 0, "Apple Swift version 6.3.3 " + private
                return 1, private
            with patch.object(paw_diagnostics, "command", side_effect=run), patch.object(paw_diagnostics.shutil, "which", return_value=None):
                summary = paw_diagnostics.collect()
            encoded = json.dumps(summary)
            self.assertNotIn(private, encoded)
            self.assertNotIn(str(config), encoded)
            self.assertNotIn("987654321", encoded)
            self.assertEqual(summary["paw"]["managed_windows"], 7)
            self.assertEqual(summary["workspaces"]["visible_display_count"], 1)
            self.assertEqual(summary["available_swift_version"], "6.3.3")
            self.assertTrue(summary["paw"]["config_error_reported"])

    def test_missing_tools_and_invalid_query_produce_partial_summary(self):
        with patch.object(paw_diagnostics, "command", return_value=(None, "")), patch.object(paw_diagnostics.shutil, "which", return_value=None):
            summary = paw_diagnostics.collect()
        self.assertFalse(summary["paw_status_available"])
        self.assertFalse(summary["workspaces"]["available"])
        self.assertIsNone(summary["config_sha256"])
        self.assertIsNone(summary["legacy_processes_running"]["skhd"])
        self.assertEqual(paw_diagnostics.workspace_summary({"unexpected": "shape"}), {"available": False})
        self.assertEqual(paw_diagnostics.workspace_summary([{"layout": []}])["layout_counts"], {"other": 1})

    def test_capture_is_private_and_refuses_repository_output(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(paw_diagnostics, "collect", return_value={"example": True}):
            report = paw_diagnostics.capture(temporary)
            self.assertEqual(report.parent.stat().st_mode & 0o777, 0o700)
            self.assertIn("## Reproduction", report.read_text())
            with self.assertRaisesRegex(ValueError, "outside"):
                paw_diagnostics.capture(paw_diagnostics.ROOT / "diagnostics")

    def test_unrecognized_version_or_status_is_not_exported(self):
        summary = paw_diagnostics.status_summary("version: private value with spaces\ntrusted: maybe\nwindows: private\n")
        self.assertIsNone(summary["version"])
        self.assertIsNone(summary["trusted"])
        self.assertIsNone(summary["managed_windows"])

    def test_stopped_app_still_records_cli_version_with_its_origin(self):
        def run(arguments):
            return (0, "0.1.0-beta.1+abcdef\n") if arguments == ["paw", "--version"] else (1, "not running")
        with patch.object(paw_diagnostics, "command", side_effect=run), patch.object(paw_diagnostics.shutil, "which", return_value=None):
            summary = paw_diagnostics.collect()
        self.assertFalse(summary["paw_status_available"])
        self.assertEqual(summary["paw"]["version"], "0.1.0-beta.1+abcdef")
        self.assertIn("CLI binary", summary["version_source"])


if __name__ == "__main__":
    unittest.main()
