"""Create an immutable domain-coverage revision without relabelling coarse spam.

The baseline test is already observed during development and remains a diagnostic.
New message groups are assigned to train/validation/test before augmentation.
"""
from __future__ import annotations

import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

from .data import (TextIdentity, UnionFind, load_jsonl, make_row, sha256_file,
                   simhash, summarize, write_json, write_jsonl)
from .tokenizer import MessageTokenizer

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def token_keys(rows, tokenizer):
    result = []
    for start in range(0, len(rows), 2048):
        ids = tokenizer.encode_batch([row["text"] for row in rows[start:start + 2048]])["input_ids"]
        result.extend(hashlib.sha256(row.tobytes()).hexdigest() for row in ids)
    return result


class TemplateIndex:
    def __init__(self):
        self.entries = []
        self.bands = collections.defaultdict(set)

    def add(self, template, index):
        fingerprint = simhash(template)
        candidates = set()
        for band in range(4):
            candidates.update(self.bands[(band, fingerprint >> (16 * band) & 65535)])
        matches = []
        grams = None
        for candidate in candidates:
            other, other_fingerprint, other_index = self.entries[candidate]
            if (fingerprint ^ other_fingerprint).bit_count() > 6:
                continue
            if abs(len(template) - len(other)) > max(10, len(template) * .2):
                continue
            if grams is None:
                grams = {template[i:i + 3] for i in range(max(1, len(template) - 2))}
            other_grams = {other[i:i + 3] for i in range(max(1, len(other) - 2))}
            similarity = len(grams & other_grams) / max(1, len(grams | other_grams))
            if similarity >= .75:
                matches.append(other_index)
        position = len(self.entries)
        self.entries.append((template, fingerprint, index))
        for band in range(4):
            self.bands[(band, fingerprint >> (16 * band) & 65535)].add(position)
        return matches


def read_candidates(raw_dir):
    candidates = []
    with zipfile.ZipFile(raw_dir / "mudou_mirror.zip") as archive:
        member = next(name for name in archive.namelist() if name.endswith(".train"))
        for index, line in enumerate(archive.read(member).decode("utf-8").splitlines()):
            fields = line.split("\t")
            if len(fields) < 2 or fields[0] != "1":
                continue
            text = fields[1].strip()
            if len(text) < 8 or len(re.findall(r"[\u3400-\u9fff]", text)) < 3:
                continue
            candidates.append(make_row(text, -1, "mudou_sms", f"mudou_spam.train:{index}",
                source_label="1", origin="labelled_real_sms_coarse_unwanted", risk_label=1,
                supervision="binary_unwanted", subtype_ground_truth="unknown_spam_or_scam"))
    with zipfile.ZipFile(raw_dir / "fgrc_sms.zip") as archive:
        member = "message/finetuning_initial.json"
        values = json.loads(archive.read(member))
        for index, item in enumerate(values):
            text, category = item["文本"].strip(), item["风险类别"]
            if len(text) < 8 or len(re.findall(r"[\u3400-\u9fff]", text)) < 3:
                continue
            candidates.append(make_row(text, 0 if category == "无风险" else 2,
                "fgrc_scd", f"finetuning_initial:{index}", source_label=category,
                origin="generated_case_derived_sms_not_captured_real_sms",
                risk_label=0 if category == "无风险" else 1, supervision="three_class",
                case_id=str(item["案件编号"])))
    return candidates


def group_and_filter(candidates, baseline, tokenizer, identity):
    """Use one joint index so transitive candidates near heldouts are excluded."""
    protected = []
    seen_ids = set()
    for name in ("train", "validation", "test", "external_mudou_binary", "external_unreviewed"):
        for row in baseline[name]:
            if row.get("script_origin") == "traditional_converted" or row["record_id"] in seen_ids:
                continue
            seen_ids.add(row["record_id"])
            protected.append({**row, "protected_split": name})
    all_rows = protected + candidates
    nprotected = len(protected)
    union = UnionFind(len(all_rows))
    by_canonical, by_template, by_token, by_case = {}, {}, {}, {}
    near = TemplateIndex()
    print(json.dumps({"phase": "joint_identity_filter", "protected": nprotected,
                      "candidate_rows": len(candidates)}), flush=True)
    tokens = token_keys(all_rows, tokenizer)
    for index, (row, token) in enumerate(zip(all_rows, tokens)):
        canonical = identity.canonical(row["text"])
        template = identity.template(row["text"])
        row["canonical_sha256"] = digest(canonical)
        row["template_sha256"] = digest(template)
        row["tokenized_256_sha256"] = token
        row["script_origin"] = identity.script(row["text"])
        for mapping, key in ((by_canonical, canonical), (by_template, template), (by_token, token)):
            if key in mapping:
                union.union(index, mapping[key])
            else:
                mapping[key] = index
        if row["source"] == "fgrc_scd":
            case = row["case_id"]
            if case in by_case:
                union.union(index, by_case[case])
            else:
                by_case[case] = index
        for other in near.add(template, index):
            union.union(index, other)
        if index % 10000 == 0:
            print(json.dumps({"phase": "grouping", "rows_completed": index,
                              "total_rows": len(all_rows)}), flush=True)
    groups = collections.defaultdict(list)
    for index, row in enumerate(all_rows):
        groups[union.find(index)].append((index, row))
    safe_groups, excluded, conflicts = [], [], []
    seen_candidate = set()
    for members in groups.values():
        new = [row for index, row in members if index >= nprotected]
        if not new:
            continue
        existing = [row for index, row in members if index < nprotected]
        if existing:
            excluded.append({"candidate_rows": len(new),
                "candidate_ids": [row["record_id"] for row in new],
                "matched_protected_examples": [row["record_id"] for row in existing[:5]],
                "protected_splits": sorted({row["protected_split"] for row in existing})})
            continue
        # A case may deliberately provide both normal and fraudulent messages.
        # Keep these together; only identical canonical texts with contradictory
        # risk annotations are ambiguous. Case membership is not a class label.
        canonical_risks = collections.defaultdict(set)
        for row in new:
            canonical_risks[row["canonical_sha256"]].add(row.get("risk_label", int(row["label"] > 0)))
        contradictions = [key for key, values in canonical_risks.items() if len(values) > 1]
        if contradictions:
            conflicts.append({"candidate_ids": [row["record_id"] for row in new],
                              "contradictory_canonical_hashes": contradictions})
            continue
        group_id = digest("domain_v2:" + min(row["record_id"] for row in new))
        unique = []
        for row in new:
            if row["canonical_sha256"] in seen_candidate:
                continue
            seen_candidate.add(row["canonical_sha256"])
            row["group_id"] = group_id
            unique.append(row)
        if unique:
            safe_groups.append(unique)
    return safe_groups, {"protected_original_rows": nprotected, "candidate_rows": len(candidates),
        "safe_groups": len(safe_groups), "safe_rows": sum(map(len, safe_groups)),
        "protected_overlap_excluded_rows": sum(row["candidate_rows"] for row in excluded),
        "excluded_groups": excluded, "coarse_risk_conflict_groups": conflicts,
        "filter_policy": "Joint union of canonical, normalized template, 256-token input, SimHash near duplicates and FGRC case ID. Exclude every candidate group connected transitively to any baseline train/validation/test or external diagnostic row. Neither labels nor predictions determine overlap exclusion."}


def split_groups(groups, seed=20261023):
    strata = collections.defaultdict(list)
    for rows in groups:
        source = "+".join(sorted({row["source"] for row in rows}))
        category = "+".join(sorted({row["source_label"] for row in rows}))
        strata[(source, category)].append(rows)
    output = {"train": [], "validation": [], "test": []}
    for key, values in sorted(strata.items()):
        values.sort(key=lambda rows: digest(f"{seed}:" + rows[0]["group_id"]))
        counts = collections.Counter()
        total = sum(map(len, values))
        target = {"train": total * .8, "validation": total * .1, "test": total * .1}
        for rows in sorted(values, key=lambda rows: -len(rows)):
            name = max(output, key=lambda name: (target[name] - counts[name]) / max(1, target[name]))
            output[name].append(rows)
            counts[name] += len(rows)
    return output


def cap_groups(groups, source, cap):
    """A deterministic category-balanced cap applied after split assignment."""
    categories = collections.defaultdict(list)
    for rows in groups:
        matching = [row for row in rows if row["source"] == source]
        if not matching:
            continue
        categories[matching[0]["source_label"]].append(matching)
    for values in categories.values():
        values.sort(key=lambda rows: digest("cap:" + rows[0]["group_id"]))
    chosen, total = [], 0
    while categories:
        progressed = False
        for category in sorted(list(categories)):
            if not categories[category]:
                del categories[category]
                continue
            rows = categories[category].pop(0)
            if total + len(rows) <= cap:
                chosen.extend(rows)
                total += len(rows)
                progressed = True
        if not progressed:
            break
    return chosen


def augment(rows, identity):
    output = list(rows)
    for row in rows:
        converted = identity.to_traditional.convert(row["text"])
        if converted != row["text"]:
            output.append({**row, "text": converted, "record_id": row["record_id"] + ":s2t",
                "script_origin": "traditional_converted", "conversion": "OpenCC s2t,after_split",
                "original_record_id": row["record_id"]})
    return output


def audit_external(rows, external, identity, tokenizer, output_dir):
    """Recompute external exclusions against this revision, using text only."""
    unique = {}
    for row in rows:
        template = identity.template(row["text"])
        unique.setdefault(template, row)
    main = list(unique.values())
    index = TemplateIndex()
    canonical, templates, tokens = {}, {}, {}
    for number, (template, row) in enumerate(unique.items()):
        index.add(template, number)
        canonical.setdefault(digest(identity.canonical(row["text"])), number)
        templates.setdefault(digest(template), number)
    for number, value in enumerate(token_keys(main, tokenizer)):
        tokens.setdefault(value, number)
    matches = []
    for external_index, (row, token) in enumerate(zip(external, token_keys(external, tokenizer))):
        template = identity.template(row["text"])
        candidates = [number for number in index.add(template, len(main) + external_index) if number < len(main)]
        for mapping, key in ((canonical, digest(identity.canonical(row["text"]))),
                             (templates, digest(template)), (tokens, token)):
            if key in mapping:
                candidates.append(mapping[key])
        if not candidates:
            continue
        candidates = sorted(set(candidates))
        other = main[candidates[0]]
        other_template = identity.template(other["text"])
        grams = {template[i:i + 3] for i in range(max(1, len(template) - 2))}
        other_grams = {other_template[i:i + 3] for i in range(max(1, len(other_template) - 2))}
        matches.append({"record_id": row["record_id"], "training_match_id": other["record_id"],
            "similarity": len(grams & other_grams) / max(1, len(grams | other_grams)),
            "matched_record_ids": [main[number]["record_id"] for number in candidates]})
    excluded = sorted(row["record_id"] for row in matches)
    remaining = [row for row in external if row["record_id"] not in excluded]
    policy = "Text-only canonical/template/256-token identity or character-trigram SimHash(Hamming<=6,4x16bit LSH,Jaccard>=0.75) against domain_v2 train+validation. Neither model scores nor labels were used."
    audit = {"created_at": datetime.now(timezone.utc).isoformat(), "revision": "domain_v2",
        "policy": policy, "pure_text_filter_policy": policy,
        "excluded_record_ids": excluded, "matches": matches, "original_rows": len(external),
        "evaluated_rows": len(remaining),
        "source_jsonl_sha256": sha256_file(output_dir / "external_mudou_binary.jsonl"),
        "evaluated_record_order_sha256": digest("\n".join(row["record_id"] for row in remaining) + "\n"),
        "order_hash_serialization": "UTF-8 record_id lines in original order, final newline",
        "evaluation_role": "Already-observed baseline development diagnostic; not an untouched final benchmark",
        "prepared_files_modified": False}
    write_json(output_dir / "external_near_duplicates.json", audit)
    return audit


def prepare_revision(output_dir=None, baseline_dir=None):
    baseline_dir = Path(baseline_dir or ROOT / "data/prepared")
    output_dir = Path(output_dir or ROOT / "data/prepared_domain_v2")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Prepared revision already exists: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline_manifest = json.loads((baseline_dir / "manifest.json").read_text(encoding="utf-8"))
    baseline = {name: load_jsonl(baseline_dir / info["filename"])
                for name, info in baseline_manifest["files"].items()}
    for name, info in baseline_manifest["files"].items():
        if sha256_file(baseline_dir / info["filename"]) != info["sha256"]:
            raise ValueError(f"Baseline source changed: {name}")
    candidates = read_candidates(ROOT / "data/raw")
    identity = TextIdentity()
    tokenizer = MessageTokenizer(ROOT / "artifacts/pretrained/vocab.txt", max_length=256)
    groups, filtering = group_and_filter(candidates, baseline, tokenizer, identity)
    assignment = split_groups(groups)
    selected = {}
    caps = {"train": (10000, 5000), "validation": (1500, 700), "test": (1500, 700)}
    for name, values in assignment.items():
        fgrc_cap, mudou_cap = caps[name]
        selected[name] = {"fgrc": cap_groups(values, "fgrc_scd", fgrc_cap),
                          "mudou": cap_groups(values, "mudou_sms", mudou_cap)}
    new_training_originals = selected["train"]["fgrc"] + selected["train"]["mudou"]
    new_training = augment(new_training_originals, identity)
    train = baseline["train"] + new_training
    validation = baseline["validation"] + selected["validation"]["fgrc"] + selected["validation"]["mudou"]
    fgrc_test = selected["test"]["fgrc"]
    fgrc_traditional = [{**row, "text": identity.to_traditional.convert(row["text"]),
        "script_origin": "traditional_converted", "conversion": "OpenCC s2t,heldout_same_case_test_identity",
        "original_record_id": row["record_id"]} for row in fgrc_test]
    # Reuse explicitly identified baseline held-out normal rows only as the
    # negative side of this binary report, never as new training or validation.
    binary_test = [{**row, "risk_label": 0, "evaluation_role": "paired_baseline_test_normal_subset"}
                   for row in baseline["test"] if row["source"] == "mudou_sms" and row["label"] == 0]
    binary_test += [{**row, "evaluation_role": "new_mudou_trainfile_reserved_group"}
                    for row in selected["test"]["mudou"]]
    output = {**baseline, "train": train, "validation": validation,
              "fgrc_test": fgrc_test, "fgrc_traditional_converted": fgrc_traditional,
              "binary_domain_test": binary_test}
    # All split identity checks use actual text and token arrays, not inherited
    # metadata that might become stale after script augmentation.
    logical = {"train": train, "validation": validation,
               "test": baseline["test"] + fgrc_test + binary_test,
               "external": baseline["external_mudou_binary"] + baseline["external_unreviewed"]}
    maps = {}
    for name, rows in logical.items():
        keys = token_keys(rows, tokenizer)
        maps[name] = {"canonical": {digest(identity.canonical(row["text"])) for row in rows},
                      "template": {digest(identity.template(row["text"])) for row in rows},
                      "tokenized_256": set(keys), "group": {row["group_id"] for row in rows},
                      "fgrc_case": {row["case_id"] for row in rows if row["source"] == "fgrc_scd"}}
    overlap = {}
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        overlap[f"{left}:{right}"] = {key: len(maps[left][key] & maps[right][key]) for key in maps[left]}
    if any(any(values.values()) for values in overlap.values()):
        raise ValueError(f"Revision contains cross-split identities: {overlap}")
    # Baseline external was already diagnosed and contains four documented
    # normal near-duplicates; it remains a seen diagnostic, not model selection.
    files = {}
    for name, rows in output.items():
        path = output_dir / f"{name}.jsonl"
        if name in baseline and name not in ("train", "validation"):
            shutil.copyfile(baseline_dir / baseline_manifest["files"][name]["filename"], path)
        else:
            write_jsonl(path, rows)
        files[name] = {"filename": path.name, "path": str(path), "sha256": sha256_file(path), **summarize(rows)}
        if name in ("external_mudou_binary", "binary_domain_test"):
            files[name]["risk_label_counts"] = dict(collections.Counter(str(row["risk_label"]) for row in rows))
            files[name]["task"] = "binary_normal_vs_unwanted_only"
    sources = {key: dict(value) for key, value in baseline_manifest["sources"].items()}
    # This revision adds coarse-label supervision; do not inherit the baseline
    # description that excluded every source spam row from training.
    sources["mudou_sms"]["semantics"] = (
        "Chinese SMS: source 0 means normal and source 1 means unwanted/spam, "
        "without a reliable fraud-versus-advertising subtype. Baseline training-file "
        "normal rows remain normal=0. This revision adds overlap-filtered original "
        "TRAIN-file unwanted rows using label=-1, risk_label=1, "
        "supervision=binary_unwanted and -log(P(spam)+P(scam)) loss; source spam "
        "is never forced into a fine-grained class. New unwanted groups are "
        "reserved for validation/test before augmentation. The original TEST file "
        "remains a previously observed binary development diagnostic."
    )
    sources["fgrc_scd"] = {"url": "https://huggingface.co/datasets/Abooooo/FGRC-SCD",
        "download_url": "https://huggingface.co/datasets/Abooooo/FGRC-SCD/resolve/main/FGRC-SCD-sms.zip?download=true",
        "archive": "fgrc_sms.zip", "archive_sha256": sha256_file(ROOT / "data/raw/fgrc_sms.zip"),
        "card": "data/raw/fgrc_README.md", "license": "MIT stated in dataset card; underlying source-case terms still apply",
        "semantics": "Generated SMS from CCF23-EVAL task6 cases; 无风险->normal0, nine named risk categories->scam2. Actual case IDs preserved and kept within one split.",
        "limitations": "Generated message-form data, not an independent real-SMS corpus. Existing Telecom source lacks case IDs, so cross-source case identity can only be screened using text similarity and cannot be guaranteed completely."}
    external_audit = audit_external(train + validation, baseline["external_mudou_binary"],
                                   identity, tokenizer, output_dir)
    manifest = {**baseline_manifest, "created_at": datetime.now(timezone.utc).isoformat(),
        "revision": "domain_v2", "baseline_manifest_sha256": sha256_file(baseline_dir / "manifest.json"),
        "files": files, "sources": sources,
        "partial_supervision": {"label": -1, "risk_label": 1, "supervision": "binary_unwanted",
            "loss": "-log(P(spam)+P(scam)); never force unknown source spam into a fine-grained class",
            "metrics": "Exclude partial labels from three-class confusion metrics; include risk_label in binary unwanted metrics"},
        "revision_preparation": {"added_training_originals": len(new_training_originals),
            "added_training_with_traditional": len(new_training), "caps_after_group_split": caps,
            "selected": {name: {source: len(rows) for source, rows in item.items()} for name, item in selected.items()},
            "cross_split_identity_overlap": overlap,
            "near_duplicate_separation": "Joint union index before new source splitting; baseline main groups retained. All new near-connected/case-connected groups excluded if they touch any baseline row.",
            "fg_rc_case_identity": "FGRC case IDs are isolated across all revision splits; unavailable case IDs in older Telecom corpus remain an explicit limitation",
            "baseline_test": "Previously observed diagnostic after baseline development; no claims of an untouched final independent benchmark"},
        "external_diagnostic_identity_audit": {"file": "external_near_duplicates.json",
            "original_rows": external_audit["original_rows"],
            "evaluated_rows": external_audit["evaluated_rows"],
            "excluded_record_ids": external_audit["excluded_record_ids"]},
        "limitations": baseline_manifest["limitations"] + [
            "Baseline external results were observed before this domain repair and are development diagnostics, never used for threshold selection.",
            "FGRC SMS is generated from cases, not captured real SMS. Its nine risk classes map to scam under provider labels.",
            "Mudou TRAIN unwanted is coarse-labelled and receives partial binary supervision. New reserved unwanted groups are genuine message texts but lack spam-versus-scam subtype ground truth.",
            "Binary domain test reuses the explicitly identified normal subset of the original held-out main test alongside newly reserved Mudou TRAIN positives.",
            "The baseline model is a warm start whose training is limited to the retained baseline training split. New heldouts were identity-filtered against that training before selection."]}
    write_json(output_dir / "source_documentation.json", sources)
    write_json(output_dir / "overlap_filter_details.json", filtering)
    audit = {"passed": True, "created_at": datetime.now(timezone.utc).isoformat(),
        "all_prepared_hashes_verified": True, "cross_split_overlap": overlap,
        "new_source_case_and_near_groups_split_before_caps_and_augmentation": True,
        "partial_spam_not_mislabelled_as_scam": True, "baseline_files_preserved": True,
        "baseline_unchanged_test_hashes": {name: files[name]["sha256"] == baseline_manifest["files"][name]["sha256"]
            for name in ("test", "test_traditional_converted", "external_mudou_binary", "external_unreviewed")},
        "selected": manifest["revision_preparation"]["selected"],
        "filtered_candidate_rows": filtering["protected_overlap_excluded_rows"],
        "source_limitations": sources["fgrc_scd"]["limitations"]}
    write_json(output_dir / "data_audit.json", audit)
    # The supervisor treats this file as readiness. Publish it last, after all
    # content files and audit reports are complete and identities have passed.
    write_json(output_dir / "manifest.json", manifest)
    print(json.dumps({"phase": "domain_revision_ready", "directory": str(output_dir),
        "files": {name: info["rows"] for name, info in files.items()},
        "cross_split_overlap": overlap}, ensure_ascii=False), flush=True)
    return manifest


def audit_revision_hashes(output_dir):
    """Read-only byte verification plus inspection of the saved split audit.

    This deliberately does not rerun template, case, or near-duplicate grouping.
    Its result distinguishes freshly verified hashes from the earlier stored
    separation audit; neither the dataset nor its manifest is rewritten.
    """
    output_dir = Path(output_dir)
    manifest_path = output_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checked = {}
    root = output_dir.resolve()
    for name, details in manifest["files"].items():
        path = (root / details["filename"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Invalid dataset file path: {name}")
        actual = sha256_file(path)
        if actual != details["sha256"]:
            raise ValueError(f"Dataset hash mismatch: {name}")
        checked[name] = {"sha256": actual, "rows_from_manifest": details["rows"]}
    recorded = json.loads((output_dir / "data_audit.json").read_text(encoding="utf-8"))
    overlaps = recorded.get("cross_split_overlap", {})
    if recorded.get("passed") is not True or not overlaps or any(
        any(values.values()) for values in overlaps.values()
    ):
        raise ValueError("Stored separation audit is absent, failed, or contains overlaps")
    return {"passed": True, "read_only": True,
        "verification_scope": "Fresh dataset-file SHA256 checks and inspection of the previously stored separation audit; no grouping recalculation",
        "manifest_sha256": sha256_file(manifest_path), "checked_files": checked,
        "recorded_separation_audit_passed": True,
        "recorded_separation_audit_created_at": recorded.get("created_at"),
        "grouping_recalculated": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-dir", type=Path, default=ROOT / "data/prepared",
        help="Existing immutable baseline dataset (default: project data/prepared)")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/prepared_domain_v2",
        help="New preparation directory, or existing revision to verify; nonempty preparation destinations are preserved")
    parser.add_argument("--audit-only", "--hash-only", dest="audit_only", action="store_true",
        help="Read-only SHA256 verification and stored-audit inspection; does not rerun grouping or write files")
    args = parser.parse_args(argv)
    if args.audit_only:
        print(json.dumps(audit_revision_hashes(args.output_dir), ensure_ascii=False, indent=2))
        return 0
    prepare_revision(output_dir=args.output_dir, baseline_dir=args.baseline_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
