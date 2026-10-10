"""Audit metadata nhãn/group/pair Draft; không đọc ảnh hoặc materialize release."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, cast

TARGETS = ("phone_use", "looking_around")
STATES = {"P", "N", "U"}


def read_rows(path: Path) -> list[dict[str, Any]]:
    """Đọc JSONL/JSON metadata; không truy cập đường dẫn media trong record."""
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, list):
        return cast(list[dict[str, Any]], value)
    for key in ("records", "candidates", "pairs", "rows", "links"):
        if isinstance(value.get(key), list):
            return cast(list[dict[str, Any]], value[key])
    raise ValueError(f"Metadata không có danh sách record rõ ràng: {path}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identifier(row: dict[str, Any]) -> str:
    return str(row.get("sample_id") or row.get("candidate_id") or row.get("id") or "")


def proposed_states(row: dict[str, Any]) -> tuple[str, str]:
    value = row.get("final_proposed_states", row.get("proposed_states"))
    if isinstance(value, dict):
        states = tuple(value[target] for target in TARGETS)
    elif isinstance(value, list) and len(value) == 2:
        states = tuple(value)
    else:
        raise ValueError(f"Thiếu proposed_states cho {identifier(row)}")
    if len(states) != 2 or any(state not in STATES for state in states):
        raise ValueError(f"State không hợp lệ cho {identifier(row)}: {states}")
    return str(states[0]), str(states[1])


def bucket(row: dict[str, Any]) -> str:
    value = row.get("primary_bucket", row.get("bucket"))
    if value:
        return str(value)
    parts = identifier(row).split("-")
    return parts[1] if len(parts) == 3 and parts[0] == "V7" else "UNKNOWN"


def optional_metadata(row: dict[str, Any], name: str) -> str:
    """Thiếu camera/room/group luôn unknown; không thay bằng source hoặc visual hint."""
    value = row.get(name)
    if value is None:
        return "UNKNOWN"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def registered_group(row: dict[str, Any]) -> str:
    if row.get("leakage_group_id") is not None:
        return optional_metadata(row, "leakage_group_id")
    return optional_metadata(row, "group_id")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_image_key(row: dict[str, Any]) -> tuple[str, str] | None:
    for key in ("source_pixel_sha256", "source_image_sha256", "source_sha256"):
        if row.get(key):
            return key, str(row[key])
    return None


def annotation_tables(rows: list[dict[str, Any]], version: str) -> dict[str, Any]:
    matrix: Counter[tuple[str, ...]] = Counter()
    hint_matrix: Counter[tuple[str, ...]] = Counter()
    combinations: Counter[tuple[str, ...]] = Counter()
    looking: Counter[tuple[str, ...]] = Counter()
    source_count: Counter[str] = Counter()
    fully_known_by_source: Counter[str] = Counter()
    bucket_states: dict[str, Counter[str]] = defaultdict(Counter)
    image_count: Counter[str] = Counter()
    hint_count: Counter[str] = Counter()
    known = uu = 0
    combination_totals: Counter[str] = Counter()
    target_totals = {target: Counter({"P": 0, "N": 0, "U": 0}) for target in TARGETS}
    crowded = []
    desk_classroom: Counter[str] = Counter({"P": 0, "N": 0, "U": 0})
    for row in rows:
        sid = identifier(row)
        source = optional_metadata(row, "source_id")
        domain = optional_metadata(row, "domain")
        family = optional_metadata(row, "visual_family_hint")
        group = registered_group(row)
        phone, gaze = proposed_states(row)
        primary = bucket(row)
        camera = optional_metadata(row, "camera_id")
        room = optional_metadata(row, "room_id")
        combinations[(version, source, domain, primary, phone, gaze)] += 1
        combination_totals[phone + gaze] += 1
        known += phone != "U" and gaze != "U"
        if phone != "U" and gaze != "U":
            fully_known_by_source[source] += 1
        bucket_states[primary][phone + gaze] += 1
        uu += phone == gaze == "U"
        for target, state in zip(TARGETS, (phone, gaze), strict=True):
            target_totals[target][state] += 1
            matrix[(version, source, domain, target, state, group)] += 1
            hint_matrix[(version, source, domain, primary, target, state, group, family)] += 1
        source_count[source] += 1
        image = source_image_key(row)
        image_count["|".join(image) if image else "UNKNOWN"] += 1
        hint_count[source + "|" + family] += 1
        if primary == "C":
            looking[(version, source, camera, room, group, family, gaze)] += 1
        if primary == "A" and domain == "classroom_or_exam_context":
            desk_classroom[phone] += 1
        if primary == "D":
            crowded.append(
                {
                    "version": version,
                    "sample_id": sid,
                    "source_id": source,
                    "domain": domain,
                    "phone": phone,
                    "looking": gaze,
                    "actual_proposed_cooccurrence": phone == gaze == "P",
                    "phone_known": phone != "U",
                    "looking_known": gaze != "U",
                    "ownership_review_status": "Draft: cần owner xem đúng anchor và thiết bị",
                    "evidence": row.get(
                        "final_reason",
                        row.get(
                            "reason", row.get("label_reason", row.get("observation", "UNKNOWN"))
                        ),
                    ),
                    "person_unit_hint": optional_metadata(row, "person_unit_hint"),
                }
            )
    matrix_fields = [
        "version",
        "source_id",
        "domain",
        "target",
        "state",
        "registered_group",
        "count",
    ]
    hint_fields = [
        "version",
        "source_id",
        "domain",
        "bucket",
        "target",
        "state",
        "registered_group",
        "visual_family_hint",
        "count",
    ]
    combination_fields = ["version", "source_id", "domain", "bucket", "phone", "looking", "count"]
    looking_fields = [
        "version",
        "source_id",
        "camera_id",
        "room_id",
        "registered_group",
        "visual_family_hint",
        "looking",
        "count",
    ]

    def counter_rows(counts: Counter[tuple[str, ...]], fields: list[str]) -> list[dict[str, Any]]:
        return [
            dict(zip(fields, (*key, count), strict=True)) for key, count in sorted(counts.items())
        ]

    concentration = []
    for level, counts in (
        ("source", source_count),
        ("source_image", image_count),
        ("visual_family_hint", hint_count),
    ):
        for key, count in counts.most_common():
            concentration.append(
                {
                    "version": version,
                    "level": level,
                    "key": key,
                    "count": count,
                    "share": count / len(rows),
                }
            )
    return {
        "summary": {
            "version": version,
            "crop_count": len(rows),
            "fully_known": known,
            "all_unknown": uu,
            "combination_counts": dict(sorted(combination_totals.items())),
            "target_counts": {target: dict(counts) for target, counts in target_totals.items()},
            "desk_classroom_counts": dict(desk_classroom),
            "source_counts": dict(source_count),
            "fully_known_by_source": dict(fully_known_by_source),
            "bucket_combination_counts": {key: dict(value) for key, value in bucket_states.items()},
            "camera_unknown": sum(optional_metadata(row, "camera_id") == "UNKNOWN" for row in rows),
            "room_unknown": sum(optional_metadata(row, "room_id") == "UNKNOWN" for row in rows),
            "registered_group_unknown": sum(registered_group(row) == "UNKNOWN" for row in rows),
        },
        "matrix": (matrix_fields, counter_rows(matrix, matrix_fields)),
        "hint_matrix": (hint_fields, counter_rows(hint_matrix, hint_fields)),
        "combinations": (combination_fields, counter_rows(combinations, combination_fields)),
        "looking": (looking_fields, counter_rows(looking, looking_fields)),
        "concentration": (["version", "level", "key", "count", "share"], concentration),
        "crowded": (
            [
                "version",
                "sample_id",
                "source_id",
                "domain",
                "phone",
                "looking",
                "actual_proposed_cooccurrence",
                "phone_known",
                "looking_known",
                "ownership_review_status",
                "evidence",
                "person_unit_hint",
            ],
            crowded,
        ),
    }


def pair_endpoints(pair: dict[str, Any]) -> tuple[str, str, str]:
    positive = pair.get("positive_sample_id", pair.get("positive_id", pair.get("positive")))
    negative = pair.get("negative_sample_id", pair.get("negative_id", pair.get("negative")))
    target = pair.get("target", pair.get("target_name"))
    if target is None and pair.get("bucket") in {"A", "B", "C"}:
        target = "looking_around" if pair["bucket"] == "C" else "phone_use"
    if isinstance(positive, dict):
        positive = identifier(positive)
    if isinstance(negative, dict):
        negative = identifier(negative)
    if target not in TARGETS or not positive or not negative:
        raise ValueError(f"Pair schema thiếu endpoint/target rõ ràng: {pair}")
    return str(positive), str(negative), str(target)


def audit_pairs(
    rows: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    attributions: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_id = {identifier(row): row for row in rows}
    original = set()
    audited = []
    for pair in pairs:
        positive, negative, target = pair_endpoints(pair)
        original.add((positive, negative, target))
        if positive not in by_id or negative not in by_id:
            raise ValueError(f"Pair tham chiếu sample ngoài batch: {positive}/{negative}")
        index = TARGETS.index(target)
        pos_state = proposed_states(by_id[positive])[index]
        neg_state = proposed_states(by_id[negative])[index]
        valid = pos_state == "P" and neg_state == "N"
        audited.append(
            {
                **pair,
                "audit_positive_state": pos_state,
                "audit_negative_state": neg_state,
                "target_polarity_valid": valid,
                "audit_status": "Draft polarity hợp lệ; cần review anchor"
                if valid
                else "Không còn P/N sau QA; không dùng pair hiện tại",
            }
        )
    image_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = source_image_key(row)
        if key:
            image_groups[key].append(row)
    for attribution in attributions or []:
        sid = identifier(attribution)
        photo = attribution.get("flickr_photo_id", attribution.get("photo_id"))
        if sid in by_id and photo:
            image_groups[("flickr_photo_id", str(photo))].append(by_id[sid])
    added = []
    proposed_ids = set()
    for image, group_rows in sorted(image_groups.items()):
        for first, second in itertools.combinations(group_rows, 2):
            first_unit = optional_metadata(first, "person_unit_hint")
            second_unit = optional_metadata(second, "person_unit_hint")
            if "UNKNOWN" in (first_unit, second_unit) or first_unit == second_unit:
                continue
            for index, target in enumerate(TARGETS):
                first_state, second_state = (
                    proposed_states(first)[index],
                    proposed_states(second)[index],
                )
                if {first_state, second_state} != {"P", "N"}:
                    continue
                positive_row, negative_row = (
                    (first, second) if first_state == "P" else (second, first)
                )
                ids = (identifier(positive_row), identifier(negative_row), target)
                if ids in original or ids in proposed_ids:
                    continue
                proposed_ids.add(ids)
                added.append(
                    {
                        "positive_sample_id": ids[0],
                        "negative_sample_id": ids[1],
                        "target": target,
                        "strength": "same_image",
                        "source_evidence": {image[0]: image[1]},
                        "person_unit_hints": [
                            optional_metadata(positive_row, "person_unit_hint"),
                            optional_metadata(negative_row, "person_unit_hint"),
                        ],
                        "status": "Draft cần owner xác nhận anchor",
                        "independent_group_gain": 0,
                    }
                )
    return audited, added


def conservative_graph(
    rows: list[dict[str, Any]],
    attributions: list[dict[str, Any]],
    historical_rows: list[dict[str, Any]],
    pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Whole-component proposal từ metadata; hint union không chứng minh independence."""
    parent: dict[str, str] = {}
    edges: list[dict[str, Any]] = []
    split_hints: dict[str, set[str]] = defaultdict(set)
    unresolved_near_flags = []

    def find(node: str) -> str:
        parent.setdefault(node, node)
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    def join(left: str, right: str, relation: str, proof: str) -> None:
        if left == right:
            return
        left_root, right_root = find(left), find(right)
        parent[right_root] = left_root
        edges.append({"left": left, "right": right, "relation": relation, "evidence_status": proof})

    seen: dict[tuple[str, str], str] = {}
    row_ids = {identifier(row) for row in rows}
    for row in rows:
        sid = identifier(row)
        find(sid)
        source_hashes = {
            "source_pixel_sha256": row.get("source_pixel_sha256"),
            "source_image_sha256": row.get("source_image_sha256", row.get("source_sha256")),
        }
        for field, value in source_hashes.items():
            if value:
                key = (field, str(value))
                if key in seen:
                    join(sid, seen[key], field, "metadata_exact_match")
                else:
                    seen[key] = sid
        family = optional_metadata(row, "visual_family_hint")
        if family != "UNKNOWN":
            key = ("source_visual_hint", optional_metadata(row, "source_id") + "|" + family)
            if key in seen:
                join(sid, seen[key], "visual_family_hint", "conservative_unproven_scene")
            else:
                seen[key] = sid
        accepted_group = registered_group(row)
        if accepted_group != "UNKNOWN":
            key = ("registered_group", accepted_group)
            if key in seen:
                join(sid, seen[key], "registered_group", "registered_metadata")
            else:
                seen[key] = sid
        for field in ("nearest_parent", "nearest_evaluation", "nearest_eval"):
            nearest = row.get(field)
            if not isinstance(nearest, dict):
                continue
            unresolved_near_flags.append(
                {
                    "sample_id": sid,
                    "relation": field,
                    "metadata": nearest,
                    "graph_union": False,
                    "status": "Nearest similarity không chứng minh lineage; review nếu triage flag",
                }
            )
    historical_seen: dict[tuple[str, str], str] = {}
    historical_groups: dict[str, str] = {}
    parent_scene_hints: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        family = optional_metadata(row, "visual_family_hint")
        if family.startswith("PARENT-TRAIN-"):
            parent_scene_hints[family.removeprefix("PARENT-TRAIN-")].append(identifier(row))
    for row in historical_rows:
        sid = identifier(row)
        node = "historical:" + sid
        # Chỉ nhập parent node nếu có exact byte/pixel link tới candidate.
        linked = False
        source = row.get("source", {})
        if not isinstance(source, dict):
            source = {}
        source_hashes = {
            "source_pixel_sha256": row.get("source_pixel_sha256", source.get("pixel_sha256")),
            "source_image_sha256": row.get("source_image_sha256", source.get("image_sha256")),
        }
        group_value = row.get("group")
        if isinstance(group_value, dict):
            group = group_value.get("leakage_group_id")
        else:
            group = row.get("leakage_group_id", row.get("group_id"))
        # Hint đã ghi rõ parent group chỉ ràng buộc split bảo thủ, không thành approval.
        for candidate in parent_scene_hints.get(str(group), []):
            join(candidate, node, "parent_scene_hint", "conservative_unproven_scene")
            linked = True
        for field, value in source_hashes.items():
            if not value:
                continue
            key = (field, str(value))
            if key in seen:
                join(seen[key], node, "parent_" + field, "metadata_exact_match")
                linked = True
            if key in historical_seen and linked:
                join(node, historical_seen[key], "historical_same_source", "metadata_exact_match")
            historical_seen[key] = node
        if not linked:
            continue
        split = row.get("split")
        if split:
            split_hints[node].add(str(split))
        if group:
            group = str(group)
            if group in historical_groups:
                join(
                    node,
                    historical_groups[group],
                    "historical_registered_group",
                    "registered_metadata",
                )
            else:
                historical_groups[group] = node
    flickr: dict[str, str] = {}
    for attribution in attributions:
        sid = identifier(attribution)
        if sid not in row_ids:
            continue
        photo = attribution.get("flickr_photo_id", attribution.get("photo_id"))
        if not photo:
            continue
        photo = str(photo)
        if photo in flickr:
            join(sid, flickr[photo], "same_flickr_photo_id", "public_attribution_metadata")
        else:
            flickr[photo] = sid
    for pair in pairs or []:
        if pair.get("match_strength") != "same_scene":
            continue
        positive, negative, _ = pair_endpoints(pair)
        if positive in row_ids and negative in row_ids:
            join(positive, negative, "r7_same_scene_pair", "draft_scene_evidence_owner_pending")
    components: dict[str, list[str]] = defaultdict(list)
    for node in sorted(parent):
        components[find(node)].append(node)
    proposed: list[dict[str, Any]] = []
    for nodes in sorted(components.values(), key=lambda values: values[0]):
        members = [node for node in nodes if not node.startswith("historical:")]
        historical = [node for node in nodes if node.startswith("historical:")]
        splits = sorted(set().union(*(split_hints[node] for node in nodes)))
        evaluation = any(
            split in {"val", "valid", "validation", "test", "evaluation_unknown"}
            for split in splits
        )
        if evaluation:
            action = "quarantine_review_only; không tuyển vào train"
        elif historical:
            action = (
                "review parent scene; nếu xác nhận parent train thì giữ whole-component cùng train"
            )
        else:
            action = (
                "review_only; owner chốt group và train/new-development-val cho whole-component"
            )
        proposed.append(
            {
                "component_id": "GC-" + hashlib.sha256("|".join(nodes).encode()).hexdigest()[:12],
                "candidate_ids": members,
                "historical_nodes": historical,
                "historical_split_hints": splits,
                "candidate_count": len(members),
                "proposal": action,
                "official_split": None,
                "independence_status": "UNPROVEN",
                "owner_approval": False,
            }
        )
    return {
        "edges": edges,
        "components": proposed,
        "unresolved_near_flags": unresolved_near_flags,
        "summary": {
            "candidate_nodes": len(row_ids),
            "component_count_conservative_hints": len(proposed),
            "independent_groups_proven": 0,
            "registered_group_approval": "owner pending",
            "evaluation_linked_components": sum(
                "quarantine" in component["proposal"] for component in proposed
            ),
            "parent_linked_components_pending_review": sum(
                bool(component["historical_nodes"]) for component in proposed
            ),
            "parent_scene_hint_edges": sum(
                edge["relation"] == "parent_scene_hint" for edge in edges
            ),
            "component_count_is_not_independent_group_count": True,
        },
    }


def run(config: dict[str, Any], root: Path) -> None:
    root = root.resolve()
    output = (root / config["output_dir"]).resolve()
    report_root = (root / "artifacts/reports").resolve()
    if not output.is_relative_to(report_root) or output == report_root:
        raise ValueError("Audit output phải là thư mục con artifacts/reports trong workspace")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Không ghi đè audit đã tồn tại; chọn output version mới")
    input_paths = {
        key: (root / config[key]).resolve()
        for key in ("r7_proposals", "final_proposals", "pairs", "attributions", "parent_manifest")
    }
    if any(
        not path.is_relative_to(root) or path.suffix not in {".json", ".jsonl"}
        for path in input_paths.values()
    ):
        raise ValueError("Chỉ đọc JSON/JSONL metadata trong repository")
    pins = {
        key: {"path": path.relative_to(root).as_posix(), "sha256": sha256(path)}
        for key, path in input_paths.items()
    }
    for key, expected in config.get("expected_sha256", {}).items():
        if pins[key]["sha256"] != expected:
            raise ValueError(f"Pin SHA không khớp {key}")
    versions = {
        "R7": read_rows(input_paths["r7_proposals"]),
        "Final-proposal": read_rows(input_paths["final_proposals"]),
    }
    for version, rows in versions.items():
        ids = [identifier(row) for row in rows]
        if not all(ids) or len(ids) != len(set(ids)):
            raise ValueError(f"Sample ID rỗng hoặc duplicate trong {version}")
    if {identifier(row) for row in versions["R7"]} != {
        identifier(row) for row in versions["Final-proposal"]
    }:
        raise ValueError("Final khác membership R7; audit này cần cùng batch")
    baseline_by_id = {identifier(row): row for row in versions["R7"]}
    versions["Final-proposal"] = [
        {**baseline_by_id[identifier(row)], **row} for row in versions["Final-proposal"]
    ]
    tables = {version: annotation_tables(rows, version) for version, rows in versions.items()}
    pairs = read_rows(input_paths["pairs"])
    attributions = read_rows(input_paths["attributions"])
    pair_audits = {}
    additions = {}
    for version, rows in versions.items():
        audited, added = audit_pairs(rows, pairs, attributions)
        pair_audits[version] = audited
        additions[version] = added
    graph = conservative_graph(
        versions["Final-proposal"], attributions, read_rows(input_paths["parent_manifest"]), pairs
    )
    # Sau pins/schema/graph preflight mới ghi vào output version mới.
    output.mkdir(parents=True, exist_ok=True)
    for table_name in (
        "matrix",
        "hint_matrix",
        "combinations",
        "looking",
        "concentration",
        "crowded",
    ):
        fields = tables["R7"][table_name][0]
        table_rows = [row for table in tables.values() for row in table[table_name][1]]
        write_csv(output / f"annotation-{table_name.replace('_', '-')}.csv", table_rows, fields)
    write_json(output / "group-pair-audit.json", pair_audits)
    write_json(output / "group-additional-real-pair-proposals.json", additions)
    write_json(output / "group-edges.json", graph["edges"])
    write_json(output / "group-whole-component-proposal.json", graph["components"])
    write_json(output / "group-unresolved-near-flags.json", graph["unresolved_near_flags"])
    summary = {
        "status": "Draft; không approval/release/split/train",
        "input_pins": pins,
        "annotation": {version: table["summary"] for version, table in tables.items()},
        "pairs": {
            version: {
                "existing_count": len(audited),
                "strength_counts": dict(
                    Counter(str(pair.get("match_strength", "UNKNOWN")) for pair in audited)
                ),
                "valid_target_polarity": sum(pair["target_polarity_valid"] for pair in audited),
                "invalid_target_polarity": sum(
                    not pair["target_polarity_valid"] for pair in audited
                ),
                "additional_same_image_proposals": len(additions[version]),
            }
            for version, audited in pair_audits.items()
        },
        "graph": graph["summary"],
        "media_read": False,
        "model_executed": False,
    }
    write_json(output / "annotation-summary.json", summary)
    report = [
        "# Audit nhãn và group/pairs v7",
        "",
        "Trạng thái: Draft. R7 bất biến; final proposal chưa là canonical labels.",
        "",
        "Group registered, camera và room missing giữ UNKNOWN; không suy từ source/visual hint. "
        "Whole-component graph dùng các hint bảo thủ để tránh tách họ hàng, "
        "không chứng minh independence.",
        "",
        "| Version | Crop | Fully-known | U/U | Phone P/N/U | Looking P/N/U |",
        "|---|---:|---:|---:|---|---|",
    ]
    for version, table in tables.items():
        item = table["summary"]
        phone = item["target_counts"]["phone_use"]
        gaze = item["target_counts"]["looking_around"]
        report.append(
            f"| {version} | {item['crop_count']} | {item['fully_known']} | {item['all_unknown']} | "
            f"{phone['P']}/{phone['N']}/{phone['U']} | {gaze['P']}/{gaze['N']}/{gaze['U']} |"
        )
    report.extend(
        [
            "",
            "Các file CSV gồm source × domain × target × P/N/U × registered group "
            "và bảng visual family hint riêng; bảng combinations không gộp U thành N. "
            "Looking có camera/room/group thực tế hoặc UNKNOWN. "
            "Crowded đếm P/P từ proposed states; phenotype crowded "
            "không chứng minh co-occurrence hoặc ownership.",
            "",
            "Pair mới chỉ đề xuất khi cùng source hash/pixels và person_unit_hint khác nhau, "
            "có target P/N. Cần owner xem anchor, không tạo group gain. "
            "Không tuyên bố tìm thêm session pair nếu session/camera chưa được ghi nhận.",
            "",
            "Không có official split. Component có exact evaluation link cách ly bảo thủ; "
            "component parent phải review linkage và giữ cùng split đã chốt; "
            "component chưa có parent chờ owner chốt group và train hoặc new-development-val. "
            "Giữ historical validation/test nguyên trạng. "
            "Nearest similarity là cờ chưa chứng minh.",
            "",
            "CLI: `python -m ai_exam_monitoring.data.v7_annotation_audit "
            "--config <config-yaml> --root <repo-root>`.",
        ]
    )
    (output / "annotation-audit.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    import yaml

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    run(config, args.root)


if __name__ == "__main__":
    main()
