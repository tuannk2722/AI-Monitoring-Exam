from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REQUIRED = {
    "README.md",
    "AGENTS.md",
    "docs/00-INDEX.md",
    "docs/25-interface-and-data-contracts.md",
    "configs/baseline.yaml",
    "configs/datasets/exam_v0.1.yaml",
    "src/ai_exam_monitoring/data/build_dataset.py",
    "src/ai_exam_monitoring/training/train.py",
    "src/ai_exam_monitoring/evaluation/evaluate.py",
}
FORBIDDEN_TRACKED_SUFFIXES = {
    ".pt", ".pth", ".onnx", ".engine", ".mp4", ".avi", ".mov", ".mkv",
    ".env", ".jpg", ".jpeg", ".png", ".npy", ".pyc", ".pyo", ".pem", ".key", ".p12",
}
FORBIDDEN_TRACKED_DIRS = {
    ".venv", "venv", "__pycache__", "data/raw", "data/interim", "data/processed",
    "artifacts/models", "artifacts/predictions", "artifacts/evidence",
    ".dvc/cache", ".dvc/tmp",
}


def forbidden_path(relative: str) -> bool:
    path = Path(relative)
    name = path.name.lower()
    normalized = relative.lower()
    data_metadata = path.suffix.lower() == ".dvc" or name == ".gitignore"
    return (
        path.suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES
        or name == ".env"
        or (name.startswith(".env.") and name != ".env.example")
        or name in {"credentials.json", "service-account.json", "service_account.json",
                    "token.json", "id_rsa", "id_ed25519"}
        or normalized == ".dvc/config.local"
        or any(normalized.startswith(f"{directory}/") and name != ".gitkeep"
               and not (directory in {"data/raw", "data/interim", "data/processed"}
                        and data_metadata)
               for directory in FORBIDDEN_TRACKED_DIRS)
    )


def tracked_paths(root: Path) -> list[str] | None:
    # A ZIP nested inside another checkout must not inherit that checkout's index.
    # .git can also be a file (Git worktree).
    if not (root / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"],
        check=True, capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="surrogateescape").split("\0")[:-1]


def main(root: Path | None = None, *, require_git: bool = False) -> int:
    root = root or Path(__file__).resolve().parents[1]
    failures: list[str] = []
    for relative in sorted(REQUIRED):
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    try:
        paths = tracked_paths(root)
    except (OSError, subprocess.CalledProcessError):
        failures.append("cannot read Git index; install Git and verify repository access/integrity")
    else:
        if paths is None:
            print("WARNING: no .git metadata (ZIP mode); Git tracking safety NOT verified")
            if require_git:
                failures.append("Git metadata required for tracking safety check")
        else:
            print("Checking Git index (including staged files; ignored/untracked files excluded)")
            for relative in sorted(set(paths)):
                if forbidden_path(relative):
                    failures.append(f"large/sensitive path tracked by Git: {relative}")
    index = root / "docs/00-INDEX.md"
    if index.is_file():
        index_text = index.read_text(encoding="utf-8")
        for number in range(1, 26):
            marker = f"{number:02d}-"
            if marker not in index_text:
                failures.append(f"documentation index does not reference {marker}*")
    for failure in failures:
        print(f"ERROR: {failure}")
    print(f"Repository check complete; failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check repository structure and Git-tracked paths")
    parser.add_argument("--require-git", action="store_true", help="fail in ZIP/no-Git mode")
    sys.exit(main(require_git=parser.parse_args().require_git))
