## MODIFIED Requirements

### Requirement: Dataset category coverage
The training and evaluation dataset MUST include benign, malicious, borderline, obfuscated, and near-miss benign samples that are semantically close to attack topics, and MUST additionally cover staged attack prompts and adversarially rewritten prompts designed to evade naive detectors.

#### Scenario: Category distribution validation
- **WHEN** dataset validation is executed before training
- **THEN** the system SHALL verify that each required category is represented and SHALL fail validation if any category is missing

### Requirement: Multilingual and noisy input support
The dataset MUST include Russian, English, mixed-language, transliterated, and intentionally distorted text examples, and SHALL track dedicated robustness subsets for language transfer and noisy adaptive prompts.

#### Scenario: Language coverage check
- **WHEN** dataset metadata is inspected
- **THEN** the system SHALL expose counts for each required language/form, SHALL identify robustness subsets for multilingual and noisy prompts, and SHALL block release if required coverage is absent

### Requirement: Label schema consistency
Each sample MUST contain mandatory fields: `id`, `text`, `binary_label`, `threat_type`, `language`, and `source`.

#### Scenario: Mandatory field enforcement
- **WHEN** a sample is ingested into processed dataset
- **THEN** ingestion SHALL reject samples missing any mandatory field and SHALL log the validation error

### Requirement: Anti-shortcut data quality controls
Dataset construction MUST prevent trivial lexical shortcuts that let models infer labels from obvious phrases only, and SHALL specifically validate that benign security-discussion samples and obfuscated malicious samples remain present in sufficient quantity.

#### Scenario: Shortcut heuristic detection
- **WHEN** quality checks detect overrepresented trigger phrases in malicious class or detect missing benign near-miss coverage
- **THEN** the data pipeline SHALL flag the split and SHALL require balancing or augmentation before training

### Requirement: Adversarial holdout readiness
The processed dataset MUST define stable adversarial holdout splits for robustness evaluation, including obfuscation, policy-bypass, multilingual transfer, and benign security-discussion slices.

#### Scenario: Holdout manifest validation
- **WHEN** the dataset manifest is prepared for an experiment run
- **THEN** the system SHALL verify that all required adversarial holdout splits are present and SHALL fail experiment setup if any split is missing
