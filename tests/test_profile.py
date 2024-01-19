import unittest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserSchema
from src.database.models import User, Publication
from src.repositories.profile import update_avatar_url, update_username, update_about, count_user_publications, \
    count_usage_days, get_user_by_username


class TestAsyncUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)

    async def test_update_avatar_url(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True,
            avatar="avatar_test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_avatar_url(user.avatar, "avatar_test", self.session)
        self.assertEqual(user.avatar, "avatar_test")

    async def test_update_username(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True,
            avatar="avatar_test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_username(user, "test3", self.session)
        self.assertEqual(user.username, "test3")

    async def test_update_about(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True,
            avatar="avatar_test", about="about_test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        await update_about(user, "about_test_2", self.session)
        self.assertEqual(user.about, "about_test_2")

    async def test_count_user_publications(self):
        publication = Publication(id=1, title="test1", description="description1", user_id=1)

        mocked_publication = MagicMock()
        mocked_publication.scalar.return_value = 1
        self.session.execute.return_value = mocked_publication
        result = await count_user_publications(publication.user_id, self.session)
        self.assertEqual(result, 1)

    async def test_count_usage_days(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True,
            avatar="avatar_test", created_at=datetime.now()
        )
        mocked_user = MagicMock()
        mocked_user.scalar.return_value = user
        self.session.execute.return_value = mocked_user
        result = await count_usage_days(user.created_at, self.session)
        self.assertEqual(result, 0)

    async def test_get_user_by_username(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True,
            avatar="avatar_test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_username(user.username, self.session)
        self.assertEqual(result.username, "test2")
