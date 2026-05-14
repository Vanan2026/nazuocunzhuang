import tempfile
import unittest
from pathlib import Path

from scan_text_encoding import classify_bytes, find_mojibake_markers
from scan_text_encoding import should_scan


class EncodingScanTests(unittest.TestCase):
    def test_utf8_text_is_clean(self):
        result = classify_bytes(Path("clean.md"), "村庄".encode("utf-8"))

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["encoding"], "utf-8")
        self.assertFalse(result["needs_fix"])

    def test_gb18030_text_is_reported_for_conversion(self):
        result = classify_bytes(Path("legacy.txt"), "庭院".encode("gb18030"))

        self.assertEqual(result["status"], "non_utf8")
        self.assertEqual(result["encoding"], "gb18030")
        self.assertTrue(result["needs_fix"])

    def test_invalid_utf8_without_good_legacy_decode_is_suspect(self):
        result = classify_bytes(Path("bad.txt"), b"\xff\xfe\xfa\x00text")

        self.assertIn(result["status"], {"binary", "undecodable"})
        self.assertTrue(result["needs_fix"])

    def test_common_mojibake_markers_are_detected(self):
        markers = find_mojibake_markers("当前任务: 鎺ュ叆 Godot")

        self.assertIn("鎺", markers)

    def test_scanner_artifacts_are_not_scanned_by_default(self):
        root = Path(".")

        self.assertFalse(should_scan(Path("tools/scan_text_encoding.py"), root, False, {".py"}))
        self.assertFalse(should_scan(Path("tools/test_scan_text_encoding.py"), root, False, {".py"}))


if __name__ == "__main__":
    unittest.main()
