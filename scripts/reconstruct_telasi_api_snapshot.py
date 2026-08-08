#!/usr/bin/env python3
"""Reconstruct and verify the canonical 2026-08-08 Telasi API JSON snapshot."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = ROOT / "data" / "telasi_api" / "raw" / "2026-08-08"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def reconstruct(snapshot_dir: Path) -> bytes:
    manifest = json.loads((snapshot_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    canonical = manifest["canonical_orkhevi_search"]
    parts = []
    for item in canonical["chunks"]:
        data = (snapshot_dir / item["path"]).read_bytes()
        if len(data) != item["bytes"] or sha256(data) != item["sha256"] or git_blob_sha1(data) != item["git_blob_sha1"]:
            raise SystemExit(f"Chunk verification failed: {item['path']}")
        parts.append(data)
    b64 = b"".join(parts)
    if len(b64) != canonical["base64_text_bytes"] or sha256(b64) != canonical["base64_text_sha256"]:
        raise SystemExit("Joined Base64 verification failed")
    gz = base64.b64decode(b64, validate=True)
    if len(gz) != canonical["gzip_bytes"] or sha256(gz) != canonical["gzip_sha256"]:
        raise SystemExit("Gzip verification failed")
    raw = gzip.decompress(gz)
    if len(raw) != canonical["original_json_bytes"] or sha256(raw) != canonical["original_json_sha256"]:
        raise SystemExit("Original JSON verification failed")
    json.loads(raw.decode("utf-8"))
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-dir", default=str(DEFAULT_DIR))
    parser.add_argument("--output", help="Write reconstructed JSON here; omit to verify only")
    args = parser.parse_args()
    raw = reconstruct(Path(args.snapshot_dir))
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        print(f"Verified and wrote {len(raw)} bytes to {path}")
    else:
        print(f"Verified canonical Telasi API snapshot: {len(raw)} bytes, sha256={sha256(raw)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
