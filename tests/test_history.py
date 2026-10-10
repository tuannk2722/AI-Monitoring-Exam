"""Kiểm archive lossless, collision, hash và đường dẫn khôi phục."""

import tempfile
import unittest
import zipfile
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.history import create, list_files, member_path, restore, show, verify
from ai_exam_monitoring.common.provenance import sha256_file


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = {"data/raw/a.txt": b"same", "data/raw/b.txt": b"same",
                       "docs/note.md": "Nhãn đã duyệt.\n".encode()}
        for relative, payload in self.inputs.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        self.archive = self.root / "archive/history.zip"
        create(self.root, self.archive, self.inputs, name="fixture")
        self.destination = self.root / "restored"

    def test_round_trip_and_content_deduplication(self):
        manifest = verify(self.archive, expected_sha256=sha256_file(self.archive))
        self.assertEqual(len(manifest.files), 3)
        with zipfile.ZipFile(self.archive) as stream:
            self.assertEqual(len(stream.namelist()), 3)
        self.assertEqual(restore(self.archive, self.destination), 3)
        for relative, payload in self.inputs.items():
            self.assertEqual((self.destination / relative).read_bytes(), payload)
        self.assertEqual(restore(self.archive, self.destination), 3)

    def test_show_and_selective_restore(self):
        self.assertEqual(list_files(self.archive, prefixes=("docs",)), ["docs/note.md"])
        self.assertEqual(show(self.archive, "docs/note.md"), "Nhãn đã duyệt.\n")
        self.assertEqual(restore(self.archive, self.destination, prefixes=("data/raw",),
                                 exclude=("data/raw/b.txt",)), 1)
        self.assertTrue((self.destination / "data/raw/a.txt").is_file())
        self.assertFalse((self.destination / "docs").exists())

    def test_collision_is_rejected_before_any_write(self):
        path = self.destination / "docs/note.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"different")
        with self.assertRaises(DataContractError):
            restore(self.archive, self.destination)
        self.assertFalse((self.destination / "data").exists())
        self.assertEqual(path.read_bytes(), b"different")

    def test_unsafe_paths_are_rejected(self):
        for relative in ["../a", "/a", "C:/a", "a\\b", "a//b", "a/./b", "a/"]:
            with self.subTest(relative=relative), self.assertRaises(DataContractError):
                member_path(self.root, relative)

    def test_existing_parent_file_blocks_restore_before_writes(self):
        self.destination.mkdir()
        (self.destination / "docs").write_bytes(b"file")
        with self.assertRaises(DataContractError):
            restore(self.archive, self.destination)
        self.assertFalse((self.destination / "data").exists())

    def test_wrong_archive_hash_and_corrupt_blob_block_restore(self):
        with self.assertRaises(DataContractError):
            restore(self.archive, self.destination, expected_sha256="0" * 64)
        corrupt = self.root / "corrupt.zip"
        with zipfile.ZipFile(self.archive) as source, zipfile.ZipFile(corrupt, "w") as output:
            for name in source.namelist():
                output.writestr(name, source.read(name) if name == "manifest.json" else b"bad")
        with self.assertRaises(DataContractError):
            restore(corrupt, self.destination)
        self.assertFalse(self.destination.exists())

    def test_archive_overwrite_and_unlisted_member_are_rejected(self):
        with self.assertRaises(DataContractError):
            create(self.root, self.archive, self.inputs, name="second")
        with zipfile.ZipFile(self.archive, "a") as stream:
            stream.writestr("extra.txt", b"unlisted")
        with self.assertRaises(DataContractError):
            verify(self.archive)
