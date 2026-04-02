from __future__ import annotations

import csv
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from split_stream_replay_batches import split_csv


class SplitStreamReplayBatchesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd() / "tmp_test_artifacts" / f"split_{uuid4().hex}"
        self.root.mkdir(parents=True)
        self.input_file = self.root / "input.csv"
        self.output_dir = self.root / "batches"
        with self.input_file.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["order_id", "user_id"])
            for order_id in range(1, 6):
                writer.writerow([order_id, 100 + order_id])

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def count_rows(self, path: Path) -> int:
        with path.open("r", newline="", encoding="utf-8") as handle:
            return sum(1 for _ in csv.DictReader(handle))

    def test_split_csv_preserves_all_rows(self) -> None:
        counts = split_csv(self.input_file, self.output_dir, batches=2)
        total_rows = sum(counts.values())
        self.assertEqual(total_rows, 5)
        self.assertTrue((self.output_dir / "replay_batch_01.csv").exists())
        self.assertTrue((self.output_dir / "replay_batch_02.csv").exists())
        self.assertEqual(
            self.count_rows(self.output_dir / "replay_batch_01.csv")
            + self.count_rows(self.output_dir / "replay_batch_02.csv"),
            5,
        )


if __name__ == "__main__":
    unittest.main()
