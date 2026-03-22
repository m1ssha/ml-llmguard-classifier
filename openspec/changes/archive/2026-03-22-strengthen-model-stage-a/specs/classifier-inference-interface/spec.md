## MODIFIED Requirements

### Requirement: Unified Python inference API
The classifier module MUST expose a single Python prediction entrypoint equivalent to `predict(text)` for backend usage.

#### Scenario: Predict API invocation
- **WHEN** backend calls the classifier with input text
- **THEN** the API SHALL return a structured result object without requiring direct access to internal model components

### Requirement: Structured output fields
Inference output MUST include `binary_label`, `binary_confidence`, `threat_type`, `threat_confidence`, and `signals` in addition to top-level maliciousness indicator, and SHALL include version and threshold metadata plus optional evidence fields for explainability.

#### Scenario: Output schema validation
- **WHEN** an inference result is serialized
- **THEN** schema validation SHALL pass only if all required output fields are present with valid types and version metadata is attached

### Requirement: Confidence and score logging
The inference pipeline MUST log predicted classes and confidence values for observability and downstream policy analysis, and SHALL record applied deployment profile or threshold configuration.

#### Scenario: Inference audit logging
- **WHEN** prediction is completed
- **THEN** the system SHALL write an audit log record containing binary and threat confidences, rule-signal summary, and deployment-profile metadata

### Requirement: CPU-compatible inference performance
The inference path MUST run without dedicated GPU and MUST be suitable for local deployment constraints.

#### Scenario: CPU execution mode
- **WHEN** inference is executed on a CPU-only environment
- **THEN** the model SHALL produce predictions successfully within configured latency limits

### Requirement: Evidence-aware response contract
The inference interface MUST support additive explainability fields that expose matched rule evidence without breaking existing gateway consumers.

#### Scenario: Additive contract expansion
- **WHEN** the inference response includes evidence data
- **THEN** the additional fields SHALL be schema-versioned and SHALL remain backward-compatible for consumers that only read the core MVP fields
