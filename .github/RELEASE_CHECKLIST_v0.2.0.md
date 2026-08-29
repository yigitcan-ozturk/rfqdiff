# rfqdiff v0.2.0 release checklist — completed

Release status: **COMPLETED**  
Release date: **2026-08-29**  
Package metadata: `0.2.0`  
Machine-readable contract: `0.2`  
Git tag: `v0.2.0`  
Tagged release commit: `63b074284954a9ae04b80e3b290e4f6427df690d`  
GitHub Release: `rfqdiff v0.2.0`

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
- [x] Sanitized industrial golden RFQ pilot
- [x] `supplier-scorecard` RFQdiff v0.2 consumer-contract verification
- [x] Multi-tool Phase 2 procurement pilot verification
- [x] `CHANGELOG.md` finalized for v0.2.0

## Publication completed

- [x] Changed `CHANGELOG.md` heading to `[0.2.0] - 2026-08-29`.
- [x] Created annotated Git tag `v0.2.0` at release commit `63b074284954a9ae04b80e3b290e4f6427df690d`.
- [x] Published GitHub Release `rfqdiff v0.2.0` from that tag.
- [x] Used the v0.2.0 changelog section as the release-notes baseline.
- [x] Verified the release page, source archives and downloadable distribution assets.
- [x] Confirmed the normal `main` test workflow is green at the tagged release commit (`33271631667`).
- [x] Downloaded the published wheel from the GitHub Release and verified its SHA-256 digest.
- [x] Clean-installed the published wheel into a fresh Python 3.11 virtual environment and executed `rfqdiff --help`.
- [x] Ran a representative released comparison and verified recommendation, runner-up, score margin, score breakdown and provenance.
- [x] Generated and validated an XLSX comparison report using the published wheel.
- [x] Stored post-release evidence in GitHub Actions artifact `rfqdiff-v0.2.0-release-verification` from run `33271772371`.

## Published artifacts

- `rfqdiff-0.2.0-py3-none-any.whl`  
  SHA-256: `858a0c7a7b0caf69f4b1f22843363edd8d14cad4553564539abcbc33ec878fa5`
- `rfqdiff-0.2.0.tar.gz`  
  SHA-256: `8a716802ed14312c5cd785161b08760d9f1a54a4569101673f2b58cdc3ce9e17`

## Post-release verification

Post-release verification workflow run `33271772371` completed successfully against the actual published wheel. The verifier downloaded the GitHub Release asset, checked its digest, installed it cleanly, ran a representative commercial comparison, validated the JSON v0.2 contract and generated an XLSX report. The ordinary `main` test workflow on the post-release verification commit (`33271772506`) also completed successfully.

The temporary release-publisher and post-release-verifier workflows were intentionally removed after successful execution so the repository does not retain one-off publication machinery.

## Release boundary

v0.2.0 is the commercial quotation-comparison release. FX normalization remains in `currency-normalizer`, technical compliance remains in `bidlint`, and broader supplier risk remains outside `rfqdiff`.

No new scoring criteria were added as part of release publication or verification.
