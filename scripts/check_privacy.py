#!/usr/bin/env python3
"""Reject staged files containing likely personal paths, email addresses, or secrets."""

import argparse
from io import BytesIO
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

SAFE_NAME = "Shanhaijing Project"
SAFE_EMAIL = "noreply@shanhaijing.invalid"
TEXT_SUFFIXES = {
    ".bbmodel", ".gitattributes", ".gitignore", ".html", ".js", ".json",
    ".md", ".py", ".sh", ".svg", ".toml", ".txt", ".yaml", ".yml",
}
PATTERNS = {
    "absolute Windows path": re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),
    "home directory path": re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[^/\s]+"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "common access token": re.compile(r"(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})"),
}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def git(*args):
    return subprocess.check_output(("git", *args), stderr=subprocess.PIPE)


def check_identity(issues):
    expected = f"{SAFE_NAME} <{SAFE_EMAIL}> "
    for kind in ("AUTHOR", "COMMITTER"):
        identity = git("var", f"GIT_{kind}_IDENT").decode("utf-8", "replace")
        if not identity.startswith(expected):
            issues.append(f"Git {kind.lower()} identity is not the project pseudonym")


def check_text(label, data, issues):
    text = data.decode("utf-8", "replace")
    for line_number, line in enumerate(text.splitlines(), 1):
        for description, pattern in PATTERNS.items():
            if pattern.search(line):
                issues.append(f"{label}:{line_number}: {description}")
        if any(not match.group().lower().endswith(".invalid") for match in EMAIL.finditer(line)):
            issues.append(f"{label}:{line_number}: email address")


def check_image(label, data, issues):
    try:
        from PIL import Image
    except ImportError:
        issues.append(f"{label}: Pillow is required to check image metadata")
        return
    try:
        with Image.open(BytesIO(data)) as image:
            for key, value in image.info.items():
                if isinstance(value, str):
                    check_text(f"{label} metadata {key}", value.encode("utf-8"), issues)
                elif isinstance(value, bytes) and len(value) <= 1_000_000:
                    check_text(f"{label} metadata {key}", value, issues)
            for key, value in image.getexif().items():
                check_text(f"{label} EXIF {key}", str(value).encode("utf-8"), issues)
    except Exception as error:
        issues.append(f"{label}: image metadata unreadable ({type(error).__name__})")


def check_file(label, data, issues):
    suffix = PurePosixPath(label).suffix.lower()
    if suffix in TEXT_SUFFIXES or PurePosixPath(label).name in TEXT_SUFFIXES:
        check_text(label, data, issues)
    elif suffix in (".png", ".gif", ".jpg", ".jpeg", ".webp"):
        check_image(label, data, issues)
    elif suffix == ".zip":
        try:
            with zipfile.ZipFile(BytesIO(data)) as archive:
                for entry in archive.infolist():
                    check_text(f"{label} entry name", entry.filename.encode("utf-8"), issues)
                    if entry.is_dir():
                        continue
                    if entry.file_size > 100_000_000:
                        issues.append(f"{label}/{entry.filename}: entry too large to inspect")
                        continue
                    check_file(f"{label}/{entry.filename}", archive.read(entry), issues)
        except zipfile.BadZipFile:
            issues.append(f"{label}: invalid ZIP archive")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="scan every tracked file in the index")
    args = parser.parse_args()
    check_identity_issues = []
    check_identity(check_identity_issues)
    listing = git("ls-files", "--cached", "-z") if args.all else git(
        "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"
    )
    paths = [part.decode("utf-8") for part in listing.split(b"\0") if part]
    issues = check_identity_issues
    for path in paths:
        data = Path(path).read_bytes() if args.all else git("show", ":" + path)
        check_file(path, data, issues)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        print(f"Privacy check failed: {len(issues)} issue(s).", file=sys.stderr)
        return 1
    scope = "tracked working files" if args.all else "staged files"
    print(f"Privacy check passed: {len(paths)} {scope} scanned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
