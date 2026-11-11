#!/usr/bin/env python3
"""Create a local PAW bug-report draft with an allowlisted diagnostic summary."""

import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import platform
import re
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAYOUTS = {"bsp", "columns", "master", "stack", "float"}


def command(arguments):
    try:
        result = subprocess.run(arguments, capture_output=True, text=True, timeout=5)
        return result.returncode, result.stdout + result.stderr
    except (OSError, subprocess.TimeoutExpired):
        return None, ""


def status_summary(text):
    fields = dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)
    version = fields.get("version", "")
    return {
        "version": version if re.fullmatch(r"[0-9][0-9A-Za-z.+_-]{0,80}", version) else None,
        "trusted": fields.get("trusted") if fields.get("trusted") in {"yes", "no"} else None,
        "bindings": "ok" if fields.get("bindings") == "ok" else "unavailable or problems reported",
        "icon_font": "ok" if fields.get("iconFont") == "ok" else "unavailable or missing",
        "config_error_reported": bool(fields.get("error")),
        "managed_windows": int(fields["windows"]) if fields.get("windows", "").isdigit() else None,
        "stacks": int(fields["stacks"]) if fields.get("stacks", "").isdigit() else None,
    }


def workspace_summary(data):
    if not isinstance(data, list) or not all(isinstance(ws, dict) for ws in data):
        return {"available": False}
    layouts = collections.Counter(ws.get("layout") if isinstance(ws.get("layout"), str) and ws["layout"] in LAYOUTS else "other" for ws in data)
    displays = {ws["displayID"] for ws in data if ws.get("visible") is True and type(ws.get("displayID")) is int and ws["displayID"] > 0}
    return {"available": True, "workspace_count": len(data), "visible_workspaces": sum(ws.get("visible") is True for ws in data), "visible_display_count": len(displays), "layout_counts": dict(sorted(layouts.items()))}


def collect():
    status_code, status = command(["paw", "status"])
    summary = {"captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "macos": platform.mac_ver()[0], "architecture": platform.machine(), "paw_status_available": status_code == 0, "paw": status_summary(status if status_code == 0 else "")}
    summary["version_source"] = "running app" if summary["paw"]["version"] else "unavailable"
    if not summary["paw"]["version"]:
        code, version = command(["paw", "--version"])
        if code == 0:
            summary["paw"]["version"] = status_summary("version: " + version.strip())["version"]
            if summary["paw"]["version"]:
                summary["version_source"] = "CLI binary; running app unavailable"
    query_code, query = command(["paw", "query", "--json"])
    try:
        summary["workspaces"] = workspace_summary(json.loads(query)) if query_code == 0 else {"available": False}
    except ValueError:
        summary["workspaces"] = {"available": False}
    fields = dict(line.split(": ", 1) for line in status.splitlines() if ": " in line)
    config_hash = None
    try:
        config = pathlib.Path(fields["config"])
        if config.is_file() and config.stat().st_size <= 2 * 1024 * 1024:
            config_hash = hashlib.sha256(config.read_bytes()).hexdigest()
    except (KeyError, OSError):
        pass
    summary["config_sha256"] = config_hash
    try:
        inventory = json.loads((ROOT / "profiles/macos/v2-paw/inventory.json").read_text())
        expected = next(entry["sha256"] for entry in inventory["files"] if entry["path"] == "home/.config/paw/config.json5")
        summary["config_matches_saved_v2"] = config_hash == expected if config_hash else None
    except (OSError, ValueError, KeyError, StopIteration):
        summary["config_matches_saved_v2"] = None
    summary["legacy_processes_running"] = {}
    for name in ["yabai", "skhd", "borders"]:
        code, _ = command(["pgrep", "-x", name])
        summary["legacy_processes_running"][name] = code == 0 if code in {0, 1} else None
    binary = shutil.which("paw")
    summary["cli_signature_valid"] = None
    summary["cli_signing"] = "unavailable"
    if binary:
        binary = pathlib.Path(binary).resolve()
        target = next((p for p in binary.parents if p.suffix == ".app"), binary)
        code, _ = command(["codesign", "--verify", "--strict", str(target)])
        summary["cli_signature_valid"] = code == 0 if code is not None else None
        code, detail = command(["codesign", "-dv", str(target)])
        if code == 0:
            summary["cli_signing"] = "ad hoc" if "Signature=adhoc" in detail else "certificate"
    _, swift = command(["swift", "--version"])
    match = re.search(r"Swift version ([0-9.]+)", swift)
    summary["available_swift_version"] = match.group(1) if match else None
    return summary


def capture(output):
    output = pathlib.Path(output).expanduser().resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Keep diagnostics outside the dotfiles repository")
    output.mkdir(parents=True, exist_ok=True)
    folder = pathlib.Path(tempfile.mkdtemp(prefix=datetime.datetime.now().strftime("%Y%m%d-%H%M%S-"), dir=output))
    report = folder / "report.md"
    summary = json.dumps(collect(), indent=2, sort_keys=True)
    report.write_text(f"""# PAW bug report draft

## Reproduction
1. Starting layout/workspace and relevant application versions:
2. Exact key, mouse action or CLI command:
3. What happened:

Expected behavior:
Actual behavior:
Frequency (for example, 3 of 5 attempts):
Earliest known good / first affected PAW build:
Does it reproduce with a minimal config and without Sketchybar hooks?:

## Diagnostic summary
```json
{summary}
```

## Evidence to add after review
Minimal configuration needed, a short relevant log excerpt or a recording.
No raw config, window titles, app names, hostnames, logs or crash reports were
included automatically. Review all attachments before sharing upstream.
Do not post until the reproduction and expected/actual behavior are filled in.
""")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path.home() / "Library/Logs/dotfiles/paw", help="Local output parent, outside the repository")
    args = parser.parse_args()
    try:
        print(capture(args.output))
    except (ValueError, OSError) as error:
        parser.exit(1, f"Diagnostics stopped: {error}\n")


if __name__ == "__main__":
    main()
