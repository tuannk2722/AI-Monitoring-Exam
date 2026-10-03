"""Reproduce or complete the owner-supplied Roboflow v1 audit; never build/train.

Run from repository root. Output/evidence directories must not already exist.
--existing-reports reuses the prior full decode reports, reconciles every source
label against the ZIP, and records hashes of reused reports. Omit to rerun them.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from hashlib import sha256
from importlib.metadata import version
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.audit import audit_dataset
from ai_exam_monitoring.data.overlay import export_overlays
from ai_exam_monitoring.data.yolo import YoloAnnotation

EXPECTED = "70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed"
NAMES = {0: "Looking around", 1: "No cheating", 2: "Phone use"}
SCB = {
    "SCB5-Discuss-2024-9-17.zip": (
        "63aa029d04f8e9d5027cc2491aeca10785678750bdae4351835bfceaab95187f"
    ),
    "SCB5-Handrise-Read-write-2024-9-17.zip": (
        "46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d"
    ),
    "SCB_BowTurnHead_20250509.zip": (
        "a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828"
    ),
}


def digest(path):
    with Path(path).open("rb") as stream:
        return sha256(stream.read()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_members(archive):
    seen = set()
    for info in archive.infolist():
        name = PurePosixPath(info.filename)
        if (
            name.is_absolute()
            or ".." in name.parts
            or "\\" in info.filename
            or ":" in info.filename
        ):
            raise ValueError(f"Unsafe archive path: {info.filename}")
        key = info.filename.casefold()
        if key in seen:
            raise ValueError(f"Duplicate archive path: {info.filename}")
        seen.add(key)


def contact_sheet(rows, target):
    font = ImageFont.load_default(size=15)
    tiles = []
    for row in rows:
        with Image.open(row["overlay"]) as image:
            image = image.convert("RGB")
            image.thumbnail((590, 530))
        tile = Image.new("RGB", (610, 580), "white")
        tile.paste(image, (10, 40))
        ImageDraw.Draw(tile).text(
            (10, 8), f"{row['id']} | {row['reason']}", font=font, fill="black"
        )
        tiles.append(tile)
    sheet = Image.new("RGB", (1220, 580 * math.ceil(len(tiles) / 2)), "#cccccc")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 2) * 610, (i // 2) * 580))
    sheet.save(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--scb-archives", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--existing-reports", type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.evidence.exists():
        raise ValueError("Use new output/evidence directories; existing files are preserved")
    if digest(args.archive) != EXPECTED:
        raise ValueError("Archive is not the owner-supplied v1 ZIP")
    # All inputs are read-only; do not allow outputs inside raw/source paths.
    forbidden = [Path("data/raw").resolve()]
    if args.existing_reports:
        forbidden.append(args.existing_reports.resolve())
    for target in (args.output.resolve(), args.evidence.resolve()):
        if any(target == root or root in target.parents for root in forbidden):
            raise ValueError("Output must be outside raw/existing audit inputs")
    args.output.mkdir(parents=True)
    args.evidence.mkdir(parents=True)
    out, evidence = args.output, args.evidence
    provenance = {
        "schema_version": 1,
        "audit_date": "2026-10-04",
        "archive": {
            "path": str(args.archive),
            "bytes": args.archive.stat().st_size,
            "sha256": EXPECTED,
        },
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "python": platform.python_version(),
        "packages": {key: version(key) for key in ["Pillow", "numpy", "PyYAML"]},
        "script_sha256": digest(__file__),
        "command": sys.argv,
        "code_sha256": {
            str(p): digest(p) for p in Path("src/ai_exam_monitoring/data").glob("*.py")
        },
        "mode": "reuse_prior_full_decode_reports_and_reconcile_zip"
        if args.existing_reports
        else "full_audit",
        "reused_reports": {},
        "scb_archives": [],
        "automatic": [
            "all_raw_label_rows",
            "strict_class_counts_reconciled",
            "bbox_statistics",
            "exact_sha256_all_zip_images",
            "cross_scb_exact_sha256",
        ],
        "not_checked": [
            "near_duplicates",
            "verified_video_session_grouping",
            "exhaustive_semantics",
            "consent_chain",
            "model_quality",
        ],
    }
    reports, raw, good_rows, errors = {}, {}, {}, []
    strict_counts, raw_images, strict_images = {}, {}, {}
    hashes, manifest = defaultdict(list), []
    with ZipFile(args.archive) as archive:
        safe_members(archive)
        if archive.testzip() is not None:
            raise ValueError("Archive CRC failed")
        provenance["archive"]["crc_ok"] = True
        provenance["archive"]["zip_entries"] = len(archive.infolist())
        metadata = {
            name: archive.read(name).decode("utf-8")
            for name in ["data.yaml", "README.dataset.txt", "README.roboflow.txt"]
        }
        config = yaml.safe_load(metadata["data.yaml"])
        assert config["roboflow"]["version"] == 1 and config["names"] == list(NAMES.values())
        save(
            evidence / "source-metadata.json",
            {
                "scope": "verbatim owner ZIP metadata, not external consent verification",
                "files": metadata,
            },
        )
        save(evidence / "source-names.json", NAMES)
        if not args.existing_reports:
            source = out / "extracted"
            archive.extractall(source)
        for split in ["train", "valid", "test"]:
            if args.existing_reports:
                path = args.existing_reports / f"{split}-audit.json"
                reports[split] = json.loads(path.read_text(encoding="utf-8"))
                provenance["reused_reports"][split] = {"path": str(path), "sha256": digest(path)}
            else:
                reports[split] = audit_dataset(
                    source,
                    images_dir=f"{split}/images",
                    labels_dir=f"{split}/labels",
                    source_names=NAMES,
                )
            r = reports[split]
            save(out / f"{split}-audit.json", r)
            assert {int(k): v for k, v in r["source_names"].items()} == NAMES
            raw[split], good_rows[split], strict_counts[split] = Counter(), Counter(), Counter()
            raw_images[split], strict_images[split] = Counter(), Counter()
            label_files = sorted(
                n
                for n in archive.namelist()
                if n.startswith(f"{split}/labels/") and n.endswith(".txt")
            )
            image_files = sorted(
                n
                for n in archive.namelist()
                if n.startswith(f"{split}/images/") and n.endswith(".jpg")
            )
            assert (
                len(image_files) == r["image_count"] and len(label_files) == r["label_file_count"]
            )
            bad_files = set()
            for name in label_files:
                file_counts, valid, bad = Counter(), [], False
                for number, line in enumerate(archive.read(name).decode("utf-8").splitlines(), 1):
                    if not line.strip():
                        continue
                    fields = line.split()
                    cid = int(fields[0])
                    raw[split][cid] += 1
                    file_counts[cid] += 1
                    try:
                        box = YoloAnnotation.parse(line)
                        if box.class_id not in NAMES:
                            raise DataContractError("Unknown source ID")
                        valid.append(box)
                        good_rows[split][cid] += 1
                    except DataContractError as exc:
                        bad = True
                        _, x, y, w, h = map(float, fields)
                        overflow = max(0, w / 2 - x, h / 2 - y, x + w / 2 - 1, y + h / 2 - 1)
                        xd, yd, wd, hd = map(Decimal, fields[1:])
                        decimal_overflow = max(
                            Decimal(0), wd / 2 - xd, hd / 2 - yd, xd + wd / 2 - 1, yd + hd / 2 - 1
                        )
                        image_name = (
                            name.replace("/labels/", "/images/").removesuffix(".txt") + ".jpg"
                        )
                        with Image.open(BytesIO(archive.read(image_name))) as image:
                            iw, ih = image.size
                        overflow_pixels = max(
                            0,
                            (w / 2 - x) * iw,
                            (h / 2 - y) * ih,
                            (x + w / 2 - 1) * iw,
                            (y + h / 2 - 1) * ih,
                        )
                        errors.append(
                            {
                                "split": split,
                                "label": name,
                                "line": number,
                                "class_id": cid,
                                "raw": line,
                                "error": str(exc),
                                "overflow_normalized": overflow,
                                "overflow_pixels": overflow_pixels,
                                "overflow_decimal_from_text": str(decimal_overflow),
                            }
                        )
                raw_images[split].update(file_counts.keys())
                if bad:
                    bad_files.add(name)
                else:
                    strict_counts[split].update(b.class_id for b in valid)
                    strict_images[split].update(set(b.class_id for b in valid))
            assert bad_files == {x["file"] for x in r["invalid_labels"]}
            assert dict(strict_counts[split]) == {
                int(k): v for k, v in r["annotation_count_by_class_id"].items()
            }
            for name in image_files:
                data = archive.read(name)
                hashed = sha256(data).hexdigest()
                hashes[hashed].append(name)
                manifest.append({"image": name, "sha256": hashed})
            print(
                f"{split}: raw={dict(raw[split])}, strict={dict(strict_counts[split])}, "
                f"bad_files={len(bad_files)}",
                flush=True,
            )
        train = reports["train"]
        class_boxes = {}
        quantiles = {}
        for cid in NAMES:
            boxes = sorted(
                [
                    (a["width"] * a["height"], s, a)
                    for s in train["samples"]
                    for a in s["annotations"]
                    if a["class_id"] == cid
                ],
                key=lambda x: (x[0], x[1]["image"]),
            )
            class_boxes[cid] = boxes
            values = np.array(
                [[a["width"] * s["width"], a["height"] * s["height"], area] for area, s, a in boxes]
            )
            quantiles[cid] = {
                "scope": "fully valid train label files",
                "count": len(boxes),
                "quantiles": [0, 0.1, 0.5, 0.9, 1],
                **{
                    key: np.quantile(values[:, i], [0, 0.1, 0.5, 0.9, 1]).tolist()
                    for i, key in enumerate(["width_pixels", "height_pixels", "area_normalized"])
                },
            }
        selection = []
        selected_paths = set()

        def select(sample, cid, reason):
            if sample["image"] in selected_paths:
                return
            selected_paths.add(sample["image"])
            sid = f"R{len(selection) + 1:02d}"
            inp = out / "review-input"
            (inp / "images").mkdir(parents=True, exist_ok=True)
            (inp / "labels").mkdir(parents=True, exist_ok=True)
            (inp / "images" / f"{sid}.jpg").write_bytes(archive.read(sample["image"]))
            (inp / "labels" / f"{sid}.txt").write_bytes(archive.read(sample["label"]))
            selection.append(
                {
                    "id": sid,
                    "class_focus": cid,
                    "reason": reason,
                    "source_image": sample["image"],
                    "source_label": sample["label"],
                    "source_image_sha256": sha256(archive.read(sample["image"])).hexdigest(),
                }
            )

        for cid, boxes in class_boxes.items():
            for reason, index in [
                ("smallest_train_box", 0),
                ("median_train_box", len(boxes) // 2),
                ("largest_train_box", len(boxes) - 1),
            ]:
                select(boxes[index][1], cid, reason)
        phone = sorted(
            [s for s in train["samples"] if any(a["class_id"] == 2 for a in s["annotations"])],
            key=lambda s: s["image"],
        )
        for index in np.linspace(0, len(phone) - 1, 7, dtype=int):
            select(phone[index], 2, "phone_filename_spread_not_video_groups")
        export_overlays(
            out / "review-input",
            images_dir="images",
            labels_dir="labels",
            source_names=NAMES,
            output_dir=out / "review",
            limit=len(selection),
        )
        for i, row in enumerate(selection, 1):
            row["overlay"] = (out / "review" / f"{i:04d}.png").as_posix()
        save(evidence / "review-selection.json", selection)
        for cid in NAMES:
            rows = [row for row in selection if row["class_focus"] == cid]
            contact_sheet(rows, out / "review" / f"class-{cid}-contact.png")
        train_errors = [x for x in errors if x["split"] == "train"]
        warning_rows = []
        for reason, item in [
            ("minimum_train_overflow", min(train_errors, key=lambda x: x["overflow_normalized"])),
            ("maximum_train_overflow", max(train_errors, key=lambda x: x["overflow_normalized"])),
        ]:
            img = item["label"].replace("/labels/", "/images/").removesuffix(".txt") + ".jpg"
            with Image.open(BytesIO(archive.read(img))) as original:
                canvas = original.convert("RGB")
            draw = ImageDraw.Draw(canvas)
            for line_number, line in enumerate(
                archive.read(item["label"]).decode("utf-8").splitlines(), 1
            ):
                if not line.strip():
                    continue
                cid, x, y, w, h = map(float, line.split())
                color = "red" if line_number == item["line"] else "yellow"
                draw.rectangle(
                    (
                        (x - w / 2) * canvas.width,
                        (y - h / 2) * canvas.height,
                        (x + w / 2) * canvas.width,
                        (y + h / 2) * canvas.height,
                    ),
                    outline=color,
                    width=2,
                )
                draw.text(
                    ((x - w / 2) * canvas.width, (y - h / 2) * canvas.height),
                    f"L{line_number} ID{int(cid)}",
                    fill=color,
                    stroke_width=1,
                    stroke_fill="black",
                )
            tile = Image.new("RGB", (max(canvas.width, 800), canvas.height + 70), "white")
            tile.paste(canvas, (0, 0))
            font = ImageFont.load_default(size=16)
            ImageDraw.Draw(tile).text(
                (8, canvas.height + 5),
                f"RAW WARNING line {item['line']}: {item['error']}\n"
                f"overflow={item['overflow_normalized']:.16g}; NOT REPAIRED",
                fill="red",
                font=font,
            )
            target = out / "review" / f"warning-{len(warning_rows) + 1}.png"
            tile.save(target)
            warning_rows.append(
                {
                    **item,
                    "id": f"W{len(warning_rows) + 1:02d}",
                    "reason": reason,
                    "source_image": img,
                    "overlay": target.as_posix(),
                }
            )
        save(evidence / "warning-selection.json", warning_rows)
        save(out / "invalid-rows.json", errors)
        save(out / "image-hashes.json", manifest)
        diagnostics = {
            "invalid_rows": len(errors),
            "invalid_files": len({x["label"] for x in errors}),
            "reasons": dict(Counter(x["error"] for x in errors)),
            "overflow_pixels_min": min(x["overflow_pixels"] for x in errors),
            "overflow_pixels_max": max(x["overflow_pixels"] for x in errors),
            "overflow_min": min(x["overflow_normalized"] for x in errors),
            "overflow_max": max(x["overflow_normalized"] for x in errors),
            "overflow_at_most_1e-12": sum(x["overflow_normalized"] <= 1e-12 for x in errors),
            "threshold_note": "Diagnostic count only, validator unchanged",
            "raw_counts": raw,
            "valid_rows_even_in_bad_files": good_rows,
            "strict_counts": strict_counts,
            "raw_images_containing_class": raw_images,
            "strict_images_containing_class": strict_images,
            "per_class_train_bbox_quantiles": quantiles,
        }
        save(evidence / "diagnostics.json", diagnostics)
        for split, r in reports.items():
            small = {
                k: v for k, v in r.items() if k not in ["samples", "dataset_root", "invalid_labels"]
            }
            small.update(
                {
                    "invalid_label_files": len(r["invalid_labels"]),
                    "invalid_rows": sum(x["split"] == split for x in errors),
                    "raw_counts": raw[split],
                    "strict_images_containing_class": strict_images[split],
                    "raw_images_containing_class": raw_images[split],
                    "full_report": (out / f"{split}-audit.json").as_posix(),
                }
            )
            save(evidence / f"{split}-summary.json", small)
    print("Supplemental diagnostics and overlays complete; checking SCB ZIP bytes", flush=True)
    scb_hashes = set()
    for filename, expected in SCB.items():
        path = args.scb_archives / filename
        actual = digest(path)
        if actual != expected:
            raise ValueError(f"SCB archive hash mismatch: {filename}")
        count = 0
        with ZipFile(path) as archive:
            for name in archive.namelist():
                if name.lower().endswith((".jpg", ".jpeg", ".png")):
                    scb_hashes.add(sha256(archive.read(name)).hexdigest())
                    count += 1
        provenance["scb_archives"].append({"name": filename, "sha256": actual, "images": count})
        print(filename, count, flush=True)
    groups = [{"sha256": h, "files": paths} for h, paths in hashes.items() if len(paths) > 1]
    overlap = sorted(set(hashes) & scb_hashes)
    save(out / "exact-duplicate-groups.json", groups)
    save(
        evidence / "duplicates-summary.json",
        {
            "scope": "all ZIP images including files with invalid labels",
            "images": len(manifest),
            "unique_sha256": len(hashes),
            "exact_groups": len(groups),
            "extra_copies": sum(len(g["files"]) - 1 for g in groups),
            "cross_split_groups": sum(
                len({p.split("/")[0] for p in g["files"]}) > 1 for g in groups
            ),
            "scb_unique_sha256": len(scb_hashes),
            "cross_scb_hash_groups": len(overlap),
            "cross_scb_matching_hashes": overlap,
            "near_duplicates_checked": False,
        },
    )
    provenance["artifacts"] = {p.name: digest(p) for p in out.glob("*.json")}
    save(evidence / "provenance.json", provenance)
    print("Audit completion succeeded; has_errors remains true for source geometry.", flush=True)


if __name__ == "__main__":
    main()
