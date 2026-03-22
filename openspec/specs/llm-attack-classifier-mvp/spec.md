# llm-attack-classifier-mvp Specification

## Purpose
TBD - created by archiving change plan-openspec-classifier. Update Purpose after archive.
## Requirements
### Requirement: Two-stage classification pipeline
The classifier MUST process each input message in two stages: binary safety detection and, for malicious messages, threat type classification.

#### Scenario: Benign message stops after stage one
- **WHEN** the binary stage predicts `benign`
- **THEN** the system SHALL return a result with `binary_label=benign` and SHALL NOT execute threat type classification

#### Scenario: Malicious message proceeds to stage two
- **WHEN** the binary stage predicts `malicious`
- **THEN** the system SHALL execute threat type classification and include both binary and threat outputs in the response

### Requirement: Hybrid signal aggregation
The classifier MUST combine ML outputs with rule-based security signals in a single inference result.

#### Scenario: Rule-based signals are present in response
- **WHEN** a prediction is generated
- **THEN** the response SHALL include a `signals` object with rule-derived scores or flags relevant to attack patterns

### Requirement: Output contract for gateway integration
The classifier MUST return a stable JSON-compatible structure containing maliciousness decision, confidences, threat type, and auxiliary signals.

#### Scenario: Full malicious response format
- **WHEN** input is classified as malicious
- **THEN** the result SHALL include `is_malicious`, `binary_label`, `binary_confidence`, `threat_type`, `threat_confidence`, and `signals`

