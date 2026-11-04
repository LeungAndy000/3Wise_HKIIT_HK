"""Reproducible research SMS corpus preparation, with explicit source semantics.

This module never imports LinkWise or its URL vocabulary.  Dataset archives are
retained, and prepared revisions must use a new output directory.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

LABELS = {0: "normal", 1: "spam", 2: "scam"}
SOURCES = {
    "fbs_sms": {
        "url": "https://github.com/Cypher-Z/FBS_SMS_Dataset",
        "archive_url": "https://codeload.github.com/Cypher-Z/FBS_SMS_Dataset/zip/refs/heads/master",
        "archive": "fbs_sms.zip",
        "license": "No explicit SPDX license; public research release requests source attribution and CCS2020 citation.",
        "citation": "Zhang et al. (2020), Lies in the Air: Characterizing Fake-base-station Spam Ecosystem in China, doi:10.1145/3372297.3417257",
        "semantics": "Real de-identified fake-base-station SMS. AD:* means advertising spam; FR:* means fraud. IL:* and Other are excluded because they do not define the requested three-class target.",
        "limitations": "Spam reflects unsolicited fake-base-station delivery, which text alone cannot always establish. Word segmentation and anonymization are source preprocessing artifacts.",
    },
    "mudou_sms": {
        "url": "https://github.com/shaonianruntu/Spam-Message-Classification",
        "archive_url": "https://codeload.github.com/shaonianruntu/Spam-Message-Classification/zip/refs/heads/master",
        "archive": "mudou_mirror.zip",
        "license": "No license is specified in this public mirror. Upstream provenance and redistribution/commercial rights are unresolved; local research prototype only.",
        "semantics": "Chinese SMS: 0 normal, 1 spam. Only original training-file normal rows enter three-class training; spam rows cannot be reliably divided into fraud versus advertising and are excluded. Original test file is reserved for binary external evaluation only.",
        "limitations": "Mirror rather than original data collector. Some normal-labelled rows contain marketing, so class labels reflect source annotation, not consent inferred from wording.",
    },
    "telecom_fraud_5": {
        "url": "https://github.com/ChangMianRen/Telecom_Fraud_Texts_5",
        "archive_url": "https://codeload.github.com/ChangMianRen/Telecom_Fraud_Texts_5/zip/refs/heads/main",
        "archive": "telecom_fraud_5.zip",
        "license": "Repository GPL-3.0 plus README explicitly restricts dataset to university/research-institution scientific research and prohibits commercial use.",
        "semantics": "label00 normal ->0; label01 government impersonation, label02 loans, label03 customer-service impersonation, label04 acquaintance impersonation ->2.",
        "limitations": "Mixed normal SMS and case-derived/generated fraud messages or phone dialogue; these are not all independently captured real SMS. Do not interpret combined test performance as real-SMS-only deployment accuracy.",
        "paper": "https://doi.org/10.3390/app142411628",
    },
    "smishing_imc2025": {
        "url": "https://github.com/reportsmishing/Smishing-Dataset-IMC25",
        "archive_url": "https://codeload.github.com/reportsmishing/Smishing-Dataset-IMC25/zip/refs/heads/main",
        "archive": "smishing_imc.zip",
        "license": "CC-BY-4.0",
        "citation": "Agarwal et al. (2025), Fishing for Smishing: Understanding SMS Phishing Infrastructure and Strategies by Mining Public User Reports, doi:10.1145/3730567.3764431",
        "semantics": "Preserve Chinese-language public reports as unlabelled external diagnostics. scam_type is a topical field and is NOT a validated normal/spam/scam label.",
        "limitations": "Chinese subset includes anti-fraud notices, genuine-looking appointments, truncated messages, and ambiguous wrong-number contacts. All-scam mapping would corrupt the benchmark. No formal accuracy metric is justified without independent label review.",
    },
    "nus_sms": {
        "url": "https://github.com/kite1988/nus-sms-corpus",
        "archive_url": "https://codeload.github.com/kite1988/nus-sms-corpus/zip/refs/heads/master",
        "archive": "nus_sms.zip",
        "license": "Public research release requests paper attribution; no explicit SPDX license in repository.",
        "citation": "Chen and Kan (2013), Creating a Live, Public Short Message Service Corpus: The NUS SMS Corpus, Language Resources and Evaluation 47(2).",
        "semantics": "Volunteer personal SMS in Simplified and genuine Traditional Chinese; no scam/spam classification labels. Retained archive only, not assigned guessed ground truth.",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class TextIdentity:
    """Script-independent canonical identities and template-group fingerprints."""

    def __init__(self):
        from opencc import OpenCC
        self.to_simple = OpenCC("t2s")
        self.to_traditional = OpenCC("s2t")

    def script(self, text: str) -> str:
        t2s = self.to_simple.convert(text) != text
        s2t = self.to_traditional.convert(text) != text
        return "mixed" if t2s and s2t else "traditional" if t2s else "simplified" if s2t else "shared_or_other"

    def canonical(self, text: str) -> str:
        text = self.to_simple.convert(unicodedata.normalize("NFKC", text)).lower()
        return re.sub(r"\s+", "", text)

    def template(self, text: str) -> str:
        text = self.canonical(text)
        text = re.sub(r"https?://[^\s，。；！、<>]+|www\.[^\s，。；！、<>]+", "URL", text)
        text = re.sub(r"[a-z0-9][a-z0-9.-]*\.(?:com|cn|net|org|hk|tw|cc|xyz)(?:/[^\s，。；！、<>]*)?", "URL", text)
        text = re.sub(r"[a-z0-9_.+-]+@[a-z0-9.-]+", "EMAIL", text)
        text = re.sub(r"<[^<>]+>", "CONTACT", text)
        text = re.sub(r"url[a-z]*|cellphone|hotline|phone|digit|name|place|qq|wechat", "CONTACT", text, flags=re.I)
        text = re.sub(r"\d+(?:[.,:/-]\d+)*", "NUMBER", text)
        return re.sub(r"[^\u3400-\u9fffA-Za-z]", "", text)


def decode_csv(content: bytes) -> str:
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise ValueError("Dataset text does not decode losslessly as UTF-8 or GB18030")


def make_row(text: str, label: int | None, source: str, record_id: str, *, source_label: str, origin: str, **extra) -> dict:
    return {"text": text.strip(), "label": label, "source": source,
            "record_id": f"{source}:{record_id}", "source_label": source_label,
            "text_origin": origin, "script_origin": "original", **extra}


def read_sources(raw_dir: Path) -> tuple[list[dict], list[dict], list[dict], dict]:
    rows, external, unreviewed = [], [], []
    raw_counts = collections.Counter()
    with zipfile.ZipFile(raw_dir / "fbs_sms.zip") as archive:
        for member in sorted(archive.namelist()):
            category = member.rsplit("/", 1)[-1]
            if not category.startswith(("AD:", "FR:")):
                continue
            label = 1 if category.startswith("AD:") else 2
            for index, text in enumerate(archive.read(member).decode("utf-8").splitlines()):
                # Remove segmentation spaces only. Actual source content is retained.
                text = re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])", "", text)
                if text.strip():
                    rows.append(make_row(text, label, "fbs_sms", f"{category}:{index}", source_label=category, origin="real_deidentified_sms"))
                    raw_counts[f"fbs_sms:{label}"] += 1
    with zipfile.ZipFile(raw_dir / "mudou_mirror.zip") as archive:
        for member in sorted(archive.namelist()):
            if not member.endswith((".train", ".test")):
                continue
            for index, line in enumerate(archive.read(member).decode("utf-8").splitlines()):
                parts = line.split("\t")
                if len(parts) < 2 or parts[0] not in ("0", "1"):
                    continue
                label, text = int(parts[0]), parts[1].strip()
                if len(text) < 8 or len(re.findall(r"[\u3400-\u9fff]", text)) < 3:
                    continue
                item = make_row(text, label if label == 0 else None, "mudou_sms", f"{Path(member).name}:{index}", source_label=parts[0], origin="labelled_sms_mirror")
                if member.endswith(".test"):
                    item["risk_label"] = label
                    item["evaluation_task"] = "binary_normal_vs_unwanted"
                    external.append(item)
                    raw_counts[f"mudou_official_test:{label}"] += 1
                elif label == 0:
                    rows.append(item)
                    raw_counts["mudou_sms:0"] += 1
    with zipfile.ZipFile(raw_dir / "telecom_fraud_5.zip") as archive:
        for member in sorted(archive.namelist()):
            if not member.endswith(".csv"):
                continue
            label = 0 if member.endswith("label00-last.csv") else 2
            reader = csv.DictReader(io.StringIO(decode_csv(archive.read(member))))
            for index, item in enumerate(reader):
                text = item["content"].strip()
                if len(text) >= 8:
                    rows.append(make_row(text, label, "telecom_fraud_5", f"{Path(member).name}:{index}", source_label=item["label"], origin="normal_sms_or_text" if label == 0 else "case_derived_or_generated_sms_and_dialogue"))
                    raw_counts[f"telecom_fraud_5:{label}"] += 1
    with zipfile.ZipFile(raw_dir / "smishing_imc.zip") as archive:
        member = next(name for name in archive.namelist() if name.endswith("final_dataset_output.csv"))
        reader = csv.DictReader(io.StringIO(archive.read(member).decode("utf-8-sig")))
        for index, item in enumerate(reader):
            if item["language"] == "Chinese":
                unreviewed.append(make_row(item["text"], None, "smishing_imc2025", str(index), source_label=item["scam_type"], origin="public_report_needs_label_review", source_record=item))
                raw_counts["smishing_imc2025:unreviewed"] += 1
    return rows, external, unreviewed, dict(raw_counts)


class UnionFind:
    def __init__(self, count):
        self.parent = list(range(count))

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[max(left, right)] = min(left, right)


def simhash(text: str) -> int:
    tokens = {text[i:i + 3] for i in range(max(1, len(text) - 2))}
    values = [int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big") for token in tokens]
    sums = [sum(1 if value >> bit & 1 else -1 for value in values) for bit in range(64)]
    return sum(1 << bit for bit, value in enumerate(sums) if value >= 0)


def assign_groups(rows: list[dict], identity: TextIdentity) -> tuple[list[dict], dict]:
    """Union exact normalized templates and close 3-gram SimHash neighbours.

    Four 16-bit bands are candidate retrieval, followed by Hamming <=6 and
    3-gram Jaccard >=0.75. This is a reproducible heuristic, not a guarantee that
    every possible campaign/paraphrase has been identified.
    """
    union = UnionFind(len(rows))
    exact, bands = {}, collections.defaultdict(list)
    templates, fingerprints = [], []
    near_edges = 0
    for index, row in enumerate(rows):
        template = identity.template(row["text"])
        templates.append(template)
        fingerprint = simhash(template)
        fingerprints.append(fingerprint)
        if template in exact:
            union.union(index, exact[template])
        else:
            exact[template] = index
        candidates = set()
        for band in range(4):
            key = (band, (fingerprint >> (band * 16)) & 0xffff)
            candidates.update(bands[key])
            bands[key].append(index)
        grams = None
        for other in candidates:
            if (fingerprint ^ fingerprints[other]).bit_count() > 6:
                continue
            if abs(len(template) - len(templates[other])) > max(10, len(template) * .2):
                continue
            if grams is None:
                grams = {template[i:i+3] for i in range(max(1, len(template)-2))}
            other_grams = {templates[other][i:i+3] for i in range(max(1, len(templates[other])-2))}
            if len(grams & other_grams) / max(1, len(grams | other_grams)) >= .75:
                union.union(index, other)
                near_edges += 1
    grouped = collections.defaultdict(list)
    for index, row in enumerate(rows):
        grouped[union.find(index)].append(row)
    output, conflicts = [], []
    for members in grouped.values():
        group_id = hashlib.sha256(min(identity.template(row["text"]) for row in members).encode()).hexdigest()
        # Labels conflict across some advertising/normal templates. Exclude the
        # whole ambiguous group instead of picking a convenient label.
        if len({row["label"] for row in members}) != 1:
            conflicts.append({"group_id": group_id, "rows": len(members), "labels": sorted({row["label"] for row in members})})
            continue
        for row in members:
            row["group_id"] = group_id
            row["script_origin"] = identity.script(row["text"])
            row["canonical_sha256"] = hashlib.sha256(identity.canonical(row["text"]).encode()).hexdigest()
            row["template_sha256"] = hashlib.sha256(identity.template(row["text"]).encode()).hexdigest()
            output.append(row)
    # Exact duplicate texts within a group are retained once regardless ofsource.
    deduplicated = {}
    for row in output:
        deduplicated.setdefault(row["canonical_sha256"], row)
    return list(deduplicated.values()), {"method": "script-independent URL/contact/number-normalized templates + 64bit character-trigram SimHash,4x16bit LSH,Hamming<=6,Jaccard>=0.75", "near_duplicate_union_edges": near_edges, "raw_groups": len(grouped), "ambiguous_label_groups_excluded": conflicts, "exact_duplicates_excluded": len(output) - len(deduplicated)}


def stratified_group_split(rows: list[dict], seed: int = 20261023) -> dict[str, list[dict]]:
    """Deterministic 80/10/10 by source and label at intact group level."""
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["group_id"]].append(row)
    strata = collections.defaultdict(list)
    for group, members in groups.items():
        strata[(members[0]["label"], "+".join(sorted({r["source"] for r in members})))].append((group, members))
    result = {"train": [], "validation": [], "test": []}
    for key, members in sorted(strata.items()):
        members.sort(key=lambda item: hashlib.sha256(f"{seed}:{item[0]}".encode()).hexdigest())
        total = sum(len(items) for _, items in members)
        targets = {"train": total * .8, "validation": total * .1, "test": total * .1}
        counts = collections.Counter()
        # Fill the currently most under-target fraction; a large template group
        # cannot be broken merely to create cosmetically exact class counts.
        for _, items in sorted(members, key=lambda item: -len(item[1])):
            split = max(result, key=lambda name: (targets[name] - counts[name]) / max(1, targets[name]))
            result[split].extend(items)
            counts[split] += len(items)
    for name, values in result.items():
        values.sort(key=lambda row: hashlib.sha256(f"{seed}:{name}:{row['record_id']}".encode()).hexdigest())
    return result


def summarize(rows: list[dict]) -> dict:
    return {"rows": len(rows), "labels": dict(collections.Counter(str(row["label"]) for row in rows)),
            "sources": dict(collections.Counter(row["source"] for row in rows)),
            "source_labels": dict(collections.Counter(f"{row['source']}:{row['label']}" for row in rows)),
            "scripts": dict(collections.Counter(row["script_origin"] for row in rows)),
            "groups": len({row.get("group_id") for row in rows}),
            "mean_characters": sum(len(row["text"]) for row in rows) / max(1, len(rows))}


def prepare(raw_dir: Path, output_dir: Path, seed: int = 20261023) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite prepared dataset; choose a new output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    identity = TextIdentity()
    raw_rows, external, unreviewed, raw_counts = read_sources(raw_dir)
    filtered = [row for row in raw_rows if len(row["text"]) >= 8 and len(re.findall(r"[\u3400-\u9fff]", row["text"])) >= 3]
    print(json.dumps({"phase": "grouping_templates", "rows": len(filtered)}), flush=True)
    rows, grouping = assign_groups(filtered, identity)
    splits = stratified_group_split(rows, seed)
    original_training_count = len(splits["train"])
    # One alternate orthography per original training row, keeping groupidentity.
    augmented = []
    for row in splits["train"]:
        traditional = identity.to_traditional.convert(row["text"])
        if traditional != row["text"]:
            item = {**row, "text": traditional, "record_id": row["record_id"] + ":s2t", "script_origin": "traditional_converted", "conversion": "OpenCC s2t,after_split", "original_record_id": row["record_id"]}
            augmented.append(item)
    splits["train"].extend(augmented)
    converted_test = [{**row, "text": identity.to_traditional.convert(row["text"]), "script_origin": "traditional_converted", "conversion": "OpenCC s2t,heldout_same_test_identity", "original_record_id": row["record_id"]} for row in splits["test"]]
    groups = {name: {row["group_id"] for row in values} for name, values in splits.items()}
    templates = {name: {row["template_sha256"] for row in values} for name, values in splits.items()}
    canonicals = {name: {row["canonical_sha256"] for row in values} for name, values in splits.items()}
    overlaps = {}
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        overlaps[f"{left}:{right}"] = {"group_overlap": len(groups[left] & groups[right]), "template_overlap": len(templates[left] & templates[right]), "canonical_overlap": len(canonicals[left] & canonicals[right])}
    if any(any(value.values()) for value in overlaps.values()):
        raise ValueError(f"Cross-split identities found: {overlaps}")
    # External original test must not share a canonical/template with any main
    # split (including evaluation), not just the training split.
    all_templates = set.union(*templates.values())
    all_canonical = set.union(*canonicals.values())
    external_clean, external_dropped, seen_external = [], [], set()
    for row in external:
        canonical = hashlib.sha256(identity.canonical(row["text"]).encode()).hexdigest()
        template = hashlib.sha256(identity.template(row["text"]).encode()).hexdigest()
        if canonical in all_canonical or template in all_templates or canonical in seen_external:
            external_dropped.append(row["record_id"])
            continue
        seen_external.add(canonical)
        row.update(script_origin=identity.script(row["text"]), canonical_sha256=canonical, template_sha256=template, group_id=template)
        external_clean.append(row)
    for row in unreviewed:
        row["script_origin"] = identity.script(row["text"])
        row["group_id"] = hashlib.sha256(identity.template(row["text"]).encode()).hexdigest()
        row["evaluation_status"] = "unreviewed_not_gold_no_metrics"
    files = {}
    for name, values in {**splits, "test_traditional_converted": converted_test, "external_mudou_binary": external_clean, "external_unreviewed": unreviewed}.items():
        path = output_dir / f"{name}.jsonl"
        write_jsonl(path, values)
        files[name] = {"path": str(path), "filename": path.name, "sha256": sha256_file(path), **summarize(values)}
        if name == "external_mudou_binary":
            files[name]["risk_label_counts"] = dict(collections.Counter(str(row["risk_label"]) for row in values))
            files[name]["task"] = "binary_only: score risk=1-P(normal), compare against original spam/normal labels; do not compute3classscammetrics"
    source_report = {}
    for source, details in SOURCES.items():
        archive = raw_dir / details["archive"]
        source_report[source] = {**details, "archive_sha256": sha256_file(archive) if archive.exists() else None, "archive_bytes": archive.stat().st_size if archive.exists() else None}
    manifest = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "seed": seed,
                "label_names": {str(key): value for key, value in LABELS.items()}, "raw_counts": raw_counts,
                "preparation": {"filtered_original_rows": len(filtered), "deduplicated_rows": len(rows), "original_train_rows": original_training_count, "traditional_training_augmentation_rows": len(augmented), "split": "80/10/10 stratifiedbylabelandsource, intacttemplate/near-duplicategroups", "grouping": grouping, "cross_split_overlap": overlaps},
                "files": files, "sources": source_report,
                "external_official_test_overlap_rows_excluded": len(external_dropped), "external_excluded_record_ids": external_dropped,
                "limitations": ["Research prototype only: dataset permissions are mixed, including explicit noncommercial research restrictions and unresolved mirror licensing.", "Main evaluation mixes real de-identified SMS with case-derived/generated fraud messages/dialogue; report per-source results as well as combinedmetrics.", "Converted Traditional Chinese test is a paired orthographic robustness test, not an independent native Hong Kong/Taiwan SMS benchmark.", "Script inference uses OpenCC change detection; shared characters do not establish a speaker's region or language variety.", "Template clustering is a documented heuristic and cannot guarantee separation of all semantic campaigns/paraphrases.", "External Mudou is an original held-out file from a source also contributing normal training rows, not a completely independent source for the normal class.", "External IMC Chinese reports are retained unreviewed and are not valid ground truth merely because they were reported as suspicious.", "Absence of sender identity or consent prevents determination of legal legitimacy from text alone."]}
    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "source_documentation.json", source_report)
    print(json.dumps({"phase": "dataset_ready", "output_dir": str(output_dir), "splits": {name: item["rows"] for name, item in files.items()}, "manifest": str(output_dir / "manifest.json")}), flush=True)
    return manifest


def download_sources(raw_dir: Path) -> None:
    import requests
    raw_dir.mkdir(parents=True, exist_ok=True)
    for source, details in SOURCES.items():
        path = raw_dir / details["archive"]
        if path.exists():
            continue
        response = requests.get(details["archive_url"], timeout=120)
        response.raise_for_status()
        # No ZIP extraction: source filenames containing ':' are invalid onWindows.
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            if not archive.namelist():
                raise ValueError(f"Empty dataset archive: {source}")
        path.write_bytes(response.content)
        print(json.dumps({"downloaded": source, "bytes": len(response.content)}), flush=True)


def audit_prepared(data_dir: Path) -> dict:
    """Verify every prepared byte hash and the logical split invariants."""
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    loaded, checked = {}, {}
    for name, info in manifest["files"].items():
        path = data_dir / info["filename"]
        actual_hash = sha256_file(path)
        if actual_hash != info["sha256"]:
            raise ValueError(f"Data hash changed: {name}")
        values = load_jsonl(path)
        if len(values) != info["rows"]:
            raise ValueError(f"Data row count changed: {name}")
        loaded[name] = values
        checked[name] = {"rows": len(values), "sha256": actual_hash}
    for name in ("train", "validation", "test", "test_traditional_converted"):
        if any(row["label"] not in LABELS for row in loaded[name]):
            raise ValueError(f"Invalid supervised label: {name}")
    original_training = {row["record_id"] for row in loaded["train"] if row["script_origin"] != "traditional_converted"}
    train_augmented = [row for row in loaded["train"] if row["script_origin"] == "traditional_converted"]
    if any(row["original_record_id"] not in original_training for row in train_augmented):
        raise ValueError("Traditional training augmentation was sourced outside training")
    original_test = loaded["test"]
    paired = loaded["test_traditional_converted"]
    if len(original_test) != len(paired) or any(
        original["record_id"] != converted["original_record_id"]
        or original["label"] != converted["label"]
        or original["group_id"] != converted["group_id"]
        for original, converted in zip(original_test, paired)
    ):
        raise ValueError("Converted test is not paired to the held-out original test")
    overlaps = {}
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        overlap = {key: len({row[key] for row in loaded[left]} & {row[key] for row in loaded[right]})
                   for key in ("group_id", "canonical_sha256", "template_sha256")}
        if any(overlap.values()):
            raise ValueError(f"Cross-split leakage: {left}:{right}: {overlap}")
        overlaps[f"{left}:{right}"] = overlap
    if any(row["label"] is not None for row in loaded["external_unreviewed"]):
        raise ValueError("Unreviewed external messages have been assigned fabricated labels")
    if any(row["risk_label"] not in (0, 1) or (row["risk_label"] == 1 and row["label"] is not None)
           for row in loaded["external_mudou_binary"]):
        raise ValueError("External binary spam was incorrectly relabelled as a scam class")
    return {"passed": True, "checked_at": datetime.now(timezone.utc).isoformat(),
            "checked_files": checked, "cross_split_overlap": overlaps,
            "training_augmentation_origin_verified": True,
            "paired_traditional_test_verified": True,
            "unreviewed_external_not_treated_as_gold": True,
            "external_spam_not_forced_to_scam": True,
            "formal_native_traditional_test_rows": sum(row["script_origin"] == "traditional" for row in original_test),
            "limitations": manifest["limitations"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/prepared"))
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if args.audit_only:
        report = audit_prepared(args.output_dir)
        write_json(args.output_dir / "data_audit.json", report)
        print(json.dumps({"passed": report["passed"], "report": str(args.output_dir / "data_audit.json")}))
        return
    if args.download:
        download_sources(args.raw_dir)
    prepare(args.raw_dir, args.output_dir, args.seed)


if __name__ == "__main__":
    main()
