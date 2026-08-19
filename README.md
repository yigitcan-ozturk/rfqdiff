# rfqdiff

`rfqdiff` is a lightweight command-line tool for comparing supplier quotations.

It reads quotation data from JSON files, scores suppliers using price, lead time and payment terms, and prints a simple procurement decision summary.

## Why this exists

Supplier quotations often arrive in different formats and procurement teams spend time manually comparing commercial terms. `rfqdiff` is the first building block toward a faster, structured quotation comparison workflow.

## v0.1 features

- Compare 2 or more supplier quotations
- Validate required quotation fields
- Compare price, lead time and payment terms
- Produce a weighted supplier score
- Highlight the cheapest, fastest and best-payment-term supplier
- Recommend the highest-scoring supplier
- Reject mixed currencies until currency normalization is added

## Scoring

Current default weights:

- Price: 50%
- Lead time: 30%
- Payment terms: 20%

Lower price and lead time score higher. Longer payment terms score higher.

## Requirements

- Python 3.13+
- No third-party Python packages required

## Run the sample

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

## Roadmap

- Currency normalization
- Excel/CSV import
- PDF quotation extraction
- Technical compliance comparison
- Configurable scoring weights
- Exportable comparison report

## Status

Project 01 / 45 — YÖ90 Builder Track.
