from api import get_users, auth, create_user, update_user, delete_user


def set_routes(app):
    app.router.add_route('POST', '/api/auth', auth)

    app.router.add_route('GET', '/api', get_users)
    app.router.add_route('POST', '/api', create_user)
    app.router.add_route('PUT', '/api/{user_id}', update_user)
    app.router.add_route('DELETE', '/api/{user_id}', delete_user)
