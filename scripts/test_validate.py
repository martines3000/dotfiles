import contextlib
import hashlib
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import validate


class SnapshotValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.git("init", "-q")
        original = self.root / "legacy.txt"
        original.write_bytes(b"original archive\0binary data")
        self.git("add", "legacy.txt")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "baseline")
        base = self.git("rev-parse", "HEAD").strip()
        archive = self.root / "archive/legacy-2023"
        archive.mkdir(parents=True)
        self.git("mv", "legacy.txt", "archive/legacy-2023/legacy.txt")
        self.profile = self.root / "profiles/macos/v1-yabai"
        self.source = self.profile / "home/settings.toml"
        self.source.parent.mkdir(parents=True)
        self.source.write_text('theme = "example"\n')
        self.inventory = {
            "legacy_base_commit": base,
            "files": [{"path": "home/settings.toml", "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest()}],
        }
        self.write_inventory()
        for name, value in [("ROOT", self.root), ("PROFILE", self.profile)]:
            patcher = patch.object(validate, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True)

    def write_inventory(self):
        (self.profile / "inventory.json").write_text(json.dumps(self.inventory))

    def test_valid_snapshot_preserves_binary_archive(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validate.validate()

    def test_changed_snapshot_is_rejected(self):
        self.source.write_text('theme = "changed"\n')
        with self.assertRaisesRegex(SystemExit, "Snapshot checksum changed"):
            validate.validate()

    def test_changed_archive_is_rejected(self):
        (self.root / "archive/legacy-2023/legacy.txt").write_text("changed")
        with self.assertRaisesRegex(SystemExit, "Archived content changed"):
            validate.validate()

    def test_private_path_is_rejected_even_when_in_inventory(self):
        (self.root / ".gitignore").write_text(".ssh/\n")
        private = self.profile / "home/.ssh/config"
        private.parent.mkdir()
        private.write_text("example\n")
        self.inventory["files"].append({"path": "home/.ssh/config", "sha256": hashlib.sha256(private.read_bytes()).hexdigest()})
        self.write_inventory()
        with self.assertRaisesRegex(SystemExit, "Private/generated path"):
            validate.validate()


if __name__ == "__main__":
    unittest.main()
