from aiohttp import web


@web.middleware
async def check_auth(request, handler):
    if request.path != '/api/auth':
        auth = request.headers.get('Authorization')

        if not auth:
            return web.HTTPUnauthorized()

        auth_users = await request.app['db'].get_auth_list()
        user_perm = auth_users.get(auth)

        if not user_perm or user_perm == 'blocked':
            return web.HTTPForbidden()

        if request.method != 'GET' and user_perm != 'admin':
            return web.HTTPForbidden()

    response = await handler(request)
    return response
