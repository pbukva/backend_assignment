from aiohttp import web
from yarl import URL


def user_id_from_request(request: web.Request):
    url = URL(request.path)
    user_id_str = url.parts[-1]
    user_id = int(user_id_str)
    return user_id
