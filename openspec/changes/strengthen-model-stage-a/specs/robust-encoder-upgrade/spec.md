## ADDED Requirements

### Requirement: Stronger encoder candidate
The training system MUST support a stronger encoder-based candidate beyond the current surrogate pipeline while preserving CPU-compatible inference as a deployment constraint.

#### Scenario: Strong encoder training run
- **WHEN** the stronger encoder training pipeline is executed
- **THEN** the system SHALL train the configured encoder candidate and SHALL persist the model, tokenizer, label mapping, and training metadata

### Requirement: Comparative encoder benchmarking
The project MUST compare the stronger encoder candidate against the current surrogate pipeline on the same dataset and adversarial robustness suite.

#### Scenario: Encoder comparison report
- **WHEN** evaluation is executed for model selection
- **THEN** the report SHALL include quality and latency comparisons between the surrogate and stronger encoder candidates

### Requirement: Deployment-ready artifact bundle
Each encoder candidate MUST export an inference bundle that includes model weights or serialized estimator, preprocessing configuration, label mapping, thresholds, and version metadata.

#### Scenario: Artifact bundle export
- **WHEN** training finishes successfully
- **THEN** the system SHALL write a complete versioned artifact bundle that is sufficient to reproduce inference without access to training code internals
