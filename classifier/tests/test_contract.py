from classifier.src.api.contracts import validate_result_contract


def test_contract_validation_accepts_valid_payload() -> None:
    payload = {
        "is_malicious": False,
        "binary_label": "benign",
        "binary_confidence": 0.91,
        "threat_type": None,
        "threat_confidence": None,
        "signals": {"prompt_leakage": 0.0},
        "schema_version": "v2",
        "deployment_profile": "balanced",
        "thresholds": {"binary": 0.5, "threat": 0.5},
        "evidence": {"prompt_leakage": []},
    }
    validate_result_contract(payload)

