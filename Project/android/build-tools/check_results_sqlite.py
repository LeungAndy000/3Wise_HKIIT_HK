#!/usr/bin/env python3
"""Verify the shipped result predicates and keyset policy on synthetic host SQLite.

This does not execute Android lifecycle/UI code or touch an installed SMS database.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
JAVA = ROOT / "android/app/src/main/java/hk/wisemessage/app"


def strings(expression):
    return "".join(json.loads(value) for value in re.findall(r'"(?:\\.|[^"\\])*"', expression))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "artifacts/android/result-browsing-qa/host_sqlite_validation.json")
    args = parser.parse_args()
    store_path, filter_path = JAVA / "MessageStore.java", JAVA / "ResultFilter.java"
    store, filters = store_path.read_text(encoding="utf-8"), filter_path.read_text(encoding="utf-8")
    harmful = strings(re.search(r'String HARMFUL_SQL\s*=([\s\S]+?);', filters).group(1))
    low = strings(re.search(r'String LOW_RISK_SQL\s*=([\s\S]+?);', filters).group(1))
    predicates = {
        "HARMFUL": f"({harmful})", "LOW_RISK": f"({low})",
        "REVIEW": f"NOT (({harmful}) OR ({low}))", "ALL": "1=1",
    }
    schema_start = store.index('db.execSQL("CREATE TABLE messages')
    schema = strings(store[schema_start:store.index(");", schema_start)])
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute(schema)
    checks = []

    def passed(name):
        checks.append(name)

    def insert(state="complete", label="normal", scam=0, unwanted=0, received=1):
        ordinal = db.execute("SELECT COALESCE(MAX(_id),0)+1 FROM messages").fetchone()[0]
        return db.execute("INSERT INTO messages(fingerprint,sender,body,received,source,state,label,is_scam,is_unwanted) "
                          "VALUES(?,?,?,?,?,?,?,?,?)",
                          (str(ordinal), "synthetic sender", "synthetic message", received, "inbox", state,
                           label, scam, unwanted)).lastrowid

    def page(category, before=0, size=25):
        size = max(1, min(25, size))
        where = predicates[category]
        params = []
        if before > 0:
            where = f"({where}) AND _id<?"
            params.append(before)
        rows = db.execute(f"SELECT * FROM messages WHERE {where} ORDER BY _id DESC LIMIT {size + 1}", params).fetchall()
        return rows[:size], len(rows) > size

    def count(category):
        return db.execute(f"SELECT COUNT(*) FROM messages WHERE {predicates[category]}").fetchone()[0]

    # Keep harmful records older than more than one hundred normal entries.
    harmful_ids = [insert(label="scam" if index % 2 else "spam", scam=index % 2, unwanted=1)
                   for index in range(57)]
    normal_ids = [insert(received=10_000 - index) for index in range(125)]
    uncertain_id = insert(label="normal", unwanted=1)
    pending_id = insert(state="pending", label=None, scam=None, unwanted=None)
    failed_id = insert(state="failed", label=None, scam=None, unwanted=None)
    null_label_id = insert(label=None, scam=None, unwanted=None)
    unknown_label_id = insert(label="unexpected")
    unknown_state_id = insert(state="future_state", label="normal")
    explicit_scam_id = insert(label="normal", scam=1)
    legacy_normal_id = insert(label="normal", scam=None, unwanted=None)
    invalid_scam_id = insert(label="normal", scam=2, unwanted=0)
    invalid_unwanted_id = insert(label="normal", scam=0, unwanted=-1)

    recent30 = db.execute("SELECT _id FROM messages ORDER BY _id DESC LIMIT 30").fetchall()
    assert not set(harmful_ids).intersection(row[0] for row in recent30)
    first, more = page("HARMFUL")
    assert len(first) == 25 and more and first[0]["_id"] == explicit_scam_id
    assert any(row["_id"] in harmful_ids for row in first)
    passed("older_harmful_records_visible_beyond_125_newer_normal_records")

    all_rows = db.execute("SELECT * FROM messages").fetchall()
    categories = ("HARMFUL", "LOW_RISK", "REVIEW")
    for row in all_rows:
        assert sum(db.execute(f"SELECT COUNT(*) FROM messages WHERE _id=? AND ({predicates[category]})",
                              (row["_id"],)).fetchone()[0] for category in categories) == 1
    assert sum(count(category) for category in categories) == count("ALL")
    passed("categories_partition_all_records_including_null_and_unknown_labels")

    assert not db.execute(f"SELECT _id FROM messages WHERE _id=? AND {predicates['LOW_RISK']}",
                          (uncertain_id,)).fetchall()
    review_ids = {row[0] for row in db.execute(f"SELECT _id FROM messages WHERE {predicates['REVIEW']}")}
    assert review_ids == {uncertain_id, pending_id, failed_id, null_label_id, unknown_label_id, unknown_state_id,
                          legacy_normal_id, invalid_scam_id, invalid_unwanted_id}
    passed("uncertain_normal_pending_failed_unknown_stay_in_review")

    low_ids = {row[0] for row in db.execute(f"SELECT _id FROM messages WHERE {predicates['LOW_RISK']}")}
    assert low_ids == set(normal_ids)
    passed("low_risk_excludes_scam_unwanted_missing_and_invalid_flags")

    seen = []
    cursor = 0
    page_lengths = []
    while True:
        rows, has_more = page("HARMFUL", cursor)
        page_lengths.append(len(rows))
        assert len(rows) <= 25
        seen.extend(row["_id"] for row in rows)
        if not has_more:
            break
        cursor = rows[-1]["_id"]
    assert seen == sorted(harmful_ids + [explicit_scam_id], reverse=True)
    assert page_lengths == [25, 25, 8]
    passed("25_row_keyset_pages_cover_every_matching_row_once")

    # Arrivals between pages must not shift the older cursor page or duplicate records.
    first, _ = page("HARMFUL")
    cursor = first[-1]["_id"]
    next_before, _ = page("HARMFUL", cursor)
    new_harmful_id = insert(label="scam", scam=1, unwanted=1)
    insert()
    next_after, _ = page("HARMFUL", cursor)
    assert [row["_id"] for row in next_after] == [row["_id"] for row in next_before]
    assert new_harmful_id == page("HARMFUL")[0][0]["_id"]
    passed("new_insertions_do_not_shift_or_duplicate_older_cursor_page")

    for requested in (-100, 0, 1, 25, 26, 10000):
        rows, _ = page("ALL", size=requested)
        assert len(rows) == max(1, min(25, requested))
    passed("requested_page_size_is_clamped_to_1_through_25")

    rows, has_more = page("ALL", before=1)
    assert rows == [] and not has_more
    passed("exclusive_cursor_after_oldest_record_returns_empty_page")

    rows, _ = page("LOW_RISK")
    assert [row["_id"] for row in rows] == sorted((row["_id"] for row in rows), reverse=True)
    passed("newest_record_id_order_is_independent_of_received_timestamp")

    before_count = count("ALL")
    before_harmful = count("HARMFUL")
    db.execute("UPDATE messages SET state='complete',label='scam',is_scam=1,is_unwanted=1 WHERE _id=?", (pending_id,))
    assert count("ALL") == before_count and count("HARMFUL") == before_harmful + 1
    assert pending_id not in {row[0] for row in db.execute(f"SELECT _id FROM messages WHERE {predicates['REVIEW']}")}
    passed("completion_reclassifies_same_record_without_duplication")

    assert "Math.max(1, Math.min(25, pageSize))" in store
    assert '"_id DESC", Integer.toString(boundedSize + 1)' in store
    assert 'where = "(" + where + ") AND _id<?"' in store
    assert 'db.beginTransactionNonExclusive()' in store
    passed("production_query_uses_bounded_limit_keyset_and_snapshot")

    report = {
        "scope": "Python host SQLite, synthetic in-memory records; not Android device/UI execution",
        "sqlite_version": sqlite3.sqlite_version,
        "passed": len(checks), "failed": 0, "checks": checks,
        "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (store_path, filter_path)},
        "sql_predicates_extracted_from_java": predicates,
        "fixtures": "57 older harmful +125 newer normal +uncertain/unfinished/legacy cases; no SMS/user files touched",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": len(checks), "failed": 0, "report": str(args.output)}))


if __name__ == "__main__":
    main()
