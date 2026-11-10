import contextlib
import hashlib
import io
import json
import pathlib
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


if __name__ == "__main__":
    unittest.main()
