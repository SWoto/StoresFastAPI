import asyncio
import unittest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from core.configs import settings
from schemas.users import PlainUserSchema
from core.auth import check_password
from core.database import Session, engine
from create_tables import create_tables
from models import UsersModel
import models


FAILURE_CONTRUCT_ARGUMENT = "The {} after creation does not equal the constructor argument."


class BaseTest(unittest.IsolatedAsyncioTestCase):
    data_in = {
        "email": "testing@vscode.cl",
        "document": "60:qwe:11:82:1d:2e",
        "first_name": "Jacklyn",
        "sur_name": "Christiansen",
        "admin": True,
        'password': 'amendoim@#$',
    }

    @classmethod
    def setUpClass(cls):
        # Set up class, synchronously
        pass

    async def asyncSetUp(self):
        print("Creating all data tables...")

        async with engine.begin() as conn:
            await conn.run_sync(settings.DBBaseModel.metadata.create_all)
        print("Tables created")

    async def asyncTearDown(self):
        print("Deleting all data tables...")

        async with engine.begin() as conn:
            await conn.run_sync(settings.DBBaseModel.metadata.drop_all)
        print("Tables deleted")

    async def test_query(self):
        db: AsyncSession = Session()
        user = UsersModel(**BaseTest.data_in)
        async with db as session:

            session.add(user)
            await session.commit()

        await db.close()
