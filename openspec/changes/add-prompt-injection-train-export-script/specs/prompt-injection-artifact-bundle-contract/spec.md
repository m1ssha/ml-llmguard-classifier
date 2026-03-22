## ADDED Requirements

### Requirement: Mandatory inference artifact bundle
An end-to-end training/export run SHALL produce an inference-ready bundle containing exactly the required files: `encoder_model.joblib`, `tokenizer.joblib`, `label_mapping.json`, `thresholds.json`, `training_metadata.json`, `artifact_manifest.json`, and `evaluation_report.json`.

#### Scenario: Bundle completeness validation
- **WHEN** a run completes successfully
- **THEN** all required bundle files SHALL exist under the run output directory and be referenced by the manifest

### Requirement: Manifest for inference decoupling
The system SHALL write `artifact_manifest.json` describing exported artifact paths and metadata needed to load the bundle from inference without direct dependencies on training internals.

#### Scenario: Inference consumes exported bundle
- **WHEN** an inference loader is pointed to a generated bundle directory
- **THEN** it SHALL be able to resolve required assets from `artifact_manifest.json` without importing training-only modules

### Requirement: Evaluation report coverage
The system SHALL write `evaluation_report.json` that includes binary metrics for both `balanced` and `high_recall_security` profiles, robustness slice information, and references to exported artifact paths.

#### Scenario: Report contains multi-profile metrics and slices
- **WHEN** a run completes and `evaluation_report.json` is generated
- **THEN** the report SHALL contain separate binary metric sections for `balanced` and `high_recall_security` and a section documenting robustness slice outcomes

### Requirement: Testing and documentation for script contract
The project SHALL include automated tests in `classifier/tests/` with at least one smoke test and one artifact-structure contract test for the script, and SHALL include a short run guide in `README.md`.

#### Scenario: CI validates script contract
- **WHEN** the project test suite runs for this change
- **THEN** tests SHALL verify script executability and required bundle/report structure, and the README SHALL document how to invoke the script

