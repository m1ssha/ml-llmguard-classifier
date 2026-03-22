## ADDED Requirements

### Requirement: Adversarial robustness suite
The evaluation workflow MUST execute robustness tests for paraphrase attacks, obfuscation attacks, language transfer, policy bypass, and benign security discussions.

#### Scenario: Robustness suite execution
- **WHEN** the full security evaluation workflow is launched
- **THEN** the system SHALL run all required adversarial slices and SHALL export results separately from the clean test set metrics

### Requirement: False positive security analysis
The evaluation workflow MUST quantify false positives on benign prompts that discuss security, jailbreaks, prompt injection, or model safety in a non-malicious context.

#### Scenario: Benign security false positive review
- **WHEN** a model evaluation report is generated
- **THEN** the report SHALL include a dedicated summary of false positives on benign security-discussion slices

### Requirement: Calibration-aware reporting
The evaluation workflow MUST report threshold-specific and calibration-aware operating points for deployment profiles.

#### Scenario: Deployment profile reporting
- **WHEN** model evaluation is completed for release consideration
- **THEN** the report SHALL include calibrated operating points for at least balanced mode and high-recall security mode
