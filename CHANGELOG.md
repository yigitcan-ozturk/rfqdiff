# Changelog

All notable changes to `rfqdiff` are documented here.

## [0.2.0] - 2026-08-29

The v0.2 line completes the original productization roadmap and release-hardening work for transparent, auditable commercial quotation comparison.

### Added

- Installable Python package and `rfqdiff` console CLI.
- Stable v0.2 machine-readable JSON integration payload.
- CSV quotation import with multiple suppliers per file.
- Excel (`.xlsx`) quotation import with multiple suppliers per worksheet.
- Strict configurable commercial scoring weights for price, lead time and payment terms.
- CSV and Excel comparison report export.
- Source provenance for file-loaded quotations, including filename, format, SHA-256 fingerprint, and tabular row/sheet location where applicable.
- Criterion-level score breakdowns for price, lead time and payment terms.
- Runner-up selection, score margin and deterministic decision explanations.
- Public Python helpers for quotation loading, weight validation and report export.
- Test coverage across Python 3.11, 3.12 and 3.13.
- Wheel/source-distribution build validation and installed-package smoke tests in CI.
- Sanitized industrial golden-pilot coverage for the complete quotation decision flow.
- Downstream compatibility verification with `supplier-scorecard` and the multi-tool Phase 2 procurement pilot.

### Changed

- Clarified `rfqdiff` as the commercial quotation-comparison component of the procurement toolchain.
- Kept mixed-currency normalization outside `rfqdiff` and delegated it to `currency-normalizer`.
- Kept technical compliance outside `rfqdiff` and delegated it to `bidlint`.
- Preserved upstream normalization metadata through scoring and downstream JSON output.
- Made report exports derive from the same scored payload used by the integration contract.

### Compatibility

- Existing JSON quotation inputs remain supported.
- The original `python main.py ...` workflow remains supported alongside the installed CLI.
- The default scoring model remains price 50%, lead time 30%, payment terms 20%.
- New v0.2 explanation and provenance fields are additive; the final supplier `score` remains the downstream quotation-score handoff.

## [0.1.0] - 2026-08-19

First public release.

### Added

- Compare multiple supplier quotations from JSON files.
- Score price, lead time and payment terms.
- Highlight lowest price and fastest lead time.
- Generate a simple supplier recommendation.
