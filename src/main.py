import typing
from logging import config as logging_config

import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse
from starlette.responses import StreamingResponse

from src.api.v1 import base
from src.core import config
from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)
app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)
app.include_router(base.router, prefix='/api/v1')

if __name__ == '__main__':
    uvicorn.run(
        'src.main:app',
        host=config.PROJECT_HOST,
        port=config.PROJECT_PORT,
    )
