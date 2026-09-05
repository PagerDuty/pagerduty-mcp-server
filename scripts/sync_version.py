#!/usr/bin/env python3
"""Sync version from pyproject.toml to server.json."""

import json
import tomllib as tomli
from pathlib import Path


def sync_version():
    """Sync version from pyproject.toml to server.json."""
    # Project root is one level up from scripts/
    script_dir = Path(__file__).parent.parent

    # Read version from pyproject.toml
    pyproject_path = script_dir / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
        version = pyproject["project"]["version"]

    # Update server.json with the version
    server_json_path = script_dir / "server.json"
    with open(server_json_path) as f:
        server_config = json.load(f)

    old_version = server_config.get("version", "unknown")
    server_config["version"] = version

    # Also update package version if it exists
    if "packages" in server_config:
        for package in server_config["packages"]:
            package["version"] = version

    with open(server_json_path, "w") as f:
        json.dump(server_config, f, indent=2)
        f.write("\n")  # Add trailing newline

    print(f"✅ Version updated: {old_version} → {version}")
    print(f"   Updated: {server_json_path}")


if __name__ == "__main__":
    sync_version()
