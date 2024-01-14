import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.users import get_user_by_email


@pytest.mark.asyncio
async def test_get_user_by_email():
    # Test case 1: Test with a valid email
    email = "test@example.com"
    db = AsyncSession()
    result = await get_user_by_email(email, db)
    assert result is not None

    # Test case 2: Test with a non-existent email
    email = "nonexistent@example.com"
    db = AsyncSession()
    result = await get_user_by_email(email, db)
    assert result is None

    # Test case 3: Test with an empty email
    email = ""
    db = AsyncSession()
    result = await get_user_by_email(email, db)
    assert result is None

