#!/usr/bin/env python3
"""Read-only validation for public file boundaries and historical snapshots (Python 3.11+)."""

import hashlib
import json
import pathlib
import subprocess
import tomllib


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/macos/v1-yabai"


def private_path(path):
    parts = pathlib.PurePosixPath(path).parts
    name = parts[-1].lower()
    blocked_dirs = {".ssh", "ssh", ".aws", ".kube", ".gnupg", "automatic_backups", "backups", ".cache", ".local"}
    blocked_names = {"ssh_config", "known_hosts", "authorized_keys", "fish_variables", ".bash_history", ".zsh_history", ".npmrc", ".netrc", ".pypirc", ".git-credentials"}
    return (
        bool(blocked_dirs.intersection(parts))
        or name in blocked_names
        or name.startswith((".env", "credentials", "id_rsa", "id_ed25519"))
        or name.endswith((".pem", ".key", ".p12", ".pfx", ".keystore", ".log", ".bak", ".local", "_history"))
        or ".config/gh/" in path
        or ".config/gcloud/" in path
        or path.endswith("sketchybar/helper/helper")
    )


def validate():
    errors = []
    inventory = json.loads((PROFILE / "inventory.json").read_text())
    tree = subprocess.check_output(
        ["git", "ls-tree", "-rz", inventory["legacy_base_commit"]], cwd=ROOT
    )
    legacy_records = [record.split(b"\t", 1) for record in tree.split(b"\0") if record]
    inherited = {"archive/legacy-2023/" + name.decode() for _, name in legacy_records}
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).decode().split("\0")
    for path in filter(None, paths):
        # Existing archived state is retained only with its original content, checked below.
        if private_path(path) and path not in inherited:
            errors.append(f"Private/generated path must not be published: {path}")

    recorded = set()
    for entry in inventory["files"]:
        relative = pathlib.PurePosixPath(entry["path"])
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "home":
            errors.append(f"Invalid inventory path: {relative}")
            continue
        if private_path(str(relative)):
            errors.append(f"Private/generated path in snapshot inventory: {relative}")
        path = PROFILE / relative
        if str(relative) in recorded:
            errors.append(f"Duplicate inventory path: {relative}")
        recorded.add(str(relative))
        if path.is_symlink() or not path.is_file():
            errors.append(f"Missing file or unsupported symlink: {relative}")
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            errors.append(f"Snapshot checksum changed: {relative}")
        try:
            text = data.decode("utf-8")
            if path.suffix == ".json":
                json.loads(text)
            if path.suffix == ".toml":
                tomllib.loads(text)
        except (UnicodeDecodeError, ValueError) as error:
            errors.append(f"Invalid snapshot source {relative}: {type(error).__name__}")
    home_paths = list((PROFILE / "home").rglob("*"))
    for path in home_paths:
        if path.is_symlink():
            errors.append(f"Unsupported snapshot symlink: {path.relative_to(PROFILE)}")
    actual = {str(path.relative_to(PROFILE)) for path in home_paths if path.is_file()}
    if actual != recorded:
        errors.append(f"Snapshot inventory mismatch: {sorted(actual ^ recorded)}")

    # Compare Git blob hashes so binary wallpapers are preserved as well as text files.
    legacy_count = 0
    for metadata, name in legacy_records:
        expected = metadata.split()[2].decode()
        path = ROOT / "archive/legacy-2023" / name.decode()
        if not path.is_file():
            errors.append(f"Archived file missing: {name.decode()}")
            continue
        data = path.read_bytes()
        actual_hash = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if actual_hash != expected:
            errors.append(f"Archived content changed: {name.decode()}")
        legacy_count += 1

    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(recorded)} Mac snapshot files and {legacy_count} unchanged legacy files; no blocked paths.")


if __name__ == "__main__":
    assert private_path("profiles/macos/example/home/.ssh/config")
    assert private_path("profiles/macos/example/home/.config/gh/hosts.yml")
    assert private_path("profiles/linux/example/home/.env.production")
    assert not private_path("profiles/macos/v1-yabai/home/.config/karabiner/karabiner.json")
    validate()
