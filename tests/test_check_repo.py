import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.check_repo import REQUIRED, main


class RepositoryCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in REQUIRED:
            self.write(name, "")
        self.write("docs/00-INDEX.md", "\n".join(f"{n:02d}-doc.md" for n in range(1, 26)))

    def write(self, name: str, content: str = "fixture") -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def init_git(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("Git executable unavailable")
        self.git("init")

    def check(self, *, strict: bool = False) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(self.root, require_git=strict)
        return result, output.getvalue()

    def test_ignored_and_untracked_local_files_are_not_tracked(self) -> None:
        self.init_git()
        self.write(".gitignore", ".venv/\ndata/\n*.pt\n.env\n")
        for name in [".venv/Lib/package.pth", "data/raw/photo.png", "weights.pt", ".env",
                     "untracked.mp4"]:
            self.write(name)
        self.git("add", ".gitignore")
        self.assertEqual(self.check(strict=True)[0], 0)

    def test_force_added_paths_are_rejected_even_if_deleted_on_disk(self) -> None:
        self.init_git()
        self.write(".gitignore", "*\n")
        names = ["weights.PT", "clip with spaces\nnewline.mp4", ".env", ".env.local",
                 ".dvc/config.local", "credentials.json", "private.pem",
                 ".venv/Lib/package.pth", "data/raw/manifest.csv", "model.onnx", "photo.png"]
        for name in names:
            # Windows does not permit newline in filenames.
            if "\n" in name:
                name = name.replace("\n", " ")
            self.write(name)
            self.git("add", "-f", "--", name)
            (self.root / name).unlink()
            with self.subTest(name=name):
                code, output = self.check()
                self.assertEqual(code, 1)
                self.assertIn(name, output)

    def test_safe_templates_pointers_and_placeholders(self) -> None:
        self.init_git()
        for name in [".env.example", "data/raw.dvc", "data/raw/.gitkeep", ".dvc/config"]:
            self.write(name)
            self.git("add", "--", name)
        self.assertEqual(self.check()[0], 0)

    def test_zip_is_explicitly_partial_and_strict_mode_fails(self) -> None:
        self.write(".venv/local.pth")
        code, output = self.check()
        self.assertEqual(code, 0)
        self.assertIn("NOT verified", output)
        self.assertEqual(self.check(strict=True)[0], 1)

    def test_missing_required_file_and_incomplete_index(self) -> None:
        (self.root / "README.md").unlink()
        self.write("docs/00-INDEX.md", "01-only")
        code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("missing required file: README.md", output)
        self.assertIn("does not reference 25-", output)

    def test_git_failure_does_not_fall_back_to_zip(self) -> None:
        (self.root / ".git").mkdir()
        for error in [FileNotFoundError(), subprocess.CalledProcessError(128, "git")]:
            with self.subTest(error=error), patch("scripts.check_repo.subprocess.run",
                                                 side_effect=error):
                self.assertEqual(self.check()[0], 1)

    def test_worktree_git_file_and_nul_delimited_paths(self) -> None:
        self.write(".git", "gitdir: elsewhere")
        result = subprocess.CompletedProcess([], 0, b"safe.txt\0video\nname.mp4\0")
        with patch("scripts.check_repo.subprocess.run", return_value=result):
            code, output = self.check()
        self.assertEqual(code, 1)
        self.assertIn("video\nname.mp4", output)


if __name__ == "__main__":
    unittest.main()
