## MODIFIED Requirements

### Requirement: Dataset category coverage
The training and evaluation dataset MUST include benign, malicious, borderline, obfuscated, and near-miss benign samples that are semantically close to attack topics, and MUST report category coverage per source domain.

#### Scenario: Category distribution validation
- **WHEN** dataset validation is executed before training
- **THEN** the system SHALL verify that each required category is represented and SHALL fail validation if any category is missing

#### Scenario: Source-wise category coverage check
- **WHEN** a mixed dataset is prepared from multiple sources
- **THEN** the system SHALL export category counts per `dataset_id` and SHALL flag missing critical categories in any configured primary source

### Requirement: Label schema consistency
Each sample MUST contain mandatory fields: `id`, `text`, `binary_label`, `threat_type`, `language`, and `source`, and MUST include source-tracing fields `dataset_id` and `split_role` for mixed-source experiments.

#### Scenario: Mandatory field enforcement
- **WHEN** a sample is ingested into processed dataset
- **THEN** ingestion SHALL reject samples missing any mandatory field and SHALL log the validation error

#### Scenario: Source-tracing enforcement for mixed runs
- **WHEN** dataset build mode is multi-source
- **THEN** ingestion SHALL reject samples without `dataset_id` or `split_role`

### Requirement: Anti-shortcut data quality controls
Dataset construction MUST prevent trivial lexical shortcuts that let models infer labels from obvious phrases only, and MUST monitor shortcut concentration per source domain.

#### Scenario: Shortcut heuristic detection
- **WHEN** quality checks detect overrepresented trigger phrases in malicious class
- **THEN** the data pipeline SHALL flag the split and SHALL require balancing or augmentation before training

#### Scenario: Source-specific shortcut drift detection
- **WHEN** one source has trigger concentration significantly above configured threshold
- **THEN** the pipeline SHALL mark the run as quality-risk and SHALL require explicit override to continue

## ADDED Requirements

### Requirement: Anti-leakage split constraints
The dataset build process MUST enforce anti-leakage constraints across train/validation/test, including near-duplicate detection across all configured sources.

#### Scenario: Duplicate detected across split boundaries
- **WHEN** duplicate or near-duplicate texts are found in different splits
- **THEN** the pipeline SHALL reassign or remove conflicting samples and SHALL record the action in split metadata

