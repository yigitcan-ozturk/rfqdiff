import unittest

import rfqdiff


class PackageTests(unittest.TestCase):
    def test_public_version(self):
        self.assertEqual(rfqdiff.__version__, "0.2.0")
        self.assertEqual(rfqdiff.VERSION, "0.2")

    def test_public_scoring_api(self):
        quotes = [
            {"name": "A", "currency": "EUR", "price": 100, "lead_time_weeks": 4, "payment_days": 30},
            {"name": "B", "currency": "EUR", "price": 120, "lead_time_weeks": 5, "payment_days": 0},
        ]
        scored = rfqdiff.score_quotes(quotes)
        self.assertEqual(scored[0]["name"], "A")


if __name__ == "__main__":
    unittest.main()
