# classifier-dataset-and-labeling Specification

## Purpose
TBD - created by archiving change plan-openspec-classifier. Update Purpose after archive.
## Requirements
### Requirement: Dataset category coverage
The training and evaluation dataset MUST include benign, malicious, borderline, obfuscated, and near-miss benign samples that are semantically close to attack topics.

#### Scenario: Category distribution validation
- **WHEN** dataset validation is executed before training
- **THEN** the system SHALL verify that each required category is represented and SHALL fail validation if any category is missing

### Requirement: Multilingual and noisy input support
The dataset MUST include Russian, English, mixed-language, transliterated, and intentionally distorted text examples.

#### Scenario: Language coverage check
- **WHEN** dataset metadata is inspected
- **THEN** the system SHALL expose counts for each required language/form and SHALL block release if required coverage is absent

### Requirement: Label schema consistency
Each sample MUST contain mandatory fields: `id`, `text`, `binary_label`, `threat_type`, `language`, and `source`.

#### Scenario: Mandatory field enforcement
- **WHEN** a sample is ingested into processed dataset
- **THEN** ingestion SHALL reject samples missing any mandatory field and SHALL log the validation error

### Requirement: Anti-shortcut data quality controls
Dataset construction MUST prevent trivial lexical shortcuts that let models infer labels from obvious phrases only.

#### Scenario: Shortcut heuristic detection
- **WHEN** quality checks detect overrepresented trigger phrases in malicious class
- **THEN** the data pipeline SHALL flag the split and SHALL require balancing or augmentation before training

