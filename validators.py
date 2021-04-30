from pydantic import BaseModel


class Auth(BaseModel):
    login: str
    password: str


class CreateUser(BaseModel):
    name: str
    surname: str
    login: str
    password: str
    birth_date: str
    perm_id: int

    class Config:
        extra = 'forbid'


class UpdateUser(BaseModel):
    name: str = None
    surname: str = None
    password: str = None
    birth_date: str = None
    perm_id: int = None

    class Config:
        extra = 'forbid'
