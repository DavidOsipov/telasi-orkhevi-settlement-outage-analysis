"""Byte-level validation of preserved Telasi API source snapshots."""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Validation failed: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def validate_telasi_snapshots(root: Path) -> None:
    API_SNAPSHOT = root / "data" / "telasi_api" / "raw" / "2026-08-08"
    API_MANIFEST = API_SNAPSHOT / "MANIFEST.json"
    manifest = json.loads(API_MANIFEST.read_text(encoding="utf-8"))
    canonical = manifest["canonical_orkhevi_search"]
    base64_parts = []
    for item in canonical["chunks"]:
        data = (API_SNAPSHOT / item["path"]).read_bytes()
        require(len(data) == item["bytes"], f"API chunk size mismatch: {item['path']}")
        require(sha256(data) == item["sha256"], f"API chunk SHA-256 mismatch: {item['path']}")
        require(git_blob_sha1(data) == item["git_blob_sha1"], f"API chunk Git blob hash mismatch: {item['path']}")
        base64_parts.append(data)
    joined = b"".join(base64_parts)
    require(len(joined) == canonical["base64_text_bytes"], "canonical Base64 length mismatch")
    require(sha256(joined) == canonical["base64_text_sha256"], "canonical Base64 SHA-256 mismatch")
    try:
        gz = base64.b64decode(joined, validate=True)
    except Exception as exc:
        raise SystemExit("Validation failed: canonical Base64 decoding failed") from exc
    require(len(gz) == canonical["gzip_bytes"], "canonical gzip length mismatch")
    require(sha256(gz) == canonical["gzip_sha256"], "canonical gzip SHA-256 mismatch")
    try:
        original = gzip.decompress(gz)
    except OSError as exc:
        raise SystemExit("Validation failed: canonical gzip decompression failed") from exc
    require(len(original) == canonical["original_json_bytes"], "canonical JSON length mismatch")
    require(sha256(original) == canonical["original_json_sha256"], "canonical JSON SHA-256 mismatch")
    doc = json.loads(original.decode("utf-8"))
    content = doc["content"]
    api = doc["api"]
    observed = canonical["observed_response"]
    require(content["listCount"] == observed["content_listCount"] == 17, "canonical content.listCount mismatch")
    require(len(content["list"]) == observed["content_list_length"] == 17, "canonical content.list length mismatch")
    require(api["listCount"] == observed["api_listCount"] == 0, "canonical api.listCount mismatch")
    require(len(api["list"]) == observed["api_list_length"] == 0, "canonical api.list length mismatch")
    require(
        sum(i.get("taxonomy", {}).get("content_poweroutage") == [2770] for i in content["list"]) == observed["taxonomy_2770_rows"] == 13,
        "canonical taxonomy 2770 count mismatch",
    )
    require(
        sum(i.get("taxonomy", {}).get("content_poweroutage") == [2769] for i in content["list"]) == observed["taxonomy_2769_rows"] == 4,
        "canonical taxonomy 2769 count mismatch",
    )

    exploratory = manifest["exploratory_probe_observations"]
    require(exploratory["github_actions_run_id"] == 31253449527, "unexpected exploratory run id")
    require(exploratory["artifact_id"] == 9020698787, "unexpected exploratory artifact id")
    general = next(
        item for item in exploratory["responses"]
        if item["logical_path"].endswith("contenttype-all.response.json.gz.b64")
    )
    require(general["observed_response"]["content_listCount"] == 889, "exploratory reported total mismatch")
    require(general["observed_response"]["content_list_length"] == 100, "exploratory page-1 length mismatch")
    require(
        general["observed_response"]["content_list_length"] < general["observed_response"]["content_listCount"],
        "exploratory general-list response should be explicitly partial",
    )

    mt = manifest["getMtData_probe"]
    mt_bytes = (API_SNAPSHOT / mt["path"]).read_bytes()
    require(len(mt_bytes) == mt["original_json_bytes"], "getMtData size mismatch")
    require(sha256(mt_bytes) == mt["original_json_sha256"], "getMtData SHA-256 mismatch")
    require(git_blob_sha1(mt_bytes) == mt["git_blob_sha1"], "getMtData Git blob hash mismatch")
    mt_doc = json.loads(mt_bytes.decode("utf-8"))
    require("headerObjects" in mt_doc and "placeFillers" in mt_doc, "getMtData expected metadata keys missing")
