import os
import json
import csv
import time
from typing import Dict, Any, List


class MetricsCollector:

    def __init__(self, output_dir: str = "metrics_output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.records: List[Dict[str, Any]] = []

    def record_metric(
        self,
        test_name: str,
        operation_name: str,
        duration_seconds: float,
        extra_details: str = ""
    ):
        record = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_name": test_name,
            "operation": operation_name,
            "duration_sec": round(duration_seconds, 4),
            "details": extra_details
        }
        self.records.append(record)

    def save_to_json(self, filename: str = "metrics.json") -> str:
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=4, ensure_ascii=False)
        return path

    def save_to_csv(self, filename: str = "metrics.csv") -> str:
        path = os.path.join(self.output_dir, filename)
        fieldnames = ["timestamp", "test_name", "operation", "duration_sec", "details"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.records)
        return path