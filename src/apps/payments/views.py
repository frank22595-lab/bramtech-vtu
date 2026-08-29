"""
Monnify webhook receiver.

Monnify POSTs JSON here with a signed header. We verify, log, and process.

⚠️ In production this URL must be reachable from the internet AND registered
in your Monnify dashboard. Use ngrok or Cloudflare Tunnel for local dev.
"""
from __future__ import annotations

import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import (
    WebhookAlreadyProcessed, process_monnify_webhook,
    verify_monnify_signature,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def monnify_webhook(request: HttpRequest) -> JsonResponse:
    raw = request.body
    sig = request.headers.get("monnify-signature", "")

    if not verify_monnify_signature(raw, sig):
        logger.warning("Monnify webhook: invalid signature")
        return JsonResponse({"detail": "invalid signature"}, status=401)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return JsonResponse({"detail": "invalid json"}, status=400)

    try:
        fe = process_monnify_webhook(payload)
    except WebhookAlreadyProcessed:
        # Idempotent — Monnify may retry
        return JsonResponse({"status": "already processed"}, status=200)
    except Exception as e:
        logger.exception("Monnify webhook processing error")
        return JsonResponse({"detail": str(e)}, status=500)

    if fe:
        return JsonResponse({
            "status": "applied",
            "funding_id": str(fe.public_id),
            "amount": str(fe.net_amount),
        })
    return JsonResponse({"status": "ignored"})
