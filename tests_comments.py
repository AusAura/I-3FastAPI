import pytest
from httpx import AsyncClient
from main import app
from src.database.models import *
from src.schemas.comments import *

from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.comments import *

from src.database.db import get_db, sessionmanager
import datetime
import asyncio

# now = '2024-01-13 19:52:25.934 +0200'
# now = datetime.datetime.now()
now = datetime.datetime(year=2022, month=12, day=12, hour=12, minute=12, second=12, microsecond=12, tzinfo=datetime.timezone.utc) ## + datetime.timezone(datetime.timedelta(hours=3))
# print(now)

@pytest.mark.asyncio
async def test_add_comment():
    async with sessionmanager.session() as session:
        # Test adding comment to own publication
        user = User(id=9) # Replace with appropriate user object
        db = session # Replace with appropriate db session object
        comment_body = CommentModel(text="This is a test comment", created_at=str(now), updated_at=str(now))
        publication_id = 4 # Replace with appropriate publication id
        comment = await add_comment(publication_id, user, comment_body, db)
        assert comment.user_id == user.id
        assert comment.publication_id == publication_id
        assert comment.text == comment_body.text
        assert comment.created_at is not None
        assert comment.updated_at is not None

@pytest.mark.asyncio
async def test_edit_comment():
    async with sessionmanager.session() as session:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test case for admin user
            response = await client.delete("/1/comments/1/delete", headers={"Authorization": "Bearer admin_token"})
            assert response.status_code == 200
            assert response.json() == {'comment': 'deleted_comment', 'detail': 'Comment successfully deleted'}
            
            # Test case for non-admin user
            response = await client.delete("/1/comments/1/delete", headers={"Authorization": "Bearer user_token"})
            assert response.status_code == 403
            
            # Test case for non-existing comment
            response = await client.delete("/1/comments/999/delete", headers={"Authorization": "Bearer admin_token"})
            assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_comments():
    async with sessionmanager.session() as session:
        # Test case 1: Test with valid publication ID, skip and limit
        publication_id = 1
        skip = 0
        limit = 10
        db = session
        result = await get_comments(publication_id, skip, limit, db)
        assert len(result) == limit

        # Test case 2: Test with negative skip value
        publication_id = 1
        skip = -1
        limit = 10
        db = session
        with pytest.raises(Exception):
            await get_comments(publication_id, skip, limit, db)

        # Test case 3: Test with limit greater than available comments
        publication_id = 1
        skip = 0
        limit = 100
        db = session
        result = await get_comments(publication_id, skip, limit, db)
        assert len(result) <= limit

@pytest.mark.asyncio
async def test_get_comment():
    async with sessionmanager.session() as session:
        # Test case for existing comment
        comment_id = 1
        db = session
        result = await get_comment(comment_id, db)
        assert isinstance(result, Comment)

        # Test case for non-existing comment
        comment_id = 999
        result = await get_comment(comment_id, db)
        assert result is None

        # Test case for different comment id
        comment_id = 2
        result = await get_comment(comment_id, db)
        assert isinstance(result, Comment)

        # Test case for different comment id
        comment_id = 3
        result = await get_comment(comment_id, db)
        assert isinstance(result, Comment)

@pytest.mark.asyncio
async def test_delete_comment():
    async with sessionmanager.session() as session:
        # Mock the database session
        db = MagicMock(spec=AsyncSession)

        # Create a mock user
        user = User(id=1)

        # Create a mock comment
        comment = Comment(id=1, user_id=user.id)

        # Set up the mock database session to return the mock comment
        db.execute.return_value.scalar_one_or_none.return_value = comment

        # Call the delete_comment function with the mock comment, user, and database session
        result = await delete_comment(comment_id=1, current_user=user, db=db)

        # Assert that the comment was deleted
        db.delete.assert_called_once_with(comment)
        db.commit.assert_called_once()

        # Assert that the result is the deleted comment
        assert result == comment

@pytest.mark.asyncio
async def test_delete_comment_no_comment():
    async with sessionmanager.session() as session:
        # Mock the database session
        db = MagicMock(spec=AsyncSession)

        # Create a mock user
        user = User(id=1)

        # Set up the mock database session to return None
        db.execute.return_value.scalar_one_or_none.return_value = None

        # Call the delete_comment function with a non-existent comment id, user, and database session
        result = await delete_comment(comment_id=1, current_user=user, db=db)

        # Assert that the comment was not deleted
        db.delete.assert_not_called()
        db.commit.assert_not_called()

        # Assert that the result is None
        assert result is None
