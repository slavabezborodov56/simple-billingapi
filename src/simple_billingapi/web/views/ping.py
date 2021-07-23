import os

import pkg_resources
from aiohttp.web import json_response
from aiohttp_pydantic import PydanticView


class PingView(PydanticView):
    application: str = os.getenv('APPLICATION_NAME')
    version: str = pkg_resources.get_distribution('simple-billingapi').version

    async def get(self):
        return json_response({
            'status': 'ok',
            'application': self.application,
            'version': self.version,
        })
