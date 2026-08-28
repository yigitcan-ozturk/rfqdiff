# rfqdiff v0.2.0 release checklist

Current package metadata: `0.2.0`  
Current machine-readable contract: `0.2`  
Latest published GitHub Release before this checklist: `v0.1.0`

## Preconditions completed

- [x] JSON/CSV/XLSX quotation ingestion
- [x] Configurable commercial scoring weights
- [x] CSV/XLSX comparison report export
- [x] Source provenance with SHA-256 and row/sheet traceability
- [x] Deterministic score breakdowns and decision explanations
- [x] Python 3.11, 3.12 and 3.13 unit-test matrix
- [x] Wheel and source-distribution build validation
- [x] Installed-wheel CLI smoke test outside repository checkout
- [x] End-to-end CSV → JSON + XLSX report smoke test
- [x] `CHANGELOG.md` prepared for v0.2.0

## Publication steps

- [ ] Change `CHANGELOG.md` heading from `[0.2.0] - Unreleased` to the actual release date.
- [ ] Create Git tag `v0.2.0` at the release-ready `main` commit.
- [ ] Publish GitHub Release `rfqdiff v0.2.0` from that tag.
- [ ] Use the v0.2.0 changelog section as the release notes baseline.
- [ ] Verify the release page points to the intended commit and source archives.
- [ ] Re-run/confirm the `main` GitHub Actions workflow is green at the tagged commit.
- [ ] Run a clean install check from the release artifact and execute `rfqdiff --help`.
- [ ] Run one representative comparison and verify recommendation, score breakdown, provenance and report export.

## Release boundary

v0.2.0 is the commercial quotation-comparison release. FX normalization remains in `currency-normalizer`, technical compliance remains in `bidlint`, and broader supplier risk remains outside `rfqdiff`.

No new scoring criteria should be added as part of the release publication step.
