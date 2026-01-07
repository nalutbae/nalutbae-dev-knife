#!/usr/bin/env python3
"""
Release script for Nalutbae DevKnife Toolkit

This script handles the release process including version bumping,
building, and uploading to PyPI.
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import Tuple


def run_command(cmd, description, capture_output=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=capture_output, text=True
        )
        if not capture_output:
            print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {cmd}")
        print(f"Return code: {e.returncode}")
        if capture_output:
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
        sys.exit(1)


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    version_match = re.search(r'version = "([^"]+)"', content)
    if not version_match:
        print("❌ Version not found in pyproject.toml")
        sys.exit(1)

    return version_match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string into major, minor, patch components."""
    try:
        parts = version.split(".")
        return int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        print(f"❌ Invalid version format: {version}")
        sys.exit(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch)."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"❌ Invalid bump type: {bump_type}")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def update_version_in_file(new_version: str):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Update version
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)

    pyproject_path.write_text(content)
    print(f"✅ Updated version to {new_version} in pyproject.toml")


def update_changelog(new_version: str):
    """Update CHANGELOG.md with new version."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("⚠️  CHANGELOG.md not found, skipping changelog update")
        return

    content = changelog_path.read_text()

    # Replace [Unreleased] with new version
    today = subprocess.run(
        "date +%Y-%m-%d", shell=True, capture_output=True, text=True
    ).stdout.strip()

    content = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n### Added\n- TBD\n\n### Changed\n- TBD\n\n### Fixed\n- TBD\n\n## [{new_version}] - {today}",
    )

    changelog_path.write_text(content)
    print(f"✅ Updated CHANGELOG.md with version {new_version}")


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command("git status --porcelain", "Checking git status")
    if result.stdout.strip():
        print("❌ Git working directory is not clean. Please commit or stash changes.")
        print("Uncommitted changes:")
        print(result.stdout)
        sys.exit(1)
    print("✅ Git working directory is clean")


def commit_and_tag(version: str):
    """Commit changes and create git tag."""
    run_command(f"git add .", "Staging changes", capture_output=False)
    run_command(
        f'git commit -m "chore: bump version to {version}"',
        "Committing version bump",
        capture_output=False,
    )
    run_command(
        f'git tag -a v{version} -m "Release version {version}"',
        "Creating git tag",
        capture_output=False,
    )
    print(f"✅ Created git tag v{version}")


def build_and_upload(test_pypi: bool = False):
    """Build package and upload to PyPI."""
    # Clean and build
    run_command("python scripts/build.py", "Building package", capture_output=False)

    # Upload
    if test_pypi:
        upload_cmd = "python -m twine upload --repository testpypi dist/*"
        print("📦 Uploading to Test PyPI...")
    else:
        upload_cmd = "python -m twine upload dist/*"
        print("📦 Uploading to PyPI...")

    run_command(upload_cmd, "Uploading package", capture_output=False)


def main():
    """Main release process."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py <bump_type> [--test-pypi]")
        print("bump_type: major, minor, or patch")
        print("--test-pypi: Upload to Test PyPI instead of PyPI")
        sys.exit(1)

    bump_type = sys.argv[1]
    test_pypi = "--test-pypi" in sys.argv

    if bump_type not in ["major", "minor", "patch"]:
        print("❌ Invalid bump type. Use: major, minor, or patch")
        sys.exit(1)

    print("🚀 Starting Nalutbae DevKnife Toolkit release process")
    print("=" * 60)

    # Check git status
    check_git_status()

    # Get current version and calculate new version
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)

    print(f"📋 Current version: {current_version}")
    print(f"📋 New version: {new_version}")
    print(f"📋 Bump type: {bump_type}")
    print(f"📋 Target: {'Test PyPI' if test_pypi else 'PyPI'}")

    # Confirm release
    response = input("\n❓ Continue with release? (y/N): ")
    if response.lower() != "y":
        print("❌ Release cancelled")
        sys.exit(0)

    # Update version
    update_version_in_file(new_version)
    update_changelog(new_version)

    # Commit and tag
    commit_and_tag(new_version)

    # Build and upload
    build_and_upload(test_pypi)

    print("=" * 60)
    print("🎉 Release completed successfully!")
    print(f"\n📦 Version {new_version} has been released!")

    if not test_pypi:
        print("\nNext steps:")
        print("1. Push changes to repository: git push && git push --tags")
        print("2. Create GitHub release with release notes")
        print(
            f"3. Verify installation: pip install nalutbae-dev-knife=={new_version}"
        )
    else:
        print("\nTest PyPI release completed. To test installation:")
        print(
            f"pip install --index-url https://test.pypi.org/simple/ nalutbae-dev-knife=={new_version}"
        )


if __name__ == "__main__":
    main()
