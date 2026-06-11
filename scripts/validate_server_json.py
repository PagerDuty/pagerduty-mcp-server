#!/usr/bin/env python3
"""Validate server.json against the official MCP registry schema."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import jsonschema


def fetch_schema(schema_url: str) -> dict:
    """Fetch the JSON schema from the given URL."""
    try:
        with urllib.request.urlopen(schema_url) as response:
            return json.loads(response.read())
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"❌ Error fetching schema from {schema_url}: {e}", file=sys.stderr)
        sys.exit(1)


def load_server_json(file_path: Path) -> dict:
    """Load the server.json file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"❌ Error loading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def validate_server_json(server_data: dict, schema: dict) -> None:
    """Validate the server.json data against the schema."""
    try:
        jsonschema.validate(instance=server_data, schema=schema)
        print("✅ server.json is valid!")
        print("\n📦 Server Details:")
        print(f"   Name: {server_data['name']}")
        print(f"   Version: {server_data['version']}")
        print(f"   Description: {server_data['description']}")
        if "packages" in server_data:
            print("\n📦 Packages:")
            for pkg in server_data["packages"]:
                print(f"   - {pkg['registryType']}: {pkg['identifier']} v{pkg['version']}")
    except jsonschema.ValidationError as e:
        print("❌ Validation Error:", file=sys.stderr)
        print(f"   Path: {' -> '.join(str(p) for p in e.path)}", file=sys.stderr)
        print(f"   Message: {e.message}", file=sys.stderr)
        sys.exit(1)
    except (jsonschema.SchemaError, KeyError, TypeError) as e:
        print(f"❌ Unexpected error during validation: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the validation script."""
    # Path to server.json (in project root, one level up from scripts/)
    script_dir = Path(__file__).parent.parent
    server_json_path = script_dir / "server.json"

    if not server_json_path.exists():
        print(f"❌ server.json not found at {server_json_path}", file=sys.stderr)
        sys.exit(1)

    # Load server.json
    print(f"📄 Loading {server_json_path}...")
    server_data = load_server_json(server_json_path)

    # Get schema URL from server.json
    schema_url = server_data.get("$schema")
    if not schema_url:
        print("❌ No $schema field found in server.json", file=sys.stderr)
        sys.exit(1)

    # Fetch the schema
    print(f"📥 Fetching schema from {schema_url}...")
    schema = fetch_schema(schema_url)

    # Validate
    print("🔍 Validating server.json against schema...")
    validate_server_json(server_data, schema)


if __name__ == "__main__":
    main()
