from models import permissions, users, db_url, meta
from sqlalchemy import create_engine
import datetime


def sample_data():
    conn = engine.connect()
    conn.execute(permissions.insert(), [
                 {'id': 1, 'permissions': 'admin'},
                 {'id': 2, 'permissions': 'read'},
                 {'id': 3, 'permissions': 'blocked'}]
                 )

    conn.execute(users.insert().values(
        name='admin',
        surname='admin',
        login='admin',
        birth_date=datetime.date(1970, 1, 1),
        perm_id=1,
        pass_hash='f6fdffe48c908deb0f4c3bd36c032e72'
    ))

    conn.close()


if __name__ == '__main__':
    engine = create_engine(db_url, echo=True)
    meta.drop_all(engine)
    meta.create_all(engine)
    sample_data()
