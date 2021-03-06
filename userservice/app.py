import logging
from aiohttp import web
from yarl import URL
from sortedcontainers import SortedDict
from user_types import User, DBUser, DBUserList
from data_access_gate_impl import DataStorage, DB
from helpers import user_id_from_request


LOGGER = logging.getLogger(__name__)
ds_key = 'ds'
routes = web.RouteTableDef()


@routes.get('/')
async def health(request):
    return web.json_response({'name': 'user-service'})


@routes.get('/users/{user_id}')
async def get_user(request: web.Request):
    ds: DataStorage = request.app[ds_key]
    user_id = user_id_from_request(request)
    user = await ds.get(user_id)
    if user is None:
        return web.json_response({"message": "User for given User Id does not exist"}, status=404)

    return web.json_response(user.to_dict())


@routes.get('/users')
async def get_users(request):
    ds: DataStorage = request.app[ds_key]

    # *** This needs to be reworked using Multipart concept ***
    u = DBUserList([])
    async for batch in ds.iterate():
        u.users.extend(batch.users)

    return web.json_response(u.to_dict()["users"])


@routes.post('/users')
async def create_user(request):
    ds: DataStorage = request.app[ds_key]
    user_dict = await request.json()
    user = User.from_dict(user_dict)
    user_id = await ds.add(user)
    if user_id is None:
        return web.json_response({"message": "Unable to create user"}, status=400)

    return web.json_response(DBUser.from_base(user_id=user_id, user=user).to_dict(), status=201)


@routes.put('/users/{user_id}')
async def update_user(request):
    ds: DataStorage = request.app[ds_key]
    user_dict = await request.json()
    user = DBUser.from_dict(user_dict)
    user_id = user_id_from_request(request)
    if user.user_id != user_id:
        return web.json_response({"message": "User Id provided in URL does not match the User Id provided "
                                             "in Json request data"}, status=404)

    user_id = await ds.update(user)
    if user_id is None:
        return web.json_response({"message": "User for given User Id does not exist"}, status=404)

    return web.json_response(DBUser.from_base(user_id=user_id, user=user).to_dict(), status=201)


@routes.delete('/users/{user_id}')
async def delete_user(request):
    ds: DataStorage = request.app[ds_key]
    user_id = user_id_from_request(request)
    user = await ds.delete(user_id)
    if user is None:
        return web.json_response(None, status=404)

    #return web.json_response(user.to_dict(), status=204)
    return web.json_response(None, status=204)


def create_app():
    app = web.Application()
    app[ds_key] = DataStorage(DB(SortedDict(), 0))
    app.add_routes(routes)
    return app
