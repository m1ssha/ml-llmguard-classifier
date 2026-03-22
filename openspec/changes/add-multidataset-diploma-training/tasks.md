## 1. Multi-dataset ingestion foundation

- [x] 1.1 Add configurable source registry for multiple HF datasets (including Anthropic/hh-rlhf)
- [x] 1.2 Implement chosen/rejected mapping adapter to canonical text records with origin flags
- [x] 1.3 Extend loader metadata to persist dataset_id, revision/version, and mapping strategy per source

## 2. Canonical schema and data quality hardening

- [ ] 2.1 Extend canonical sample schema with dataset_id and split_role for source tracing
- [ ] 2.2 Add source-aware validation rules for mandatory fields in mixed-source mode
- [ ] 2.3 Add anti-leakage dedup checks across train/validation/test with split repair logging
- [ ] 2.4 Add source-wise shortcut concentration checks and quality gate thresholds

## 3. Training pipeline for single vs mixed modes

- [ ] 3.1 Add dataset-mix config (sources, quotas/weights, weak-labeling policy, seed)
- [ ] 3.2 Implement deterministic corpus builder from dataset-mix config
- [ ] 3.3 Update baseline training pipeline to accept mixed-source canonical corpus
- [ ] 3.4 Update encoder/stronger encoder pipeline to run with the same mixed-source contract

## 4. Diploma evaluation protocol (A/B/C)

- [ ] 4.1 Implement Level A run: prompt-injection single-source baseline
- [ ] 4.2 Implement Level B run: mixed-source training (prompt injection + hh-rlhf-derived samples)
- [ ] 4.3 Implement Level C run: cross-dataset transfer (train-source x test-source)
- [ ] 4.4 Export transfer matrix artifact with comparable binary metrics per source pair
- [ ] 4.5 Add per-source and per-robustness-slice FP/FN breakdowns to evaluation report

## 5. Reproducibility and artifact contract

- [ ] 5.1 Persist full run config snapshot (mix config, labeling policy, profile thresholds, seed)
- [ ] 5.2 Include dataset source revisions and split statistics in artifact manifest
- [ ] 5.3 Add reproducibility bundle check in tests (artifacts sufficient for rerun)

## 6. Documentation and diploma-ready outputs

- [ ] 6.1 Update README/OpenSpec docs with multi-dataset workflow and hh-rlhf usage
- [ ] 6.2 Add report template for diploma tables: A/B/C comparisons and source-wise errors
- [ ] 6.3 Add final checklist for defense package (key plots, metrics tables, limitations)

## 7. Verification

- [ ] 7.1 Add/extend tests for chosen/rejected adapter and source-aware validation
- [ ] 7.2 Add regression tests for anti-leakage split logic and mixed-source training mode
- [ ] 7.3 Run full experiment smoke path and verify that all mandatory artifacts are generated