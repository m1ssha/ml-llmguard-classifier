# classifier-inference-interface Specification

## Purpose
TBD - created by archiving change plan-openspec-classifier. Update Purpose after archive.
## Requirements
### Requirement: Unified Python inference API
The classifier module MUST expose a single Python prediction entrypoint equivalent to `predict(text)` for backend usage.

#### Scenario: Predict API invocation
- **WHEN** backend calls the classifier with input text
- **THEN** the API SHALL return a structured result object without requiring direct access to internal model components

### Requirement: Structured output fields
Inference output MUST include `binary_label`, `binary_confidence`, `threat_type`, `threat_confidence`, and `signals` in addition to top-level maliciousness indicator.

#### Scenario: Output schema validation
- **WHEN** an inference result is serialized
- **THEN** schema validation SHALL pass only if all required output fields are present with valid types

### Requirement: Confidence and score logging
The inference pipeline MUST log predicted classes and confidence values for observability and downstream policy analysis.

#### Scenario: Inference audit logging
- **WHEN** prediction is completed
- **THEN** the system SHALL write an audit log record containing binary and threat confidences plus rule-signal summary

### Requirement: CPU-compatible inference performance
The inference path MUST run without dedicated GPU and MUST be suitable for local deployment constraints.

#### Scenario: CPU execution mode
- **WHEN** inference is executed on a CPU-only environment
- **THEN** the model SHALL produce predictions successfully within configured latency limits

