import json
import tempfile
import unittest
from pathlib import Path

import main as rfqdiff


class LoadQuoteTests(unittest.TestCase):
    def test_load_quote_accepts_valid_input(self) -> None:
        quote = {
            "name": "Supplier A",
            "currency": "EUR",
            "price": 100,
            "lead_time_weeks": 4,
            "payment_days": 30,
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quote.json"
            path.write_text(json.dumps(quote), encoding="utf-8")
            self.assertEqual(rfqdiff.load_quote(path), quote)

    def test_load_quote_accepts_currency_normalizer_metadata(self) -> None:
        quote = {
            "name": "Supplier A",
            "currency": "EUR",
            "price": 100,
            "lead_time_weeks": 4,
            "payment_days": 30,
            "normalization": {
                "tool": "currency-normalizer",
                "original_currency": "USD",
            },
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quote.json"
            path.write_text(json.dumps(quote), encoding="utf-8")
            loaded = rfqdiff.load_quote(path)

        self.assertEqual(loaded["normalization"]["tool"], "currency-normalizer")

    def test_load_quote_rejects_missing_required_field(self) -> None:
        quote = {
            "name": "Supplier A",
            "currency": "EUR",
            "price": 100,
            "lead_time_weeks": 4,
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quote.json"
            path.write_text(json.dumps(quote), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "payment_days"):
                rfqdiff.load_quote(path)


class CurrencyValidationTests(unittest.TestCase):
    def test_validate_currencies_accepts_single_currency(self) -> None:
        quotes = [
            {"currency": "eur"},
            {"currency": "EUR"},
        ]
        self.assertEqual(rfqdiff.validate_currencies(quotes), "EUR")

    def test_validate_currencies_rejects_mixed_currencies(self) -> None:
        quotes = [
            {"currency": "EUR"},
            {"currency": "USD"},
        ]
        with self.assertRaisesRegex(ValueError, "currency-normalizer"):
            rfqdiff.validate_currencies(quotes)


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quotes = [
            {
                "name": "Supplier A",
                "currency": "EUR",
                "price": 84200,
                "lead_time_weeks": 8,
                "payment_days": 30,
            },
            {
                "name": "Supplier B",
                "currency": "EUR",
                "price": 79400,
                "lead_time_weeks": 14,
                "payment_days": 0,
            },
        ]

    def test_score_quotes_ranks_expected_supplier_first(self) -> None:
        scored = rfqdiff.score_quotes(self.quotes)

        self.assertEqual(scored[0]["name"], "Supplier A")
        self.assertEqual(scored[0]["score"], 97.1)
        self.assertEqual(scored[1]["name"], "Supplier B")

    def test_score_quotes_handles_zero_payment_days_for_all_suppliers(self) -> None:
        quotes = [
            {
                "name": "Supplier A",
                "currency": "EUR",
                "price": 100,
                "lead_time_weeks": 4,
                "payment_days": 0,
            },
            {
                "name": "Supplier B",
                "currency": "EUR",
                "price": 120,
                "lead_time_weeks": 5,
                "payment_days": 0,
            },
        ]

        scored = rfqdiff.score_quotes(quotes)
        self.assertEqual(scored[0]["name"], "Supplier A")
        self.assertEqual(scored[0]["score"], 100.0)

    def test_build_result_is_pipeline_ready(self) -> None:
        scored = rfqdiff.score_quotes(self.quotes)
        payload = rfqdiff.build_result(scored, "EUR")

        self.assertEqual(payload["tool"], "rfqdiff")
        self.assertEqual(payload["version"], "0.2")
        self.assertEqual(payload["recommended_supplier"], "Supplier A")
        self.assertEqual(payload["suppliers"][0]["score"], 97.1)
        json.dumps(payload)

    def test_write_json_round_trip(self) -> None:
        scored = rfqdiff.score_quotes(self.quotes)
        payload = rfqdiff.build_result(scored, "EUR")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rfq.json"
            rfqdiff.write_json(payload, path)
            reloaded = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(reloaded["tool"], "rfqdiff")
        self.assertEqual(reloaded["suppliers"][0]["name"], "Supplier A")


if __name__ == "__main__":
    unittest.main()
