from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Date, select)

import aiopg.sa
from config import postgres
import hashlib

meta = MetaData()

db_url = "postgresql://{user}:{password}@{host}:{port}/{database}".format(**postgres)

permissions = Table(
    'permissions', meta,

    Column('id', Integer, primary_key=True),
    Column('permissions', String))

users = Table(
    'users', meta,

    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('surname', String, nullable=False),
    Column('login', String, unique=True),
    Column('birth_date', Date, nullable=False),
    Column('perm_id', Integer, ForeignKey('permissions.id')),
    Column('pass_hash', String, unique=True, index=True)
)


async def set_db(app):
    app['db'] = CRUDMethods(await aiopg.sa.create_engine(dsn=db_url))


async def close_db(app):
    await app['db'].close_db()


class CRUDMethods:
    def __init__(self, engine):
        self.engine = engine
        self.auth_list = None

    async def get_users(self, user_id=None):
        async with self.engine.acquire() as conn:
            if user_id:
                sel = users.select().where(users.c.id == user_id)
            else:
                sel = users.select()

            cursor = await conn.execute(sel)

            return await cursor.fetchall()

    async def created_user(self, param):

        hash_str = self.get_hash_string(param.login, param.password)

        async with self.engine.acquire() as conn:
            cursor = await conn.execute(users.insert().values(
                        name=param.name,
                        surname=param.surname,
                        login=param.login,
                        birth_date=param.birth_date,
                        perm_id=param.perm_id,
                        pass_hash=hash_str
                        ))
            self.auth_list = None

            return await cursor.fetchone()

    async def update_user(self, user_id, param):

        if 'password' in param.keys():
            password = param.pop('password')
            login = (await self.get_users(user_id=user_id))[0]
            param['pass_hash'] = self.get_hash_string(login=login, password=password)

        async with self.engine.acquire() as conn:
            await conn.execute(users.update().where(users.c.id == user_id).values(**param))
            self.auth_list = None

    async def delete_user(self, user_id):
        async with self.engine.acquire() as conn:
            await conn.execute(users.delete().where(users.c.id == user_id))
            self.auth_list = None

    async def get_auth_list(self):
        if self.auth_list is None:
            async with self.engine.acquire() as conn:
                j = users.join(permissions)
                cursor = await conn.execute(select([users.c.pass_hash, permissions.c.permissions]).select_from(j))
                result = await cursor.fetchall()

                self.auth_list = {r.pass_hash: r.permissions for r in result}

        return self.auth_list

    async def get_api_key(self, params):
        hash_str = self.get_hash_string(params.login, params.password)

        async with self.engine.acquire() as conn:
            cursor = await conn.execute(users.select().where(users.c.pass_hash == hash_str))
            return await cursor.fetchone()

    async def close_db(self):
        self.engine.close()
        await self.engine.wait_closed()

    @staticmethod
    def get_hash_string(login, password):

        login_pass_string = f"{login}{password}"
        hash_str = hashlib.md5(login_pass_string.encode()).hexdigest()

        return hash_str
