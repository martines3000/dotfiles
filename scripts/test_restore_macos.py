import contextlib
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import restore_macos


class MacRestoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name).resolve()
        self.profile = self.root / "profile"
        self.target = self.root / "home"
        self.target.mkdir()
        entries = []
        for name, content in [(".zshrc", "new shell\n"), (".config/example/settings.toml", 'theme = "new"\n')]:
            source = self.profile / "home" / name
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(content)
            entries.append({"path": "home/" + name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
        (self.profile / "inventory.json").write_text(json.dumps({"files": entries}))
        self.original = self.target / ".zshrc"
        self.original.write_text("original shell\n")
        patcher = patch.object(restore_macos, "PROFILE", self.profile)
        patcher.start()
        self.addCleanup(patcher.stop)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def test_preview_writes_nothing(self):
        restore_macos.restore(self.target)
        self.assertEqual(self.original.read_text(), "original shell\n")
        self.assertEqual(list(self.target.iterdir()), [self.original])

    def test_apply_backs_up_and_second_apply_is_noop(self):
        backup = restore_macos.restore(self.target, apply=True)
        self.assertEqual((backup / "files/.zshrc").read_text(), "original shell\n")
        self.assertEqual(self.original.read_text(), "new shell\n")
        self.assertIsNone(restore_macos.restore(self.target, apply=True))

    def test_rollback_restores_old_files_and_removes_new_files(self):
        backup = restore_macos.restore(self.target, apply=True)
        restore_macos.rollback(self.target, backup)
        self.assertEqual(self.original.read_text(), "new shell\n")
        restore_macos.rollback(self.target, backup, apply=True)
        self.assertEqual(self.original.read_text(), "original shell\n")
        self.assertFalse((self.target / ".config/example/settings.toml").exists())
        restore_macos.rollback(self.target, backup, apply=True)

    def test_rollback_refuses_later_user_edits_before_any_write(self):
        backup = restore_macos.restore(self.target, apply=True)
        (self.target / ".config/example/settings.toml").write_text('theme = "user edit"\n')
        with self.assertRaisesRegex(ValueError, "Changed since restore"):
            restore_macos.rollback(self.target, backup, apply=True)
        self.assertEqual(self.original.read_text(), "new shell\n")

    def test_symlink_parent_is_refused_before_any_write(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.target / ".config").symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            restore_macos.restore(self.target, apply=True)
        self.assertEqual(self.original.read_text(), "original shell\n")
        self.assertFalse(list(elsewhere.iterdir()))

    def test_tampered_source_is_refused_before_any_write(self):
        (self.profile / "home/.zshrc").write_text("changed without inventory\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            restore_macos.restore(self.target, apply=True)
        self.assertEqual(self.original.read_text(), "original shell\n")

    def test_repository_cannot_be_target(self):
        with self.assertRaisesRegex(ValueError, "outside this repository"):
            restore_macos.restore(restore_macos.ROOT, apply=True)

    def test_explicit_profile_uses_its_source_and_records_selection(self):
        older = self.root / "v1-yabai"
        (older / "home").mkdir(parents=True)
        source = older / "home/.zshrc"
        source.write_text("older shell\n")
        (older / "inventory.json").write_text(json.dumps({"files": [{"path": "home/.zshrc", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}]}))
        backup = restore_macos.restore(self.target, apply=True, profile=older)
        self.assertEqual(self.original.read_text(), "older shell\n")
        self.assertFalse((self.target / ".config/example/settings.toml").exists())
        self.assertEqual(json.loads((backup / "receipt.json").read_text())["profile"], "v1-yabai")
        restore_macos.rollback(self.target, backup, apply=True)
        self.assertEqual(self.original.read_text(), "original shell\n")

    def test_same_bytes_with_different_mode_are_restored_and_reversible(self):
        self.original.write_text("new shell\n")
        self.original.chmod(0o600)
        (self.profile / "home/.zshrc").chmod(0o755)
        backup = restore_macos.restore(self.target, apply=True)
        self.assertEqual(self.original.stat().st_mode & 0o777, 0o755)
        restore_macos.rollback(self.target, backup, apply=True)
        self.assertEqual(self.original.stat().st_mode & 0o777, 0o600)

    def test_rollback_cannot_escape_backup_directory_with_parent_components(self):
        base = self.target / "Library/Application Support/dotfiles/backups"
        base.mkdir(parents=True)
        rogue = base.parent / "rogue"
        rogue.mkdir()
        (rogue / "receipt.json").write_text(json.dumps({"target": str(self.target), "files": []}))
        with self.assertRaisesRegex(ValueError, "inside its target"):
            restore_macos.rollback(self.target, base / "../rogue", apply=True)


class SavedProfileRoundTripTests(unittest.TestCase):
    def test_saved_v2_to_v1_and_undo_preserves_experiments_and_other_data(self):
        profiles = restore_macos.ROOT / "profiles/macos"
        with tempfile.TemporaryDirectory() as temporary, contextlib.redirect_stdout(io.StringIO()):
            target = pathlib.Path(temporary).resolve()
            restore_macos.restore(target, apply=True, profile=profiles / "v2-paw")
            bar = target / ".config/sketchybar/sketchybarrc"
            bar.write_text(bar.read_text() + "\n# experimental bar setting\n")
            paw = target / ".config/paw/config.json5"
            paw.write_text(paw.read_text() + "\n// experimental PAW setting\n")
            v2 = json.loads((profiles / "v2-paw/inventory.json").read_text())["files"]
            before = {entry["path"]: (target / pathlib.Path(entry["path"]).relative_to("home")).read_bytes() for entry in v2}
            unrelated = target / "personal-document.txt"
            unrelated.write_text("unrelated content\n")

            backup = restore_macos.restore(target, apply=True, profile=profiles / "v1-yabai")
            v1 = json.loads((profiles / "v1-yabai/inventory.json").read_text())["files"]
            for entry in v1:
                destination = target / pathlib.Path(entry["path"]).relative_to("home")
                self.assertEqual(hashlib.sha256(destination.read_bytes()).hexdigest(), entry["sha256"])
            self.assertEqual(paw.read_bytes(), before["home/.config/paw/config.json5"])
            self.assertIsNone(restore_macos.restore(target, apply=True, profile=profiles / "v1-yabai"))
            restore_macos.rollback(target, backup, apply=True)
            for path, content in before.items():
                self.assertEqual((target / pathlib.Path(path).relative_to("home")).read_bytes(), content)
            self.assertFalse((target / ".skhdrc").exists())
            self.assertEqual(unrelated.read_text(), "unrelated content\n")

    def test_cli_v1_preview_and_invalid_profile_selection(self):
        script = pathlib.Path(restore_macos.__file__)
        with tempfile.TemporaryDirectory() as temporary:
            preview = subprocess.run([sys.executable, str(script), "--profile", "v1-yabai", "--target", temporary], capture_output=True, text=True)
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertIn(".skhdrc", preview.stdout)
            self.assertNotIn(".config/paw/config.json5", preview.stdout)
            self.assertFalse(list(pathlib.Path(temporary).iterdir()))
            for arguments in [["--profile", "../other"], ["--profile", "v1-yabai", "--rollback", temporary]]:
                result = subprocess.run([sys.executable, str(script), *arguments, "--target", temporary], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
