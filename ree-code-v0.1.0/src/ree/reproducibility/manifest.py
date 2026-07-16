"""Create deterministic file manifests for REE analyses."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections.abc import Iterable, Mapping
from importlib import metadata
from pathlib import Path


def sha256_file(path: str | Path, *, chunk_size: int = 1 << 20) -> str:
    """Return a file's SHA-256 digest."""

    source = Path(path)
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _package_version(name: str) -> str | None:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def build_manifest(
    paths: Iterable[str | Path],
    *,
    metadata_fields: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Build a JSON-serialisable manifest without embedding volatile timestamps."""

    records: list[dict[str, object]] = []
    for item in sorted((Path(path) for path in paths), key=lambda value: str(value)):
        if not item.is_file():
            raise FileNotFoundError(item)
        records.append(
            {
                "path": item.as_posix(),
                "size_bytes": item.stat().st_size,
                "sha256": sha256_file(item),
            }
        )

    packages = {
        name: version for name in ("ree-code", "numpy") if (version := _package_version(name))
    }
    return {
        "schema": "ree-reproducibility-manifest-v1",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": packages,
        "metadata": dict(metadata_fields or {}),
        "files": records,
    }


def write_manifest(
    output: str | Path,
    paths: Iterable[str | Path],
    *,
    metadata_fields: Mapping[str, str] | None = None,
) -> Path:
    """Write a manifest as stable, sorted JSON."""

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(paths, metadata_fields=metadata_fields)
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
