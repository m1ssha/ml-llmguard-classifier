from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GatewayRequest:
    text: str
    request_id: str


class GatewayIntegrationService:
    def __init__(self, predictor) -> None:
        self.predictor = predictor

    def handle(self, request: GatewayRequest) -> dict:
        try:
            prediction = self.predictor.predict(request.text)
            return {
                "request_id": request.request_id,
                "status": "ok",
                "result": prediction,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "request_id": request.request_id,
                "status": "error",
                "error": {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
            }

