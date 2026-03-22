## ADDED Requirements

### Requirement: Source-aware canonical sample schema
The pipeline MUST normalize all input datasets into a canonical schema that includes `id`, `text`, `binary_label`, `threat_type`, `language`, `source`, `dataset_id`, and `split_role` before training and evaluation.

#### Scenario: Canonical schema produced for mixed dataset run
- **WHEN** a multi-dataset training run starts
- **THEN** every ingested record SHALL be transformed into the canonical schema and invalid records SHALL be rejected with explicit validation errors

### Requirement: hh-rlhf chosen/rejected mapping support
The pipeline MUST support ingestion of Anthropic/hh-rlhf style pairs and MUST map `chosen` and `rejected` fields into canonical text examples according to configured weak-labeling rules.

#### Scenario: hh-rlhf pair is converted into canonical records
- **WHEN** loader receives a row containing `chosen` and `rejected`
- **THEN** the system SHALL emit canonical examples with traceable origin metadata that identifies whether the text came from `chosen` or `rejected`

### Requirement: Explicit dataset mix configuration
Training MUST be driven by an explicit dataset-mix configuration that defines source list, per-source quotas or weights, labeling strategy, and random seed.

#### Scenario: Reproducible mixed corpus build
- **WHEN** the same dataset-mix configuration and seed are reused
- **THEN** the system SHALL rebuild the same mixed corpus composition deterministically

### Requirement: Anti-leakage source-aware splitting
The data split stage MUST prevent leakage across train/validation/test by enforcing deduplication and source-aware split constraints.

#### Scenario: Near-duplicate appears across sources
- **WHEN** near-duplicate text is detected across candidate splits
- **THEN** the system SHALL assign duplicates to a single split and SHALL report deduplication actions in metadata

