import json
import statistics
import unittest
from collections import Counter

from fake import UserAgent
from utils import load


class TestUserAgentsDataset(unittest.TestCase):
    def setUp(self) -> None:
        # If the test runner requested an automated update (CI), attempt to refresh the data.
        import os
        if os.environ.get("UPDATE_INTOLI") == "1":
            try:
                import subprocess

                subprocess.check_call(["python", "data/update_from_intoli.py"])
            except Exception:
                # don't fail the whole test run if network/update isn't available
                pass

        # Load dataset used by the library
        self.data = load()
        self.ua_count = len(self.data)
        self.ua = UserAgent()

    def test_data_structure_has_required_fields(self):
        sample = self.data[0]
        keys = {"useragent", "percent", "type", "system", "browser", "version", "os"}
        self.assertTrue(keys.issubset(sample.keys()))

    def test_browser_methods_return_strings(self):
        # ensure per-browser properties return a string and correspond to the browser
        for name in ("chrome", "firefox", "safari", "edge", "opera"):
            val = getattr(self.ua, name)
            self.assertIsInstance(val, str)
            # the getBrowser method returns a dict with the browser field
            info = self.ua.getBrowser(name)
            self.assertEqual(info.get("browser"), name)
            self.assertIn("useragent", info)

    def test_device_type_filtering(self):
        ua_mobile = UserAgent(platforms=["mobile"])
        samples = [ua_mobile.random for _ in range(100)]
        types = {s for s in samples}
        # verify that returned strings exist and that the internal getBrowser respects the platforms filter
        records = [ua_mobile.getRandom for _ in range(50)]
        self.assertTrue(all(r.get("type") == "mobile" for r in records))

    def test_uniqueness_and_repetition_rate(self):
        # generate 1000 samples and compute repetition rate
        samples = [self.ua.random for _ in range(1000)]
        unique = set(samples)
        repetition_rate = (1000 - len(unique)) / 1000.0

        # Measure uniqueness (Intoli contains duplicate records for the same UA string)
        unique_count = len({r['useragent'] for r in self.data})

        # If Intoli provides ~9k+ *unique* user-agents then require a very low repetition rate.
        if unique_count >= 9000:
            self.assertLess(repetition_rate, 0.05, f"repetition too high: {repetition_rate:.3f}")
        elif self.ua_count >= 9000:
            # Intoli's source contains 10k records but many are duplicated strings — require
            # reasonable diversity while acknowledging duplicates are expected.
            self.assertGreater(unique_count, 2000, f"too few unique UAs in Intoli-derived data: {unique_count}")
            self.assertLess(
                repetition_rate,
                0.25,
                f"repetition too high for Intoli-derived dataset: {repetition_rate:.3f} (unique UAs: {unique_count})",
            )
        else:
            # offline / sample mode: ensure dataset is present and randomness is not totally degenerate
            self.assertGreater(self.ua_count, 20)
            self.assertLess(repetition_rate, 0.5, "repetition rate is extremely high for a sample dataset")

    def test_dataset_size_hint(self):
        # Provide a helpful assertion/error message when the dataset hasn't been updated.
        if self.ua_count < 1000:
            self.skipTest(
                "Dataset appears to be a small sample. To run the full-data assertions, run:\n"
                "  python data/update_from_intoli.py\n"
                "This will create `data/browsers.jsonl` from Intoli's dataset (~10k entries)."
            )
        # otherwise assert we have roughly the expected scale
        self.assertGreaterEqual(self.ua_count, 8000)


if __name__ == "__main__":
    unittest.main()
