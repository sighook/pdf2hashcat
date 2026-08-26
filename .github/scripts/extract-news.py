#!/usr/bin/env python3

import re
import sys
from pathlib import Path


HEADING_RE = re.compile(
    r"^##\s+(?:pdf2hashcat\s+)?"
    r"(?P<version>\d+\.\d+\.\d+)"
    r"(?:\s+[—-]\s+.*)?\s*$"
)


def extract_release(text, version):
    lines = text.splitlines(keepends=True)

    starts = []

    for index, line in enumerate(lines):
        match = HEADING_RE.match(line.rstrip("\r\n"))
        if match and match.group("version") == version:
            starts.append(index + 1)

    if not starts:
        raise ValueError(
            f"NEWS.md has no section for version {version}"
        )

    if len(starts) != 1:
        raise ValueError(
            f"NEWS.md has multiple sections for version {version}"
        )

    start = starts[0]
    end = len(lines)

    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break

    body = "".join(lines[start:end]).strip()

    if not body:
        raise ValueError(
            f"NEWS.md section for version {version} is empty"
        )

    return body + "\n"


def main():
    if len(sys.argv) != 4:
        print(
            f"usage: {sys.argv[0]} TAG NEWS OUTPUT",
            file=sys.stderr,
        )
        return 2

    tag, news_path, output_path = sys.argv[1:]

    match = re.fullmatch(r"v(\d+\.\d+\.\d+)", tag)
    if not match:
        print(
            f"error: release tag must be vMAJOR.MINOR.PATCH: {tag}",
            file=sys.stderr,
        )
        return 1

    version = match.group(1)

    try:
        text = Path(news_path).read_text(encoding="utf-8")
        release = extract_release(text, version)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    Path(output_path).write_text(release, encoding="utf-8")

    print(f"release notes: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
