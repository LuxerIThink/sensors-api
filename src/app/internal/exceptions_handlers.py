from starlette.responses import JSONResponse


async def validation_exception_handler(type, exc):
    error = {"loc": [str(exc).split(":")[0], 1], "msg": str(exc), "type": str(type)}
    return JSONResponse(status_code=422, content={"detail": [error]})
