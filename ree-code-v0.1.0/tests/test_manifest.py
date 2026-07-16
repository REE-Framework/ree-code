from pathlib import Path

from ree.reproducibility import build_manifest, sha256_file


def test_manifest_hashes_file(tmp_path: Path) -> None:
    target = tmp_path / "value.txt"
    target.write_text("REE\n", encoding="utf-8")
    manifest = build_manifest([target], metadata_fields={"purpose": "test"})
    assert manifest["schema"] == "ree-reproducibility-manifest-v1"
    assert manifest["metadata"] == {"purpose": "test"}
    assert manifest["files"][0]["sha256"] == sha256_file(target)
