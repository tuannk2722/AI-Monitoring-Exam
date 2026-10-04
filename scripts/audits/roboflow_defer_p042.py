"""Apply the owner's P042 deferral, preserving approved annotations."""
import json
from collections import Counter

from scripts.audits.roboflow_batch2_review import apply_group_choices
from scripts.audits.roboflow_remaining_qa import ROOT, digest, write_json


def main():
    base = ROOT / "outputs/roboflow-remaining-reviewed-20261004-v1"
    output = ROOT / "outputs/roboflow-remaining-reviewed-20261004-v2"
    decision = ROOT / "artifacts/reports/roboflow-20261004/p042-owner-decision.json"
    review = json.loads(decision.read_text(encoding="utf-8"))
    if digest(base / "summary.json") != review["base_summary_sha256"]:
        raise ValueError("Base summary changed")
    summary = json.loads((base / "summary.json").read_text(encoding="utf-8"))
    for name, checksum in summary["outputs_sha256"].items():
        if (base / name).name != name or digest(base / name) != checksum:
            raise ValueError("Base artifact changed")
    queue = apply_group_choices(json.loads((base / "queue.json").read_text(encoding="utf-8")),
                                review["groups"])
    for row in queue:
        if row["id"] == "P042":
            row.update(owner_action="defer_from_initial_subset",
                       owner_answer=review["groups"][0]["answer_verbatim"],
                       visual_qa="deferred_initial_subset")
    if output.exists():
        raise ValueError("Output already exists; do not overwrite evidence")
    output.mkdir()
    for name in ("approved-boxes.json", "held.json", "completeness.json",
                 "source-rejections.json"):
        (output / name).write_bytes((base / name).read_bytes())
    write_json(output / "queue.json", queue)
    write_json(output / "pending.json",
               [r for r in queue if r["disposition"] == "pending_manual_QA"])
    result = {**summary, "base": base.as_posix(), "output": output.as_posix(),
              "base_summary_sha256": review["base_summary_sha256"],
              "decision_sha256": digest(decision),
              "script_sha256": digest(ROOT / "scripts/audits/roboflow_defer_p042.py"),
              "logic_sha256": digest(ROOT / "scripts/audits/roboflow_batch2_review.py"),
              "dispositions": dict(Counter(r["disposition"] for r in queue)),
              "outputs_sha256": {p.name: digest(p) for p in sorted(output.iterdir())}}
    write_json(output / "summary.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
