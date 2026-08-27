# rfqdiff

**Transparent supplier quotation comparison for structured procurement decisions.**

[![Tests](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml/badge.svg)](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`rfqdiff` compares supplier quotations across price, lead time and payment terms while keeping the scoring model explicit, deterministic and machine-readable.

Mixed-currency quotations should first be normalized with [`currency-normalizer`](https://github.com/yigitcan-ozturk/currency-normalizer). Technical compliance is deliberately kept outside this tool and is supplied by [`bidlint`](https://github.com/yigitcan-ozturk/bidlint) at the portfolio decision layer.

## Why rfqdiff

Supplier quotations are often compared in spreadsheets where assumptions, weights and recommendation logic become difficult to audit. `rfqdiff` keeps the commercial comparison small and inspectable: every score is produced from explicit inputs and explicit weights.

The goal is not to automate procurement judgment. The goal is to make a commercial comparison reproducible enough that a reviewer can understand how the recommendation was produced.

## Decision boundary

`rfqdiff` is responsible for **commercial quotation comparison**.

It does:

- compare price, lead time and payment terms;
- produce deterministic supplier scores;
- return machine-readable JSON for downstream decision systems;
- preserve upstream normalization metadata when present.

It intentionally does **not**:

- fetch or infer FX rates;
- determine technical compliance;
- score operational supplier risk;
- make contractual acceptance decisions;
- hide unsupported criteria inside an opaque composite score.

Those responsibilities remain separated across the engineering procurement toolchain.

## Install

Requirements: Python 3.11+.

```bash
git clone https://github.com/yigitcan-ozturk/rfqdiff.git
cd rfqdiff
python -m pip install .
```

The installed command is:

```bash
rfqdiff --help
```

The original `python main.py ...` source-checkout workflow remains supported for backward compatibility.

## Quick start

Compare quotations:

```bash
rfqdiff samples/supplier_a.json samples/supplier_b.json
```

Machine-readable output:

```bash
rfqdiff samples/supplier_a.json samples/supplier_b.json --json
```

Write the same integration payload to a file:

```bash
rfqdiff samples/supplier_a.json samples/supplier_b.json --output rfq.json
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

## Public Python API

```python
import rfqdiff

scored = rfqdiff.score_quotes([
    {"name": "A", "currency": "EUR", "price": 100, "lead_time_weeks": 4, "payment_days": 30},
    {"name": "B", "currency": "EUR", "price": 120, "lead_time_weeks": 5, "payment_days": 0},
])
```

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

All quotations must use the same currency. For mixed currencies, normalize them first with `currency-normalizer`, then pass the normalized files to `rfqdiff`.

## Scoring model

| Criterion | Weight | Better score |
| --- | ---: | --- |
| Price | 50% | Lower |
| Lead time | 30% | Lower |
| Payment terms | 20% | Longer |

The score is intentionally explicit so the recommendation can be reviewed rather than treated as a black box.

## Pipeline role

```text
currency-normalizer ──> rfqdiff ───────────────────────┐
                                                        │
payment-terms-parser ──────────────────────────────────┼──> supplier-scorecard
                                                        │
vendor-risk-engine ────────────────────────────────────┤
                                                        │
bidlint ──> technical compliance ──────────────────────┘
```

[`supplier-scorecard`](https://github.com/yigitcan-ozturk/supplier-scorecard) reads the supplier `score` from the `rfqdiff` JSON payload as its quotation score. Engineering compliance remains an independent input from `bidlint`, keeping commercial and technical decisions separately auditable.

## Quality gates

GitHub Actions validates:

- unit tests on Python 3.11, 3.12 and 3.13;
- wheel and source-distribution builds;
- package metadata with `twine check`;
- installation of the built wheel;
- the installed `rfqdiff` console command and public package namespace.

## Engineering principles

- **Explicit scoring** — weights and criteria remain visible.
- **Deterministic results** — identical supported inputs produce identical comparison results.
- **Separation of concerns** — FX, technical compliance and supplier risk stay outside quotation scoring.
- **Machine-readable handoff** — downstream tools consume a stable structured result instead of scraping presentation text.
- **Review before authority** — a recommendation supports procurement judgment; it does not replace approval.

## Engineering procurement toolchain

| Tool | Role |
| --- | --- |
| [`currency-normalizer`](https://github.com/yigitcan-ozturk/currency-normalizer) | Normalize quotation values across currencies |
| **[`rfqdiff`](https://github.com/yigitcan-ozturk/rfqdiff)** | Compare and score normalized quotations |
| [`payment-terms-parser`](https://github.com/yigitcan-ozturk/payment-terms-parser) | Convert payment terms into commercial-risk signals |
| [`vendor-risk-engine`](https://github.com/yigitcan-ozturk/vendor-risk-engine) | Score operational, quality, compliance and dependency risk |
| [`bidlint`](https://github.com/yigitcan-ozturk/bidlint) | Produce evidence-backed technical-compliance findings and scores |
| [`supplier-scorecard`](https://github.com/yigitcan-ozturk/supplier-scorecard) | Combine commercial, risk and technical signals into one supplier recommendation |

## Roadmap

- Excel/CSV quotation import
- Configurable commercial scoring weights
- Exportable comparison reports
- Richer quotation provenance
- Richer decision explanations

## Status

Early-stage project, currently at **v0.2**. The current line provides a stable JSON integration contract plus an installable Python package and console CLI.

## License

Released under the [MIT License](LICENSE).
