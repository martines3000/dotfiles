#!/usr/bin/env python3
"""Preview/copy macOS v2 configuration; never install packages or start services."""

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import shutil
import stat
import sys
import tempfile

from validate import ROOT, private_path, validate_snapshot

PROFILE = ROOT / "profiles/macos/v2-paw"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_destination(target, relative):
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Destination must stay inside its target")
    path = target / relative
    for parent in [path, *path.parents]:
        if parent == target.parent:
            break
        if parent.is_symlink():
            raise ValueError(f"Refusing symlink destination: {parent}")
        if parent != path and parent.exists() and not parent.is_dir():
            raise ValueError(f"Destination parent is not a directory: {parent}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Destination is not a regular file: {path}")
    return path


def copy_atomic(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".dotfiles-", dir=destination.parent)
    os.close(fd)
    temporary = pathlib.Path(name)
    try:
        shutil.copy2(source, temporary)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def restore(target, apply=False):
    target = pathlib.Path(target).expanduser().resolve()
    if target.is_relative_to(ROOT):
        raise ValueError("The restore target must be outside this repository")
    if target == pathlib.Path.home().resolve() and apply and sys.platform != "darwin":
        raise ValueError("Restoring the real home directory requires macOS")
    changes = []
    for entry in validate_snapshot(PROFILE):
        relative = pathlib.Path(entry["path"]).relative_to("home")
        destination = check_destination(target, relative)
        source = PROFILE / entry["path"]
        after_mode = stat.S_IMODE(source.stat().st_mode)
        if destination.exists() and digest(destination) == entry["sha256"] and (destination.stat().st_mode & 0o111) == (after_mode & 0o111):
            continue
        before = digest(destination) if destination.exists() else None
        before_mode = stat.S_IMODE(destination.stat().st_mode) if before else None
        changes.append((relative, source, destination, before, entry["sha256"], before_mode, after_mode))
        print(f"{'REPLACE' if before else 'CREATE '} {relative}")
    if not apply or not changes:
        print(f"{len(changes)} change(s)." + (" Preview only; use --apply to copy." if not apply else ""))
        return None

    backup_root = target / "Library/Application Support/dotfiles/backups"
    check_destination(target, pathlib.Path("Library/Application Support/dotfiles/backups/.probe"))
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = pathlib.Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime("%Y%m%d-%H%M%S-"), dir=backup_root))
    backup.chmod(0o700)
    receipt = {"target": str(target), "files": []}
    for relative, source, destination, before, after, before_mode, after_mode in changes:
        receipt["files"].append({"path": str(relative), "before": before, "after": after, "before_mode": before_mode, "after_mode": after_mode})
        if before:
            copy_atomic(destination, backup / "files" / relative)
    # Save recovery information before the first destination write.
    (backup / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Recovery record: {backup}")
    for _, source, destination, *_ in changes:
        copy_atomic(source, destination)
    print(f"Copied {len(changes)} file(s).")
    return backup


def rollback(target, backup, apply=False):
    target = pathlib.Path(target).expanduser().resolve()
    backup = pathlib.Path(backup).expanduser().absolute()
    if target.is_relative_to(ROOT):
        raise ValueError("The restore target must be outside this repository")
    if target == pathlib.Path.home().resolve() and apply and sys.platform != "darwin":
        raise ValueError("Restoring the real home directory requires macOS")
    backup_root = target / "Library/Application Support/dotfiles/backups"
    if not backup.is_relative_to(backup_root) or backup.is_symlink():
        raise ValueError("Recovery record must be under this target's dotfiles backup directory")
    check_destination(target, (backup / "receipt.json").relative_to(target))
    receipt = json.loads((backup / "receipt.json").read_text())
    if receipt["target"] != str(target):
        raise ValueError("Recovery record belongs to a different target")
    changes = []
    for entry in receipt["files"]:
        relative = pathlib.Path(entry["path"])
        if not relative.parts or relative.is_absolute() or ".." in relative.parts or private_path(str(relative)):
            raise ValueError("Invalid recovery path")
        destination = check_destination(target, relative)
        current = digest(destination) if destination.exists() else None
        mode = stat.S_IMODE(destination.stat().st_mode) if current else None
        if (current, mode) == (entry["before"], entry["before_mode"]):
            continue  # Already original, including files not reached by an interrupted copy.
        # Only undo this restore's unchanged output; preserve any later user edits.
        if (current, mode) != (entry["after"], entry["after_mode"]):
            raise ValueError(f"Changed since restore; review manually: {relative}")
        source = backup / "files" / relative
        if entry["before"]:
            check_destination(target, source.relative_to(target))
            if digest(source) != entry["before"] or stat.S_IMODE(source.stat().st_mode) != entry["before_mode"]:
                raise ValueError(f"Backup checksum changed: {relative}")
        changes.append((destination, source, entry["before"]))
        print(f"{'RESTORE' if entry['before'] else 'REMOVE '} {relative}")
    if apply:
        for destination, source, before in changes:
            if before:
                copy_atomic(source, destination)
            else:
                destination.unlink()
    print(f"{len(changes)} rollback change(s)." + (" Preview only; use --apply to undo." if not apply else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=pathlib.Path, default=pathlib.Path.home(), help="Destination home directory; use a disposable directory for testing")
    parser.add_argument("--apply", action="store_true", help="Copy files after preflight; default is preview only")
    parser.add_argument("--rollback", type=pathlib.Path, help="Preview/undo an unchanged restore using its recovery directory")
    args = parser.parse_args()
    try:
        if args.rollback:
            rollback(args.target, args.rollback, args.apply)
        else:
            restore(args.target, args.apply)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Restore stopped: {error}\n")


if __name__ == "__main__":
    main()
