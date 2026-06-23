"""Offline tests for csvdiff."""

from __future__ import annotations

from pathlib import Path

from csvdiff import diff_files, diff_rows

EX = Path(__file__).resolve().parent.parent / "examples"

OLD_H = ["id", "name", "price"]
OLD = [
    {"id": "1", "name": "A", "price": "10"},
    {"id": "2", "name": "B", "price": "20"},
    {"id": "3", "name": "C", "price": "30"},
]
NEW = [
    {"id": "1", "name": "A", "price": "10"},      # unchanged
    {"id": "2", "name": "B", "price": "25"},      # changed price
    {"id": "4", "name": "D", "price": "40"},      # added
]


def test_basic_classification():
    r = diff_rows(OLD_H, OLD, OLD_H, NEW, key=["id"])
    assert r.summary() == {"added": 1, "removed": 1, "changed": 1, "unchanged": 1}
    assert r.added[0]["id"] == "4"
    assert r.removed[0]["id"] == "3"
    assert r.changed[0].key == ("2",)
    assert r.changed[0].changes[0].column == "price"
    assert (r.changed[0].changes[0].old, r.changed[0].changes[0].new) == ("20", "25")


def test_has_differences_flag():
    same = diff_rows(OLD_H, OLD, OLD_H, OLD, key=["id"])
    assert not same.has_differences
    assert same.summary() == {"added": 0, "removed": 0, "changed": 0, "unchanged": 3}


def test_ignore_columns():
    new = [dict(r, price=str(int(r["price"]) + 1)) for r in OLD]  # all prices change
    full = diff_rows(OLD_H, OLD, OLD_H, new, key=["id"])
    assert len(full.changed) == 3
    ignored = diff_rows(OLD_H, OLD, OLD_H, new, key=["id"], ignore=["price"])
    assert len(ignored.changed) == 0 and ignored.unchanged == 3


def test_columns_subset():
    new = [dict(r) for r in OLD]
    new[0]["name"] = "Z"
    new[0]["price"] = "99"
    r = diff_rows(OLD_H, OLD, OLD_H, new, key=["id"], columns=["name"])
    assert r.compared_columns == ["name"]
    assert len(r.changed) == 1
    assert all(c.column == "name" for c in r.changed[0].changes)


def test_composite_key():
    h = ["region", "sku", "qty"]
    old = [{"region": "us", "sku": "x", "qty": "1"}, {"region": "eu", "sku": "x", "qty": "2"}]
    new = [{"region": "us", "sku": "x", "qty": "5"}, {"region": "eu", "sku": "x", "qty": "2"}]
    r = diff_rows(h, old, h, new, key=["region", "sku"])
    assert r.summary()["changed"] == 1
    assert r.changed[0].key == ("us", "x")


def test_missing_key_raises():
    try:
        diff_rows(OLD_H, OLD, OLD_H, NEW, key=["nope"])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_duplicate_keys_detected():
    dup = OLD + [{"id": "1", "name": "A2", "price": "11"}]
    r = diff_rows(OLD_H, dup, OLD_H, NEW, key=["id"])
    assert ("1",) in r.dup_keys_old


def test_diff_files_from_examples():
    r = diff_files(EX / "old.csv", EX / "new.csv", key=["id"])
    assert r.summary() == {"added": 1, "removed": 1, "changed": 2, "unchanged": 1}
    added_ids = {row["id"] for row in r.added}
    removed_ids = {row["id"] for row in r.removed}
    assert added_ids == {"5"} and removed_ids == {"4"}
    changed_keys = {c.key for c in r.changed}
    assert changed_keys == {("2",), ("3",)}
