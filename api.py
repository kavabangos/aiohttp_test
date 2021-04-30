from aiohttp import web
import validators
from pydantic import ValidationError


async def auth(request):
    try:
        data = await request.app['db'].get_api_key(validators.Auth(**(await request.json())))
    except ValidationError as e:
        return web.json_response(data={'success': False, 'message': e.errors()})

    if data:
        response_json = {'success': True, 'data': {'api_key': data.pass_hash}}
    else:
        response_json = {'success': False, 'message': 'user not found'}

    return web.json_response(data=response_json)


async def get_users(request):
    param = request.query.get('user_id')
    result = await request.app['db'].get_users(user_id=param)

    response = []

    for row in result:
        item = dict(row)
        item['birth_date'] = str(row.birth_date)
        response.append(item)

    return web.json_response(data={'success': True, 'data': response})


async def create_user(request):
    try:
        data = validators.CreateUser(**(await request.json()))
        result = await request.app['db'].created_user(param=data)

    except ValidationError as e:
        return web.json_response(data={'success': False, 'message': e.errors()})
    except Exception as e:
        return web.json_response(data={'success': False, 'message': str(e)})

    return web.json_response(data={'success': True, 'user_id': result[0]})


async def update_user(request):
    try:

        data = validators.UpdateUser(**(await request.json())).dict()
        data = {k: v for k, v in data.items() if v is not None}
        user_id = request.match_info['user_id']

        await request.app['db'].update_user(user_id=user_id, param=data)

    except ValidationError as e:
        return web.json_response(data={'success': False, 'message': e.errors()})
    except Exception as e:
        return web.json_response(data={'success': False, 'message': str(e)})

    return web.json_response(data={'success': True})


async def delete_user(request):
    try:

        user_id = request.match_info['user_id']
        await request.app['db'].delete_user(user_id=user_id)

    except Exception as e:
        return web.json_response(data={'success': False, 'message': str(e)})

    return web.json_response(data={'success': True})
