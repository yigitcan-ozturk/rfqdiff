# rfqdiff

A lightweight Python CLI for comparing supplier quotations and turning commercial terms into a structured procurement decision.

[![Tests](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml/badge.svg)](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml)

## Why rfqdiff

Supplier quotations often arrive with different prices, lead times and payment terms. `rfqdiff` provides a small, transparent decision-support layer for comparing those commercial signals consistently.

Mixed-currency quotations should first be normalized with `currency-normalizer`.

## Features

- Compare two or more supplier quotations
- Validate required quotation fields
- Score price, lead time and payment terms
- Recommend the highest-scoring supplier
- Preserve currency-normalization metadata
- Return a stable structured JSON result
- Write machine-readable comparison output for `supplier-scorecard`
- Run with Python only — no third-party runtime dependencies

## Quick start

### Requirements

- Python 3.11+

### Compare quotations

```bash
python main.py samples/supplier_a.json samples/supplier_b.json
```

### Machine-readable output

```bash
python main.py \
  samples/supplier_a.json \
  samples/supplier_b.json \
  --json
```

Write the same integration payload to a file:

```bash
python main.py \
  samples/supplier_a.json \
  samples/supplier_b.json \
  --output rfq.json
```

The JSON contract contains:

```json
{
  "tool": "rfqdiff",
  "version": "0.2",
  "currency": "EUR",
  "recommended_supplier": "Supplier A",
  "suppliers": [
    {
      "name": "Supplier A",
      "score": 97.1
    }
  ]
}
```

The full supplier objects also include price, lead time, payment terms and any upstream normalization metadata.

## Quotation format

```json
{
  "name": "Supplier A",
  "currency": "EUR",
  "price": 84200,
  "lead_time_weeks": 8,
  "payment_days": 30
}
```

All quotations must use the same currency. For mixed currencies:

```bash
python ../currency-normalizer/main.py \
  --quote supplier_usd.json \
  --target-currency EUR \
  --output supplier_eur.json
```

Then pass the normalized file to `rfqdiff`.

## Scoring model

| Criterion | Weight | Better score |
| --- | ---: | --- |
| Price | 50% | Lower |
| Lead time | 30% | Lower |
| Payment terms | 20% | Longer |

The score is intentionally explicit so the recommendation can be reviewed rather than treated as a black box.

## Pipeline role

```text
currency-normalizer ──> rfqdiff ───────────────┐
                                               │
payment-terms-parser ──────────────────────────┼─> supplier-scorecard
                                               │
vendor-risk-engine ────────────────────────────┘
```

`supplier-scorecard` reads the supplier `score` from the `rfqdiff` JSON payload as its quotation score.

## Tests

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same suite automatically on supported Python versions.

## Procurement tooling suite

| Tool | Role |
| --- | --- |
| [`currency-normalizer`](https://github.com/yigitcan-ozturk/currency-normalizer) | Normalize quotation values across currencies |
| **[`rfqdiff`](https://github.com/yigitcan-ozturk/rfqdiff)** | Compare and score normalized quotations |
| [`payment-terms-parser`](https://github.com/yigitcan-ozturk/payment-terms-parser) | Convert payment terms into commercial-risk signals |
| [`vendor-risk-engine`](https://github.com/yigitcan-ozturk/vendor-risk-engine) | Score operational, quality, compliance and dependency risk |
| [`supplier-scorecard`](https://github.com/yigitcan-ozturk/supplier-scorecard) | Combine upstream signals into one supplier recommendation |

## Roadmap

- Excel/CSV import
- Technical compliance comparison
- Configurable scoring weights
- Exportable comparison reports
- Richer decision explanations

## Status

Early-stage project, currently at **v0.2**. This version adds a stable JSON integration contract and direct machine-readable output for the composite supplier-scorecard pipeline.

## License

Released under the [MIT License](LICENSE).
