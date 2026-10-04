"""Apply remaining QA owner answers to a new version; never emit training labels."""
import argparse
import json
from collections import Counter
from pathlib import Path

from ai_exam_monitoring.data.review_plan import apply_owner_review
from scripts.audits.roboflow_remaining_qa import ROOT, digest, write_json


def run(base: Path, output: Path) -> dict:
    evidence = ROOT / "artifacts/reports/roboflow-20261004"
    decisions_path = evidence / "remaining-qa-owner-decisions.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    if decisions["dataset_accepted"] is not False:
        raise ValueError("This review cannot accept a dataset")
    if digest(base / "summary.json") != decisions["base_summary_sha256"]:
        raise ValueError("Wrong owner-reviewed base")
    summary = json.loads((base / "summary.json").read_text(encoding="utf-8"))
    for name, checksum in summary["output_sha256"].items():
        path = (base / name).resolve()
        if not path.is_relative_to(base.resolve()) or digest(path) != checksum:
            raise ValueError(f"Reviewed artifact changed: {name}")
    def read(name):
        return json.loads((base / name).read_text(encoding="utf-8"))

    queue, approved = apply_owner_review(
        read("queue.json"), read("approved-boxes.json"), read("review.json"), decisions["items"]
    )
    output = output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "outputs"):
        raise ValueError("Use a new outputs directory")
    output.mkdir(parents=True)
    write_json(output / "queue.json", queue)
    write_json(output / "approved-boxes.json", approved)
    write_json(output / "pending.json",
               [r for r in queue if r["disposition"] == "pending_manual_QA"])
    write_json(output / "held.json",
               [r for r in queue if r["disposition"] == "held_outside_train_by_owner"])
    for name in ("completeness.json", "source-rejections.json"):
        (output / name).write_bytes((base / name).read_bytes())
    result = {
        "base": base.resolve().as_posix(), "output": output.as_posix(),
        "base_summary_sha256": decisions["base_summary_sha256"],
        "decision_sha256": digest(decisions_path),
        "script_sha256": digest(Path(__file__)),
        "logic_sha256": digest(ROOT / "src/ai_exam_monitoring/data/review_plan.py"),
        "queue_images": len(queue),
        "dispositions": dict(Counter(r["disposition"] for r in queue)),
        "approved_images": len(approved),
        "approved_boxes": sum(len(r["boxes"]) for r in approved),
        "training_eligible_images": 0, "dataset_accepted": False,
        "outputs_sha256": {p.name: digest(p) for p in sorted(output.iterdir())},
    }
    write_json(output / "summary.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.base, args.output), indent=2))
