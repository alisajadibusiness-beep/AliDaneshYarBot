import logging
from typing import Optional

from aiohttp import web


logger = logging.getLogger(__name__)


# ============================================================
# Health handlers
# ============================================================

async def root_handler(request: web.Request) -> web.Response:
    """
    Root endpoint.

    Example:
    GET /
    """

    return web.json_response(
        {
            "service": "AliDaneshYarBot",
            "status": "running",
            "message": "علی دانش‌یار فعال است.",
        }
    )


async def health_handler(request: web.Request) -> web.Response:
    """
    Render health check endpoint.

    Example:
    GET /health
    """

    return web.json_response(
        {
            "status": "ok",
            "service": "AliDaneshYarBot",
        }
    )


async def ready_handler(request: web.Request) -> web.Response:
    """
    Readiness endpoint.

    Kept intentionally lightweight.
    """

    return web.json_response(
        {
            "status": "ready",
            "service": "AliDaneshYarBot",
        }
    )


# ============================================================
# Server creation
# ============================================================

async def start_health_server(
    host: str = "0.0.0.0",
    port: int = 10000,
) -> web.AppRunner:
    """
    Start aiohttp HTTP server.

    Render requires the public-facing web service to bind
    to 0.0.0.0 and the assigned PORT.
    """

    app = web.Application()

    app.router.add_get(
        "/",
        root_handler,
    )

    app.router.add_get(
        "/health",
        health_handler,
    )

    app.router.add_get(
        "/ready",
        ready_handler,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host=host,
        port=port,
    )

    await site.start()

    logger.info(
        "HTTP health server started on %s:%s",
        host,
        port,
    )

    return runner


# ============================================================
# Server shutdown
# ============================================================

async def stop_health_server(
    runner: Optional[web.AppRunner],
) -> None:

    if runner is None:
        return

    try:
        await runner.cleanup()

        logger.info(
            "HTTP health server stopped."
        )

    except Exception:
        logger.exception(
            "Error while stopping HTTP health server."
        )
