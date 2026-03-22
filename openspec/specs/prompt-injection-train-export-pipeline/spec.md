# prompt-injection-train-export-pipeline Specification

## Purpose
TBD - created by archiving change add-prompt-injection-train-export-script. Update Purpose after archive.
## Requirements
### Requirement: End-to-end prompt injection training/export script
The system SHALL provide a single executable script at `classifier/scripts/run_prompt_injection_train_export.py` that performs dataset loading, schema normalization, sample preparation, encoder training, evaluation, and artifact export in one run.

#### Scenario: Successful full run with defaults
- **WHEN** an operator runs the script without overriding optional parameters
- **THEN** the script SHALL use `dataset_id=neuralchemy/Prompt-injection-dataset`, `output_root=classifier/artifacts`, and `seed=42` and complete an end-to-end training/export run

### Requirement: CLI configuration contract
The script SHALL expose and validate CLI arguments `dataset_id`, `output_root`, `seed`, `experiment_name`, `include_baseline`, and `profile`, where `profile` MUST accept only `balanced` or `high_recall_security`.

#### Scenario: Invalid profile rejected
- **WHEN** an operator provides a profile value outside `balanced` or `high_recall_security`
- **THEN** the script SHALL terminate with a clear validation error describing accepted values

### Requirement: HF schema normalization with alias handling
The training flow SHALL normalize prompt-injection dataset columns and labels using alias-based mapping for required semantic fields and MUST fail fast with actionable errors when required fields cannot be resolved.

#### Scenario: Missing required columns after alias resolution
- **WHEN** the loaded dataset does not contain any column aliases matching required text/label semantics
- **THEN** the script SHALL stop before training and output an error listing missing semantic fields, allowed aliases, and discovered columns

### Requirement: Reuse of existing project modules
The script SHALL orchestrate data, training, modeling, and evaluation by calling existing modules under `classifier/src/dataset/`, `classifier/src/training/`, `classifier/src/models/`, and `classifier/src/evaluation/` rather than duplicating equivalent logic.

#### Scenario: Implementation review for module reuse
- **WHEN** maintainers inspect the script implementation
- **THEN** they SHALL observe calls into existing project modules for core operations and no duplicated independent pipeline implementation for those operations

### Requirement: Optional baseline branch
The script SHALL support an optional baseline training/evaluation branch controlled by `include_baseline` and MUST keep encoder artifact export as the primary required output.

#### Scenario: Baseline disabled
- **WHEN** `include_baseline=false`
- **THEN** the script SHALL skip baseline training while still producing the complete encoder inference bundle and required evaluation report

