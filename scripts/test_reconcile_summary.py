import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("reconcile", Path(__file__).with_name("reconcile-summary.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReconcileTests(unittest.TestCase):
    def fixture(self, root, status="up"):
        (root / "history").mkdir()
        (root / "history/leaf-kosync.yml").write_text("status: " + status + "\ncode: 200\n")
        (root / "history/summary.json").write_text(json.dumps([
            {"slug": "leaf-kosync", "url": "https://example.com", "status": "down", "uptime": "98%"}
        ]))
        (root / "README.md").write_text("Intro\n| [Leaf](https://example.com) | 🟥 Down | 98% |\n")

    def test_recovery_degradation_and_idempotence(self):
        for status, label in module.LABELS.items():
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, status)
                module.reconcile(root)
                summary = json.loads((root / "history/summary.json").read_text())
                self.assertEqual(summary[0]["status"], status)
                self.assertEqual(summary[0]["uptime"], "98%")
                self.assertIn(label, (root / "README.md").read_text())
                first = (root / "history/summary.json").read_bytes()
                module.reconcile(root)
                self.assertEqual(first, (root / "history/summary.json").read_bytes())

    def test_invalid_or_missing_state_does_not_publish(self):
        for status in ["unknown", "up\nstatus: down"]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, status)
                before = (root / "history/summary.json").read_bytes()
                with self.assertRaises(ValueError):
                    module.reconcile(root)
                self.assertEqual(before, (root / "history/summary.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
