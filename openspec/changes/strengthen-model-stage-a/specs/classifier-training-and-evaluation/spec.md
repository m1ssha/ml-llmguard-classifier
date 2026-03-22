## MODIFIED Requirements

### Requirement: Baseline model training
The project MUST provide a reproducible baseline training pipeline using TF-IDF with Logistic Regression for comparison.

#### Scenario: Baseline training execution
- **WHEN** baseline training command is run on prepared dataset
- **THEN** the pipeline SHALL produce a trained baseline artifact and SHALL store evaluation metrics in a report file

### Requirement: Encoder-based model training
The project MUST provide a training pipeline for an encoder-only text classifier suitable for CPU inference, and SHALL support comparison between the current surrogate encoder path and a stronger encoder candidate under the same experiment protocol.

#### Scenario: Encoder model artifact generation
- **WHEN** encoder training finishes successfully
- **THEN** the system SHALL persist model weights or serialized estimator, tokenizer/config, label mapping, thresholds, and training metadata for reproducible inference

### Requirement: Mandatory metric reporting
Evaluation MUST report binary metrics (`accuracy`, `precision`, `recall`, `F1`, `ROC-AUC`) and multiclass metrics (`macro F1`, `weighted F1`, confusion matrix, per-class precision/recall), and SHALL additionally report robustness-slice outcomes and threshold-specific operating points.

#### Scenario: Metrics completeness validation
- **WHEN** evaluation report is generated
- **THEN** the report SHALL contain all mandatory clean-test and robustness metrics and SHALL fail validation if any required metric is missing

### Requirement: Standard experiment protocol
The evaluation workflow MUST support three experiments: baseline-vs-encoder, binary-only-vs-two-stage, and ablation of rule-based signals, and SHALL extend them with robustness testing against obfuscation, paraphrase, multilingual transfer, and benign security-discussion slices.

#### Scenario: Experiment suite run
- **WHEN** experiment runner is launched in full mode
- **THEN** the system SHALL execute all required clean and adversarial experiment types and SHALL export comparable summary results

### Requirement: Calibration and threshold tuning
The training and evaluation workflow MUST generate calibrated deployment profiles for at least balanced mode and high-recall security mode.

#### Scenario: Deployment profile export
- **WHEN** model selection is completed
- **THEN** the system SHALL export threshold and calibration settings for each required deployment profile
