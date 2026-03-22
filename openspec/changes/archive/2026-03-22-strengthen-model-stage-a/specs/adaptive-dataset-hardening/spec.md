## ADDED Requirements

### Requirement: Adversarial dataset coverage
The dataset MUST include adaptive-attack examples covering multilingual prompts, transliterated prompts, obfuscated prompts, staged attack prompts, and near-miss benign prompts that are semantically close to attack intent.

#### Scenario: Adversarial coverage validation
- **WHEN** the processed dataset is validated before training
- **THEN** the validation pipeline SHALL verify coverage for each adaptive-attack category and SHALL fail if any required category is absent

### Requirement: Dedicated adversarial holdout splits
The dataset pipeline MUST produce dedicated holdout splits for robustness evaluation, including at minimum obfuscation, language-transfer, policy-bypass, and benign-security-discussion slices.

#### Scenario: Holdout split generation
- **WHEN** dataset preparation completes
- **THEN** the system SHALL export the required adversarial holdout splits with stable names and documented membership criteria

### Requirement: Benign near-miss balance
The dataset MUST include benign samples that discuss jailbreaks, prompt injection, prompt leakage, or security controls without attempting to attack the model.

#### Scenario: Near-miss benign inspection
- **WHEN** quality review is executed on the dataset
- **THEN** the system SHALL confirm presence of benign near-miss examples for each major attack family and SHALL block release if the benign set is too semantically distant from malicious prompts
