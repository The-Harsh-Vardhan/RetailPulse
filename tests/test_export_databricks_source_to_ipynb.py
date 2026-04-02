from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from export_databricks_source_to_ipynb import export_notebooks


class ExportDatabricksSourceNotebookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd() / "tmp_test_artifacts" / f"ipynb_{uuid4().hex}"
        self.source_dir = self.root / "notebooks"
        self.output_dir = self.root / "notebooks_ipynb"
        self.source_dir.mkdir(parents=True)

        self.source_path = self.source_dir / "sample.py"
        self.source_path.write_text(
            "\n".join(
                [
                    "# Databricks notebook source",
                    "# MAGIC %md",
                    "# MAGIC # Sample Notebook",
                    "# MAGIC",
                    "# MAGIC This is markdown.",
                    "# COMMAND ----------",
                    "value = 2 + 2",
                    "print(value)",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def test_export_creates_expected_cells(self) -> None:
        result = export_notebooks(self.source_dir, self.output_dir, check=False)
        self.assertEqual(result, 0)

        output_path = self.output_dir / "sample.ipynb"
        payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["nbformat"], 4)
        self.assertEqual(len(payload["cells"]), 2)
        self.assertEqual(payload["cells"][0]["cell_type"], "markdown")
        self.assertIn("# Sample Notebook\n", payload["cells"][0]["source"])
        self.assertEqual(payload["cells"][1]["cell_type"], "code")
        self.assertEqual(payload["cells"][1]["source"], ["value = 2 + 2\n", "print(value)\n"])

    def test_export_is_deterministic_and_check_detects_drift(self) -> None:
        first_result = export_notebooks(self.source_dir, self.output_dir, check=False)
        second_result = export_notebooks(self.source_dir, self.output_dir, check=False)
        self.assertEqual(first_result, 0)
        self.assertEqual(second_result, 0)

        rendered_once = (self.output_dir / "sample.ipynb").read_text(encoding="utf-8")
        rendered_twice = (self.output_dir / "sample.ipynb").read_text(encoding="utf-8")
        self.assertEqual(rendered_once, rendered_twice)

        self.source_path.write_text(
            self.source_path.read_text(encoding="utf-8") + "# COMMAND ----------\nprint('extra')\n",
            encoding="utf-8",
        )
        self.assertEqual(export_notebooks(self.source_dir, self.output_dir, check=True), 1)


if __name__ == "__main__":
    unittest.main()
