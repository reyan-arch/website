"""Regression coverage for withdrawn case figures, using synthetic data only."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "work_detail_publication", REPO / "scripts/build_work_details.py"
)
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


def metric():
    return {
        "id": "holafly-synthetic",
        "public": True,
        "approved": True,
        "approval": True,
        "display": "1.23M",
        "label": "Synthetic example",
        "unit": "views",
        "period": "Example reporting window",
        "caveat": "Synthetic test fixture; not a client result.",
    }


def page():
    return {
        "id": "holafly",
        "published": True,
        "numericPublicationApproved": False,
        "numericCasePublicationApproved": False,
        "title": "A connected creator programme | IRG Media",
        "description": "Creator sourcing, refreshed briefs and repeat collaboration.",
        "h1": "A connected creator programme.",
        "primaryIntent": "Explain the working process.",
        "hero": {"title": "An ongoing programme.", "body": "Connect planning and delivery."},
        "image": {"alt": "A traveller checking a phone."},
        "sections": [{
            "id": "approach",
            "kind": "process",
            "title": "A connected working process.",
            "body": ["Carry creator context into the next brief."],
            "steps": [
                {"number": "01", "title": "Source", "body": "Match creators to the brief."},
                {"number": "02", "title": "Plan", "body": "Coordinate the delivery context."},
            ],
        }],
    }


class PublicationTests(unittest.TestCase):
    def test_metric_requires_each_literal_permission(self):
        self.assertIn("1.23M", builder.metric_card(metric()))
        for flag in ("public", "approved", "approval"):
            for value in (None, False, 1, "true", "existing-publication-record"):
                with self.subTest(flag=flag, value=value):
                    record = metric()
                    if value is None:
                        del record[flag]
                    else:
                        record[flag] = value
                    with self.assertRaises(ValueError):
                        builder.metric_card(record)

    def test_holafly_needs_both_page_permissions_even_for_approved_metric(self):
        candidate = page()
        candidate.update(numericPublicationApproved=True, numericCasePublicationApproved=True)
        candidate["sections"] = [{
            "id": "results", "kind": "overview", "title": "Results",
            "stats": [{"metricId": metric()["id"]}],
        }]
        records = {metric()["id"]: metric()}
        self.assertIn("1.23M", builder.render_section(candidate["sections"][0], candidate, records))
        for flag in ("numericPublicationApproved", "numericCasePublicationApproved"):
            for value in (None, False, 1, "true"):
                with self.subTest(flag=flag, value=value):
                    invalid = copy.deepcopy(candidate)
                    if value is None:
                        del invalid[flag]
                    else:
                        invalid[flag] = value
                    with self.assertRaises(ValueError):
                        builder.render_section(invalid["sections"][0], invalid, records)

    def test_withdrawn_record_cannot_return_through_snapshot_table_or_creator(self):
        record = metric()
        record.update(public=False, approved=False, approval=False)
        references = (
            {"id": "programme-snapshot", "kind": "overview", "stats": [{"metricId": record["id"]}]},
            {"id": "markets", "kind": "table", "columns": ["Context", "Views"],
             "rows": [{"label": "Example", "cells": [{"metricId": record["id"]}]}]},
            {"id": "creator-examples", "kind": "overview", "items": [
                {"title": "Example", "body": "Creative interpretation.", "metricId": record["id"]}
            ]},
        )
        for section in references:
            with self.subTest(section=section["id"]):
                candidate = page()
                candidate.update(numericPublicationApproved=True, numericCasePublicationApproved=True)
                candidate["sections"] = [dict(section, title="Working context")]
                with self.assertRaises(ValueError):
                    builder.render_section(candidate["sections"][0], candidate, {record["id"]: record})

    def test_stale_headline_metadata_and_copy_are_rejected_before_generation(self):
        paths = (
            ("title",), ("description",), ("h1",), ("primaryIntent",),
            ("hero", "title"), ("hero", "body"), ("image", "alt"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "content").mkdir()
            model_file = root / "content/site.json"
            for path in paths:
                for claim in ("Reached 1.23 million views.", "Reached three million views."):
                    with self.subTest(path=path, claim=claim):
                        candidate = page()
                        target = candidate
                        for key in path[:-1]:
                            target = target[key]
                        target[path[-1]] = claim
                        model_file.write_text(json.dumps({"pages": [candidate], "metrics": []}))
                        with mock.patch.object(builder, "ROOT", root), mock.patch.object(
                            builder.subprocess, "check_output"
                        ) as baseline_read:
                            with self.assertRaises(ValueError):
                                builder.main()
                            baseline_read.assert_not_called()
                        self.assertFalse((root / "site").exists())

    def test_qualitative_copy_and_process_counters_remain_publishable(self):
        candidate = page()
        record = metric()
        record.update(public=False, approved=False, approval=False)
        records = {record["id"]: record}
        builder.validate_public_page(candidate, records)
        rendered = builder.render_section(candidate["sections"][0], candidate, records)
        self.assertIn("Carry creator context into the next brief.", rendered)
        self.assertIn('aria-hidden="true">01</span>', rendered)
        self.assertIn('aria-hidden="true">02</span>', rendered)
        self.assertNotIn("data-metric-id", rendered)
        self.assertNotIn(record["display"], rendered)


if __name__ == "__main__":
    unittest.main()
