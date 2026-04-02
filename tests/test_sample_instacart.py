from __future__ import annotations

import csv
import json
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from sample_instacart import copy_lookup_files, filter_order_products, sample_orders, write_manifest


class SampleInstacartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd() / "tmp_test_artifacts" / f"sample_{uuid4().hex}"
        self.input_dir = self.root / "input"
        self.output_dir = self.root / "output"
        self.input_dir.mkdir(parents=True)
        self.output_dir.mkdir(parents=True)

        self.write_csv(
            self.input_dir / "orders.csv",
            ["order_id", "user_id", "eval_set", "order_number", "order_dow", "order_hour_of_day", "days_since_prior_order"],
            [
                ["1", "10", "prior", "1", "0", "8", ""],
                ["2", "11", "prior", "1", "1", "9", ""],
                ["3", "20", "train", "2", "2", "10", "7"],
            ],
        )
        self.write_csv(
            self.input_dir / "order_products__prior.csv",
            ["order_id", "product_id", "add_to_cart_order", "reordered"],
            [["1", "100", "1", "0"], ["2", "200", "1", "0"]],
        )
        self.write_csv(
            self.input_dir / "order_products__train.csv",
            ["order_id", "product_id", "add_to_cart_order", "reordered"],
            [["3", "300", "1", "1"], ["4", "400", "1", "0"]],
        )
        for name in ("products.csv", "aisles.csv", "departments.csv"):
            self.write_csv(self.input_dir / name, ["id", "name"], [["1", "x"]])

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def write_csv(self, path: Path, headers: list[str], rows: list[list[str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def test_sampling_and_filtering_are_deterministic(self) -> None:
        order_ids, sampled_rows = sample_orders(
            self.input_dir / "orders.csv",
            self.output_dir / "orders.csv",
            modulus=10,
            remainder=0,
        )
        prior_rows = filter_order_products(
            self.input_dir / "order_products__prior.csv",
            self.output_dir / "order_products__prior.csv",
            order_ids,
        )
        train_rows = filter_order_products(
            self.input_dir / "order_products__train.csv",
            self.output_dir / "order_products__train.csv",
            order_ids,
        )
        copy_lookup_files(self.input_dir, self.output_dir)
        write_manifest(
            self.output_dir,
            {
                "sampled_orders": sampled_rows,
                "sampled_prior_rows": prior_rows,
                "sampled_train_rows": train_rows,
            },
        )

        self.assertEqual(order_ids, {1, 3})
        self.assertEqual(sampled_rows, 2)
        self.assertEqual(prior_rows, 1)
        self.assertEqual(train_rows, 1)
        self.assertEqual(len(self.read_rows(self.output_dir / "orders.csv")), 2)
        self.assertEqual(len(self.read_rows(self.output_dir / "order_products__prior.csv")), 1)
        self.assertEqual(len(self.read_rows(self.output_dir / "order_products__train.csv")), 1)

        manifest = json.loads((self.output_dir / "sample_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["sampled_orders"], 2)


if __name__ == "__main__":
    unittest.main()
