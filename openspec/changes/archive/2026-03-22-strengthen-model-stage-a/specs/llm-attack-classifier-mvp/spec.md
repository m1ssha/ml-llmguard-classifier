## MODIFIED Requirements

### Requirement: Two-stage classification pipeline
The classifier MUST process each input message in two stages: binary safety detection and, for malicious messages, threat type classification.

#### Scenario: Benign message stops after stage one
- **WHEN** the binary stage predicts `benign`
- **THEN** the system SHALL return a result with `binary_label=benign` and SHALL NOT execute threat type classification

#### Scenario: Malicious message proceeds to stage two
- **WHEN** the binary stage predicts `malicious`
- **THEN** the system SHALL execute threat type classification and include both binary and threat outputs in the response

### Requirement: Hybrid signal aggregation
The classifier MUST combine ML outputs with rule-based security signals in a single inference result, and SHALL support explainable evidence for obfuscation, prompt leakage, role override, and policy-bypass patterns.

#### Scenario: Rule-based signals are present in response
- **WHEN** a prediction is generated
- **THEN** the response SHALL include a `signals` object with rule-derived scores or flags relevant to attack patterns and MAY include evidence metadata under the active schema version

### Requirement: Output contract for gateway integration
The classifier MUST return a stable JSON-compatible structure containing maliciousness decision, confidences, threat type, and auxiliary signals.

#### Scenario: Full malicious response format
- **WHEN** input is classified as malicious
- **THEN** the result SHALL include `is_malicious`, `binary_label`, `binary_confidence`, `threat_type`, `threat_confidence`, and `signals`

### Requirement: MVP readiness for adaptive attacks
The MVP SHALL NOT be considered ready for security-oriented deployment unless adversarial dataset coverage, robustness evaluation, and calibrated deployment profiles are present.

#### Scenario: Readiness gate validation
- **WHEN** the project is reviewed for MVP completion
- **THEN** the readiness report SHALL fail if adversarial holdout coverage, robustness metrics, or deployment profile artifacts are missing
