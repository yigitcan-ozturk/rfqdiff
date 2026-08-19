# rfqdiff

A lightweight Python CLI for comparing supplier quotations and turning commercial terms into a structured procurement decision.

[![Tests](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml/badge.svg)](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml)

## Why rfqdiff

Supplier quotations often arrive in different formats and procurement teams spend time manually comparing price, lead time and payment terms. `rfqdiff` provides a small, transparent decision-support layer for that comparison.

The goal is not to replace procurement judgment. It is to make the commercial comparison consistent, explainable and repeatable.

## Features

- Compare two or more supplier quotations
- Validate required quotation fields
- Score price, lead time and payment terms
- Highlight the cheapest and fastest supplier
- Highlight the supplier with the best payment terms
- Recommend the highest-scoring supplier
- Reject mixed currencies until normalization is applied
- Run with Python only — no third-party runtime dependencies

## Quick start

### Requirements

- Python 3.11+

### Run the included sample

```bash
python main.py samples/supplier_a.json samples/supplier_b.json
```

Example output:

```text
RFQDIFF v0.1
======================================================================================
Supplier                             Price     Lead time       Payment       Score
--------------------------------------------------------------------------------------
Supplier A                   EUR 84,200.00       8 weeks       30 days    97.1/100
Supplier B                   EUR 79,400.00      14 weeks        0 days    67.1/100

Decision summary
--------------------------------------------------------------------------------------
Recommended supplier : Supplier A (97.1/100)
Lowest price         : Supplier B (EUR 79,400.00)
Fastest lead time    : Supplier A (8 weeks)
Best payment terms   : Supplier A (30 days)
```

## Quotation format

Each supplier quotation is a JSON file:

```json
{
  "name": "Supplier A",
  "currency": "EUR",
  "price": 84200,
  "lead_time_weeks": 8,
  "payment_days": 30
}
```

Required fields:

| Field | Meaning |
| --- | --- |
| `name` | Supplier name |
| `currency` | Quotation currency |
| `price` | Total quotation value |
| `lead_time_weeks` | Delivery lead time in weeks |
| `payment_days` | Payment term in days |

## Scoring model

Current default weights:

| Criterion | Weight | Better score |
| --- | ---: | --- |
| Price | 50% | Lower |
| Lead time | 30% | Lower |
| Payment terms | 20% | Longer |

The score is intentionally simple and visible in the code so the recommendation can be reviewed rather than treated as a black box.

## Tests

Run the test suite locally with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same test suite automatically on supported Python versions.

## Related tools

`rfqdiff` is the comparison layer in a small procurement-tooling set:

- [`payment-terms-parser`](https://github.com/yigitcan-ozturk/payment-terms-parser) — parse and standardize supplier payment terms
- [`currency-normalizer`](https://github.com/yigitcan-ozturk/currency-normalizer) — normalize multi-currency supplier quotations

## Roadmap

- Integrate currency normalization
- Excel/CSV import
- PDF quotation extraction
- Technical compliance comparison
- Configurable scoring weights
- Exportable comparison reports

## Status

Early-stage project, currently at **v0.1**. The core comparison and scoring workflow is functional; the next iterations will focus on input normalization and richer procurement analysis.

## License

Released under the [MIT License](LICENSE).
