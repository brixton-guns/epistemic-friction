from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from epistemic_friction.validate import ValidationError, run_validation, sha256


class FirstStoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]

    def test_first_stone_passes(self) -> None:
        messages = run_validation(self.root)
        self.assertTrue(any("registry: PASS" in message for message in messages))

    def test_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "epistemic-friction"
            shutil.copytree(self.root, copied)

            registry_path = copied / "cases" / "case-001-transit" / "fact_registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["facts"][0]["text"] = "TAMPERED"
            registry_path.write_text(
                json.dumps(registry, indent=2) + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValidationError, "hash mismatch"):
                run_validation(copied)

    def test_manifest_does_not_hash_itself(self) -> None:
        manifest_path = self.root / "integrity" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertNotIn("integrity/manifest.json", manifest["files"])

    def test_manifest_hashes_are_sha256(self) -> None:
        manifest_path = self.root / "integrity" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for relative, digest in manifest["files"].items():
            self.assertEqual(len(digest), 64)
            self.assertEqual(sha256(self.root / relative), digest)

    def test_manifest_covers_repository_files(self) -> None:
        manifest_path = self.root / "integrity" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected = {
            str(path.relative_to(self.root))
            for path in self.root.rglob("*")
            if path.is_file()
            and path != manifest_path
            and "__pycache__" not in path.parts
        }
        self.assertEqual(set(manifest["files"]), expected)


if __name__ == "__main__":
    unittest.main()
