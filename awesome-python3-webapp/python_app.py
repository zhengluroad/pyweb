import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time, aiomysql
from datetime import datetime

from aiohttp import web


def index(request):
	return web.Response(body=b'<h1>index page</h1>',content_type='text/html')

async def init():
	app = web.Application()
	app.add_routes([web.get('/',index)])

	runner = web.AppRunner(app)
	await runner.setup()
	site = web.TCPSite(runner, 'localhost', 9000)
	await site.start()
	print('服务器启动成功！')

async def create_pool(loop, **kw):
    logging.info('create datebase connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw['password'],
        db = kw['db'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minisize = kw.get('minisize', 1),
        loop = loop
    )

async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows returned : %s' % len(rs))
        return rs

loop = asyncio.get_event_loop()
loop.run_until_complete(init())
loop.run_forever()