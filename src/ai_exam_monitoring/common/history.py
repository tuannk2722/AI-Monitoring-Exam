"""Lưu lịch sử lossless theo SHA-256 và khôi phục path gốc, không ghi đè."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import IO

from .errors import DataContractError
from .provenance import sha256_file


@dataclass(frozen=True)
class HistoryFile:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True)
class HistoryManifest:
    schema_version: int
    name: str
    files: tuple[HistoryFile, ...]


def member_path(root: Path, relative: str) -> Path:
    """Chặn traversal, path Windows đặc biệt và symlink thoát destination."""
    parts = PurePosixPath(relative)
    if (not relative or parts.as_posix() != relative or parts.is_absolute()
            or "\\" in relative or ":" in relative
            or "\x00" in relative or any(p in {".", ".."} for p in relative.split("/"))):
        raise DataContractError(f"Path lịch sử không an toàn: {relative!r}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise DataContractError("Path lịch sử thoát destination")
    return path


def _copy(stream: IO[bytes], output: IO[bytes] | None = None) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
        size += len(block)
        if output is not None:
            output.write(block)
    return digest.hexdigest(), size


def _manifest(stream: zipfile.ZipFile) -> HistoryManifest:
    if stream.getinfo("manifest.json").file_size > 20_000_000:
        raise DataContractError("Manifest lịch sử quá lớn")
    value = json.loads(stream.read("manifest.json"))
    if (not isinstance(value, dict) or set(value) != {"schema_version", "name", "files"}
            or value["schema_version"] != 1 or not isinstance(value["name"], str)
            or not isinstance(value["files"], list)):
        raise DataContractError("Schema manifest lịch sử không hợp lệ")
    rows = []
    seen: set[str] = set()
    for row in value["files"]:
        if (not isinstance(row, dict) or set(row) != {"path", "sha256", "size"}
                or not isinstance(row["path"], str) or not isinstance(row["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                or type(row["size"]) is not int or row["size"] < 0):
            raise DataContractError("File entry lịch sử không hợp lệ")
        member_path(Path.cwd(), row["path"])
        key = row["path"].casefold()
        if key in seen:
            raise DataContractError("Path lịch sử trùng hoặc khác case")
        seen.add(key)
        rows.append(HistoryFile(**row))
    names = stream.namelist()
    expected = {"manifest.json"} | {f"blobs/{r.sha256}" for r in rows}
    if len(names) != len(set(names)) or set(names) != expected:
        raise DataContractError("Inventory ZIP khác manifest hoặc có duplicate member")
    return HistoryManifest(1, value["name"], tuple(rows))


def create(
    root: Path, output: Path, paths: Iterable[str], *, name: str,
    progress: Callable[[int], None] | None = None,
) -> HistoryManifest:
    """Snapshot trước mutation; mỗi nội dung chỉ lưu một blob, kiểm hash lúc copy."""
    root = root.resolve()
    output = output.resolve()
    partial = output.with_suffix(output.suffix + ".partial")
    if (not output.is_relative_to(root / "archive") or output.exists() or partial.exists()):
        raise DataContractError("Archive phải file mới dưới archive/, không ghi đè")
    relatives = sorted(set(paths))
    files = []
    for relative in relatives:
        path = member_path(root, relative)
        if not path.is_file() or path == output or path == partial:
            raise DataContractError(f"Input lịch sử thiếu/không hợp lệ: {relative}")
        files.append(HistoryFile(relative, sha256_file(path), path.stat().st_size))
    if len({f.path.casefold() for f in files}) != len(files):
        raise DataContractError("Input path khác case không portable")
    manifest = HistoryManifest(1, name, tuple(files))
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as stream:
            written: set[str] = set()
            for i, entry in enumerate(files, 1):
                if entry.sha256 not in written:
                    source = member_path(root, entry.path)
                    compressed = source.suffix.lower() in {
                        ".png", ".jpg", ".jpeg", ".webp", ".zip", ".gz", ".pt", ".pth",
                    }
                    info = zipfile.ZipInfo(f"blobs/{entry.sha256}")
                    info.compress_type = zipfile.ZIP_STORED if compressed else zipfile.ZIP_DEFLATED
                    with (source.open("rb") as original,
                          stream.open(info, "w", force_zip64=True) as blob):
                        actual = _copy(original, blob)
                    if actual != (entry.sha256, entry.size):
                        raise DataContractError(f"Input đổi trong lúc snapshot: {entry.path}")
                    written.add(entry.sha256)
                if progress is not None and i % 1000 == 0:
                    progress(i)
            stream.writestr("manifest.json", json.dumps(asdict(manifest), ensure_ascii=False,
                                                        separators=(",", ":")))
        partial.replace(output)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return manifest


def verify(archive: Path, *, expected_sha256: str | None = None) -> HistoryManifest:
    """Kiểm toàn bộ blob SHA/size; không decode ảnh, chạy model hay extract."""
    if expected_sha256 is not None and sha256_file(archive) != expected_sha256:
        raise DataContractError("Archive SHA khác index")
    with zipfile.ZipFile(archive) as stream:
        manifest = _manifest(stream)
        checked: dict[str, int] = {}
        for entry in manifest.files:
            if entry.sha256 not in checked:
                with stream.open(f"blobs/{entry.sha256}") as blob:
                    digest, size = _copy(blob)
                if digest != entry.sha256:
                    raise DataContractError(f"Blob SHA khác manifest: {entry.path}")
                checked[digest] = size
            if checked[entry.sha256] != entry.size:
                raise DataContractError(f"Blob size khác manifest: {entry.path}")
    return manifest


def _matches(relative: str, prefixes: Iterable[str]) -> bool:
    return any(relative == prefix.rstrip("/")
               or relative.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)


def restore(
    archive: Path, destination: Path, *, prefixes: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (), expected_sha256: str | None = None,
) -> int:
    """Verify trước; từ chối collision trước ghi; chỉ restore paths được chọn."""
    manifest = verify(archive, expected_sha256=expected_sha256)
    destination = destination.resolve()
    selected = [r for r in manifest.files if (not prefixes or _matches(r.path, prefixes))
                and not _matches(r.path, exclude)]
    for row in selected:
        path = member_path(destination, row.path)
        if path.exists() and (not path.is_file() or sha256_file(path) != row.sha256):
            raise DataContractError(f"Không overwrite path khác nội dung: {row.path}")
        for parent in path.parents:
            if parent.exists() and not parent.is_dir():
                raise DataContractError(f"Parent không phải thư mục: {row.path}")
            if parent == destination:
                break
    with zipfile.ZipFile(archive) as stream:
        for row in selected:
            path = member_path(destination, row.path)
            if path.is_file():
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            # xb chặn writer khác; path được resolve lại sau tạo parent để chặn symlink.
            path = member_path(destination, row.path)
            with stream.open(f"blobs/{row.sha256}") as blob, path.open("xb") as output:
                actual = _copy(blob, output)
            if actual != (row.sha256, row.size):
                path.unlink()
                raise DataContractError(f"Restore SHA/size không khớp: {row.path}")
    return len(selected)


def show(archive: Path, relative: str, *, expected_sha256: str | None = None) -> str:
    """Đọc một file text lịch sử, không bung cả archive vào active repo."""
    if expected_sha256 is not None and sha256_file(archive) != expected_sha256:
        raise DataContractError("Archive SHA khác index")
    with zipfile.ZipFile(archive) as stream:
        manifest = _manifest(stream)
        entry = next((r for r in manifest.files if r.path == relative), None)
        if entry is None or entry.size > 1_000_000:
            raise DataContractError("Không có file text nhỏ này; dùng restore cho binary/file lớn")
        payload = stream.read(f"blobs/{entry.sha256}")
        if hashlib.sha256(payload).hexdigest() != entry.sha256 or len(payload) != entry.size:
            raise DataContractError("File text lịch sử không khớp SHA/size")
        return payload.decode("utf-8-sig")


def list_files(archive: Path, *, prefixes: tuple[str, ...] = (),
               expected_sha256: str | None = None) -> list[str]:
    """Tra original paths của đúng nhánh, không đọc nội dung hoặc extract."""
    if expected_sha256 is not None and sha256_file(archive) != expected_sha256:
        raise DataContractError("Archive SHA khác index")
    with zipfile.ZipFile(archive) as stream:
        return [row.path for row in _manifest(stream).files
                if not prefixes or _matches(row.path, prefixes)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["list", "verify", "restore", "show"])
    parser.add_argument("archive", type=Path)
    parser.add_argument("path", nargs="?")
    parser.add_argument("--destination", type=Path, default=Path.cwd())
    parser.add_argument("--prefix", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--sha256")
    args = parser.parse_args()
    if args.action == "list":
        print("\n".join(list_files(args.archive, prefixes=tuple(args.prefix),
                                   expected_sha256=args.sha256)))
    elif args.action == "show":
        if args.path is None:
            parser.error("show cần original path")
        print(show(args.archive, args.path, expected_sha256=args.sha256))
    elif args.action == "verify":
        manifest = verify(args.archive, expected_sha256=args.sha256)
        print(json.dumps({"name": manifest.name, "files": len(manifest.files),
                          "unique_blobs": len({r.sha256 for r in manifest.files})}))
    else:
        print(json.dumps({"restored_files": restore(
            args.archive, args.destination, prefixes=tuple(args.prefix),
            exclude=tuple(args.exclude), expected_sha256=args.sha256,
        )}))


if __name__ == "__main__":
    main()
