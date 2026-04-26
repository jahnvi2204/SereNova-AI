"""FastAPI middleware: latency headers + rough token/cost estimates for JSON responses."""
from __future__ import annotations

import logging
import time
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Rough USD per 1M tokens (Gemini Flash family; override via env in production dashboards)
_DEFAULT_IN_PER_1M = 0.075
_DEFAULT_OUT_PER_1M = 0.30


def estimate_tokens(text: str) -> int:
    """Very rough token estimate for logging (not for billing)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Adds X-Request-Duration-Ms; logs path, status, duration, optional body size."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        t0 = time.perf_counter()
        response: Response = await call_next(request)
        dt_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        response.headers["X-Request-Duration-Ms"] = str(dt_ms)
        try:
            logger.info(
                "%s %s -> %s in %sms",
                request.method,
                request.url.path,
                getattr(response, "status_code", "?"),
                dt_ms,
            )
        except Exception:  # noqa: BLE001
            pass
        return response


def rough_cost_usd(
    input_tokens: int,
    output_tokens: int,
    in_per_m: float = _DEFAULT_IN_PER_1M,
    out_per_m: float = _DEFAULT_OUT_PER_1M,
) -> float:
    """Naive cost estimate for dashboarding (not vendor-accurate)."""
    return (input_tokens / 1_000_000.0) * in_per_m + (output_tokens / 1_000_000.0) * out_per_m
