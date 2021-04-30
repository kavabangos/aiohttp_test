import sys
import asyncio
import logging

from aiohttp import web
from routes import set_routes
from models import set_db, close_db
from middleware import check_auth

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


app = web.Application()

set_routes(app)

app.on_startup.append(set_db)
app.on_cleanup.append(close_db)

app.middlewares.append(check_auth)

logging.basicConfig(level=logging.DEBUG, filename='log.log')

web.run_app(app)
