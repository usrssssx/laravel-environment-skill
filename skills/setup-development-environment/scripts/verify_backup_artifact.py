#!/usr/bin/env python3
import argparse
import json
import time
from pathlib import Path


ALLOWED_SUFFIXES = (".sql", ".sql.gz", ".dump", ".backup", ".tar", ".tar.gz")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("backup_path", type=Path)
    parser.add_argument("--max-age-hours", type=float, default=26)
    parser.add_argument("--minimum-bytes", type=int, default=1024)
    args = parser.parse_args()

    if not args.backup_path.exists():
        parser.error("backup_path does not exist")
    candidates = [
        path for path in args.backup_path.rglob("*")
        if path.is_file() and any(path.name.endswith(suffix) for suffix in ALLOWED_SUFFIXES)
    ]
    if not candidates:
        raise SystemExit("no backup artifact found")

    latest = max(candidates, key=lambda path: path.stat().st_mtime)
    stat = latest.stat()
    age_hours = (time.time() - stat.st_mtime) / 3600
    if stat.st_size < args.minimum_bytes:
        raise SystemExit(f"backup artifact is too small: {stat.st_size} bytes")
    if age_hours > args.max_age_hours:
        raise SystemExit(f"backup artifact is stale: {age_hours:.1f} hours")

    print(json.dumps({
        "artifact": str(latest.resolve()),
        "size_bytes": stat.st_size,
        "age_hours": round(age_hours, 2),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
