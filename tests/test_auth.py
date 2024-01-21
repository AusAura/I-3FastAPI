import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import UserSchema
from src.database.models import User
from src.repositories.users import count_users, create_user, get_user_by_email, update_token, confirmed_email


class TestAsyncUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)

    async def test_create_user(self):
        # Test case 1: Creating first user, role should be 'admin'
        body = UserSchema(username="test", email="test@example.com.ua", password="testtest", about='something')
        with patch('src.repositories.users.count_users', return_value=0) as mock_count:
            mock_count.return_value = 0
            result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        assert result.role == 'admin'

        # Test case 2: Creating second user, role should be 'user'
        body = UserSchema(username="test2", email="test@example.com.ua", password="testtest", about='something')
        with patch('src.repositories.users.count_users', return_value=1) as mock_count:
            mock_count.return_value = 1
            result = await create_user(body, self.session)
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        assert result.role == 'user'

    async def test_get_user_by_email(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True, avatar="test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await get_user_by_email(user.email, self.session)
        self.assertEqual(result.email, "test@example.com.ua")

    async def test_update_token(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True, avatar="test"
        )
        user.refresh_token = "token_test"

        await update_token(user, "token_test", self.session)
        self.assertEqual(user.refresh_token, "token_test")

    async def test_confirmed_email(self):
        user = User(
            id=1, username="test2", password="testtest", email="test@example.com.ua", confirmed=True, avatar="test"
        )
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        user.confirmed = False
        await confirmed_email(user.email, self.session)

        self.assertEqual(user.confirmed, True)

    async def test_count_users(self):
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        self.session.execute.return_value = mock_result
        count = await count_users(self.session)
        assert count == 42
