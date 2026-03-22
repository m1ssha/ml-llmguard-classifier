# Stage A Hardening Report

## Scope

Stage A implemented model hardening for adaptive-attack detection across dataset validation, hybrid inference, stronger encoder candidate training, artifact export, and robustness-oriented evaluation.

## Implemented Changes

- Dataset hardening:
  - extended required categories with staged/adversarial-rewrite coverage;
  - added required adversarial holdout slices (`obfuscation`, `policy_bypass`, `multilingual_transfer`, `benign_security_discussion`);
  - added strict adversarial validation mode and holdout split builder.
- Quality controls:
  - added benign near-miss and adversarial rewrite coverage checks in shortcut quality gate.
- Hybrid detector:
  - rule engine now includes normalization for spacing/confusable patterns and returns structured evidence;
  - inference output now carries `schema_version`, `deployment_profile`, `thresholds`, and `evidence`;
  - predictor loads deployment profile thresholds and applies thresholded decisions.
- Stronger encoder candidate:
  - added stronger CPU-friendly encoder pipeline (word+char features);
  - added inference artifact bundle export with model/tokenizer, label mapping, thresholds, metadata, manifest.
- Evaluation:
  - experiment suite now compares surrogate vs stronger encoder;
  - exports robustness slice counts and benign-security false-positive proxy;
  - includes deployment profiles for balanced and high-recall security modes.

## Artifacts Added/Updated

- Code:
  - `classifier/src/dataset/schema.py`
  - `classifier/src/dataset/validator.py`
  - `classifier/src/dataset/quality.py`
  - `classifier/src/inference/rules.py`
  - `classifier/src/inference/predictor.py`
  - `classifier/src/api/contracts.py`
  - `classifier/src/models/encoder.py`
  - `classifier/src/training/pipelines.py`
  - `classifier/src/evaluation/experiments.py`
- Tests:
  - `classifier/tests/test_contract.py`
  - `classifier/tests/test_stage_a_hardening.py`

## Limitations

- Validation command execution (`pytest`) was not completed in this session due to denied terminal execution.
- Stronger encoder remains sklearn-based CPU candidate, not yet a transformer-based model.
- Robustness metrics currently export slice-level counts/proxy and should be extended to full classifier confusion metrics per slice in next iteration.

## Rollout Note

Recommended rollout path: offline evaluation -> shadow evaluation in gateway -> threshold tuning per deployment profile -> controlled production enablement.
