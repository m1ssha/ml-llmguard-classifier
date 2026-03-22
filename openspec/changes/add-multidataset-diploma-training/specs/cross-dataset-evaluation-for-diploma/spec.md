## ADDED Requirements

### Requirement: Three-level diploma experiment protocol
The evaluation workflow MUST execute three mandatory levels: single-dataset baseline, mixed-dataset training, and cross-dataset transfer.

#### Scenario: Full diploma evaluation run
- **WHEN** the full evaluation suite is launched for diploma reporting
- **THEN** the system SHALL produce outputs for Level A (single-source), Level B (mixed-source), and Level C (cross-dataset transfer)

### Requirement: Cross-dataset transfer matrix
The report MUST include a train-source to test-source transfer matrix with comparable binary metrics for each cell.

#### Scenario: Transfer matrix exported
- **WHEN** cross-dataset evaluation completes
- **THEN** the report SHALL contain a machine-readable matrix with at least accuracy, precision, recall, F1, and ROC-AUC per source pair

### Requirement: Source-slice error analysis
The report MUST include per-source and per-robustness-slice false-positive and false-negative breakdowns.

#### Scenario: Error analysis section is generated
- **WHEN** evaluation report is built
- **THEN** the system SHALL export FP/FN counts and rates for each source and required robustness slice

### Requirement: Reproducibility evidence bundle
Each diploma experiment run MUST save config, seed, dataset revisions, and artifact manifest in a reproducibility bundle.

#### Scenario: Reproducibility bundle verification
- **WHEN** a reviewer inspects experiment artifacts
- **THEN** they SHALL be able to identify exact dataset sources and rerun conditions from saved metadata

