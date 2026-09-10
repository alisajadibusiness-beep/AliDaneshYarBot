from aiohttp import web


async def health(request):
    return web.json_response(
        {
            "status": "ok",
            "service": "AliDaneshYarBot",
        }
    )


def create_app() -> web.Application:
    app = web.Application()

    app.router.add_get(
        "/",
        health,
    )

    app.router.add_get(
        "/health",
        health,
    )

    return app


async def start_health_server(
    host: str = "0.0.0.0",
    port: int = 10000,
):
    app = create_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host,
        port,
    )

    await site.start()

    return runner
