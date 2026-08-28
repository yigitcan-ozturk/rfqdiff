# rfqdiff

**Transparent supplier quotation comparison for structured procurement decisions.**

[![Tests](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml/badge.svg)](https://github.com/yigitcan-ozturk/rfqdiff/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`rfqdiff` compares supplier quotations across price, lead time and payment terms while keeping the scoring model explicit, deterministic and machine-readable.

Mixed-currency quotations should first be normalized with [`currency-normalizer`](https://github.com/yigitcan-ozturk/currency-normalizer). Technical compliance is deliberately kept outside this tool and is supplied by [`bidlint`](https://github.com/yigitcan-ozturk/bidlint) at the portfolio decision layer.

## Why rfqdiff

Supplier quotations are often compared in spreadsheets where assumptions, weights and recommendation logic become difficult to audit. `rfqdiff` keeps the commercial comparison small and inspectable: every score is produced from explicit inputs and explicit weights.

The goal is not to automate procurement judgment. The goal is to make a commercial comparison reproducible enough that a reviewer can understand how the recommendation was produced and trace each loaded quotation back to its input file.

## Decision boundary

`rfqdiff` is responsible for **commercial quotation comparison**.

It does:

- compare price, lead time and payment terms;
- import quotations from JSON, CSV and Excel (`.xlsx`);
- use explicit default or user-supplied commercial scoring weights;
- produce deterministic supplier scores;
- return machine-readable JSON for downstream decision systems;
- export ranked comparison reports as CSV or Excel;
- attach source-file provenance to loaded quotations;
- preserve upstream normalization metadata when present in JSON inputs.

It intentionally does **not**:

- fetch or infer FX rates;
- determine technical compliance;
- score operational supplier risk;
- make contractual acceptance decisions;
- accept hidden or unsupported scoring criteria;
- treat file hashes as digital signatures or proof of authenticity.

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

Compare separate JSON quotations:

```bash
rfqdiff samples/supplier_a.json samples/supplier_b.json
```

Compare multiple suppliers from one CSV file:

```bash
rfqdiff samples/quotations.csv
```

Excel workbooks use the same columns and can be passed directly:

```bash
rfqdiff quotations.xlsx
```

Machine-readable output:

```bash
rfqdiff samples/quotations.csv --json
```

Write the same integration payload to a file:

```bash
rfqdiff samples/quotations.csv --output rfq.json
```

Export a ranked comparison report:

```bash
rfqdiff samples/quotations.csv --report comparison.csv
rfqdiff samples/quotations.csv --report comparison.xlsx
```

JSON, CSV and XLSX inputs can also be combined in one command as long as every quotation uses the same currency.

## Configurable scoring weights

The default commercial model is:

| Criterion | Weight | Better score |
| --- | ---: | --- |
| Price | 50% | Lower |
| Lead time | 30% | Lower |
| Payment terms | 20% | Longer |

For a different procurement strategy, pass a JSON weights profile with `--weights`:

```json
{
  "price": 0.40,
  "lead_time": 0.40,
  "payment_terms": 0.20
}
```

```bash
rfqdiff samples/quotations.csv --weights samples/weights-balanced.json
```

Weight profiles are deliberately strict:

- all three supported criteria must be present;
- no additional criteria are accepted;
- each value must be between `0` and `1`;
- values must sum to exactly `1.0` within floating-point tolerance.

The effective profile is returned in the output payload under `weights`, keeping each recommendation auditable.

## Quotation provenance

Every quotation loaded from a file receives an `rfqdiff_source` object. It records the input artifact used for that specific supplier row without storing the caller's full local path.

A JSON quotation receives:

```json
"rfqdiff_source": {
  "file": "supplier_a.json",
  "format": "json",
  "sha256": "..."
}
```

CSV quotations additionally record the source row. Excel quotations record both the source row and active worksheet:

```json
"rfqdiff_source": {
  "file": "quotations.xlsx",
  "format": "xlsx",
  "sha256": "...",
  "row": 2,
  "sheet": "Commercial Quotes"
}
```

The SHA-256 value is an integrity and traceability fingerprint for the input file. It helps reviewers verify that two results came from the same source bytes; it is **not** a digital signature and does not establish who created or approved the quotation.

`rfqdiff_source` is reserved by the tool and cannot be supplied in input data. This prevents imported quotations from spoofing provenance generated by `rfqdiff` itself.

The provenance object stays with each supplier through scoring and JSON output. CSV/XLSX comparison exports also include source file, format, hash, row and sheet columns where applicable.

## Comparison report exports

`--report` produces reviewer-friendly exports without replacing the machine-readable JSON contract.

CSV reports contain one ranked supplier per row with:

- rank;
- recommended flag;
- supplier name;
- currency and price;
- lead time;
- payment terms;
- final score;
- source provenance fields.

Excel reports contain two worksheets:

- `Comparison` — the ranked supplier table plus source provenance;
- `Summary` — recommended supplier, lowest price, fastest lead time, best payment terms and the effective scoring weights.

The report uses the same scored payload as the JSON output, so the human-facing export and downstream integration result remain aligned.

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
      "score": 97.1,
      "rfqdiff_source": {
        "file": "quotations.csv",
        "format": "csv",
        "sha256": "...",
        "row": 2
      }
    }
  ],
  "weights": {
    "price": 0.5,
    "lead_time": 0.3,
    "payment_terms": 0.2
  }
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

Custom weights can be supplied through the public API:

```python
weights = {"price": 0.4, "lead_time": 0.4, "payment_terms": 0.2}
scored = rfqdiff.score_quotes(quotes, weights)
```

Tabular files and weight profiles can be loaded through the public API as well:

```python
from pathlib import Path
import rfqdiff

quotes = rfqdiff.load_quotes(Path("quotations.xlsx"))
weights = rfqdiff.load_weights(Path("weights.json"))
```

Comparison reports can be exported from a built result:

```python
payload = rfqdiff.build_result(scored, "EUR", weights)
rfqdiff.write_report(payload, Path("comparison.xlsx"))
```

## Quotation format

A JSON quotation contains one supplier:

```json
{
  "name": "Supplier A",
  "currency": "EUR",
  "price": 84200,
  "lead_time_weeks": 8,
  "payment_days": 30
}
```

CSV and Excel files use one supplier per row with these required columns:

| Column | Meaning |
| --- | --- |
| `name` | Supplier name |
| `currency` | ISO-style currency code used by the quotation |
| `price` | Commercial quotation value |
| `lead_time_weeks` | Lead time in weeks |
| `payment_days` | Payment term length in days |

Example CSV:

```csv
name,currency,price,lead_time_weeks,payment_days
Supplier A,EUR,84200,8,30
Supplier B,EUR,79400,14,0
```

All quotations must use the same currency. For mixed currencies, normalize them first with `currency-normalizer`, then pass the normalized values to `rfqdiff`.

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
- JSON, CSV and Excel quotation loading;
- source-file provenance, row/sheet traceability and SHA-256 fingerprints;
- rejection of caller-supplied reserved provenance fields;
- default and configurable scoring profiles;
- rejection of incomplete or unsupported weight profiles;
- CSV and Excel comparison report exports;
- wheel and source-distribution builds;
- package metadata with `twine check`;
- installation of the built wheel and runtime dependencies;
- the installed `rfqdiff` console command and public package namespace.

## Engineering principles

- **Explicit scoring** — weights and criteria remain visible.
- **Deterministic results** — identical supported inputs produce identical comparison results.
- **Traceable inputs** — loaded quotations retain source artifact fingerprints and tabular locations.
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

- Richer decision explanations

## Status

Early-stage project, currently at **v0.2**. The current line provides a stable JSON integration contract, an installable Python package and console CLI, JSON/CSV/XLSX quotation ingestion, auditable configurable commercial scoring weights, CSV/XLSX comparison report export, and source-level quotation provenance.

## License

Released under the [MIT License](LICENSE).
