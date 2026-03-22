## MODIFIED Requirements

### Requirement: Baseline model training
The project MUST provide a reproducible baseline training pipeline using TF-IDF with Logistic Regression for comparison, and MUST support both single-source and configured multi-source dataset compositions.

#### Scenario: Baseline training execution
- **WHEN** baseline training command is run on prepared dataset
- **THEN** the pipeline SHALL produce a trained baseline artifact and SHALL store evaluation metrics in a report file

#### Scenario: Baseline run with mixed-source corpus
- **WHEN** baseline training is launched with a dataset-mix configuration
- **THEN** the run SHALL record source composition metadata and SHALL train on the canonical mixed corpus

### Requirement: Mandatory metric reporting
Evaluation MUST report binary metrics (`accuracy`, `precision`, `recall`, `F1`, `ROC-AUC`) and multiclass metrics (`macro F1`, `weighted F1`, confusion matrix, per-class precision/recall), and MUST additionally report per-source error statistics for mixed-source experiments.

#### Scenario: Metrics completeness validation
- **WHEN** evaluation report is generated
- **THEN** the report SHALL contain all mandatory metrics and SHALL fail validation if any required metric is missing

#### Scenario: Per-source metrics validation
- **WHEN** experiment mode includes more than one source dataset
- **THEN** the report SHALL include per-source FP/FN statistics and SHALL fail validation when source-level metrics are absent

### Requirement: Standard experiment protocol
The evaluation workflow MUST support the mandatory experiment set: baseline-vs-encoder, binary-only-vs-two-stage, ablation of rule-based signals, and cross-dataset transfer experiments.

#### Scenario: Experiment suite run
- **WHEN** experiment runner is launched in full mode
- **THEN** the system SHALL execute all mandatory experiment types and SHALL export comparable summary results

## ADDED Requirements

### Requirement: Cross-dataset transfer reporting
The evaluation workflow MUST export a train-source to test-source transfer matrix for diploma analysis.

#### Scenario: Transfer matrix persisted
- **WHEN** cross-dataset evaluation completes
- **THEN** the system SHALL save a machine-readable transfer matrix artifact that links each metric block to source pair metadata

