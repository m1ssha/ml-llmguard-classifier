## ADDED Requirements

### Requirement: Explainable hybrid scoring
The inference layer MUST produce rule-based scores and evidence fragments that explain why an input was associated with prompt leakage, role override, policy bypass, or obfuscation patterns.

#### Scenario: Evidence-enriched prediction
- **WHEN** inference is run on an input containing attack indicators
- **THEN** the result SHALL include structured rule scores and human-interpretable evidence for the matched indicators

### Requirement: Obfuscation-aware rule processing
The rule engine MUST normalize and inspect inputs for spaced tokens, Unicode confusables, transliteration variants, and common text obfuscation strategies before scoring.

#### Scenario: Obfuscated prompt detection
- **WHEN** a malicious prompt hides key phrases through spacing, confusable characters, or transliteration
- **THEN** the rule engine SHALL still evaluate the normalized signal and SHALL emit corresponding obfuscation-aware evidence

### Requirement: Threshold and calibration configuration
The hybrid detector MUST support configurable thresholds and calibrated confidence metadata for binary and threat-level decisions.

#### Scenario: Thresholded deployment mode
- **WHEN** the classifier is loaded for a deployment profile
- **THEN** the inference service SHALL load threshold and calibration settings alongside model artifacts and SHALL apply them consistently to predictions
