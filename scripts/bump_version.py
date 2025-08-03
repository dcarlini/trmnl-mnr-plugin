#!/usr/bin/env python3
"""
Version bumping utility for TRMNL MNR Plugin.
Similar to composer's version management.

Usage:
    python scripts/bump_version.py 1.1.0        # Release version
    python scripts/bump_version.py 1.2.0b1      # Beta version
    python scripts/bump_version.py 1.2.0-beta   # Alternative beta format
"""

import sys
import re
from pathlib import Path

def update_version_in_file(file_path, pattern, replacement, description):
    """Update version in a specific file."""
    try:
        content = Path(file_path).read_text()
        new_content = re.sub(pattern, replacement, content)
        
        if content != new_content:
            Path(file_path).write_text(new_content)
            print(f"✓ Updated {description}: {file_path}")
            return True
        else:
            print(f"⚠ No changes needed in {description}: {file_path}")
            return False
    except Exception as e:
        print(f"✗ Error updating {description}: {e}")
        return False

def normalize_version(version):
    """Convert version formats (1.1.0-beta -> 1.1.0b1)."""
    # Convert -beta, -alpha, -rc to Python format
    version = re.sub(r'-beta(\d*)', r'b\1', version)
    version = re.sub(r'-alpha(\d*)', r'a\1', version)
    version = re.sub(r'-rc(\d*)', r'rc\1', version)
    
    # Add default beta number if missing
    if version.endswith('b'):
        version += '1'
    
    return version

def get_version_info(version):
    """Parse version string into components."""
    # Parse version like 1.1.0b1
    match = re.match(r'(\d+)\.(\d+)\.(\d+)(?:([ab]|rc)(\d+))?', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    
    major, minor, patch = match.groups()[:3]
    pre_type, pre_num = match.groups()[3:5]
    
    if pre_type:
        pre_label = {"a": "alpha", "b": "beta", "rc": "rc"}[pre_type]
        return f"({major}, {minor}, {patch}, \"{pre_label}\", {pre_num or 1})"
    else:
        return f"({major}, {minor}, {patch})"

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py <version>")
        print("Example: python scripts/bump_version.py 1.1.0")
        print("Example: python scripts/bump_version.py 1.2.0b1")
        sys.exit(1)
    
    new_version = normalize_version(sys.argv[1])
    version_info = get_version_info(new_version)
    
    print(f"Bumping version to: {new_version}")
    print("=" * 50)
    
    # Update all version files
    files_updated = 0
    
    # 1. Update __version__.py
    if update_version_in_file(
        "server/__version__.py",
        r'__version__ = "[^"]*"',
        f'__version__ = "{new_version}"',
        "__version__.py"
    ):
        files_updated += 1
    
    if update_version_in_file(
        "server/__version__.py",
        r'__version_info__ = \([^)]*\)',
        f'__version_info__ = {version_info}',
        "__version__.py (version_info)"
    ):
        files_updated += 1
    
    # 2. Update pyproject.toml
    if update_version_in_file(
        "pyproject.toml",
        r'version = "[^"]*"',
        f'version = "{new_version}"',
        "pyproject.toml"
    ):
        files_updated += 1
    
    # 3. Update setup.py
    if update_version_in_file(
        "setup.py",
        r'version="[^"]*"',
        f'version="{new_version}"',
        "setup.py"
    ):
        files_updated += 1
    
    print("=" * 50)
    print(f"✓ Updated {files_updated} version references")
    print(f"Don't forget to update CHANGELOG.md manually!")
    print(f"Current version: {new_version}")

if __name__ == "__main__":
    main()