# Rating Service API Documentation

This comprehensive documentation covers essential routes for the Rating service, providing a clear guide for developers working with image rating functionalities.

---

## `POST /publications/{publication_id}/rating/add`

### Description
Adds a new rating for a specific image publication. Users can submit ratings for images, and the service ensures that users cannot rate their own publications.

### Request Parameters
- **`publication_id` (type `int`):** Unique identifier for the image publication.
- **`body` (type `RatingCreate`):** Object containing the rating information.

### Response Parameters
- **`response_model` (type `RatingResponse`):** Response object containing information about the added rating.
- **`status_code` (status code):** 201 CREATED - Successfully added a new rating.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.
- **`user` (type `User = Depends(auth_service.get_current_user)`):** Current user making the rating.

### Request Handling
1. Retrieve the specified image publication from the database.
2. Check if the publication exists; otherwise, raise a 404 NOT FOUND error.
3. Ensure that the user making the rating is not the owner of the publication; otherwise, raise a 403 FORBIDDEN error.
4. Attempt to add the rating to the database.
5. If the user has already voted for the publication, raise a 400 BAD REQUEST error.
6. Return the added rating in the response.

### Example Usage
```python
import requests

url = "http://<HOST>/publications/<publication_id>/rating/add"

payload = {
  "value": 5
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
```

### Notes
Ensure the user is not the owner of the image publication and has not already voted before using this route.

---

## `GET /publications/{publication_id}/rating/users`

### Description
Retrieves users who have rated a specific image publication. This route is accessible to all roles, but if the user is an admin, moderator, or the image owner, any user's ratings can be accessed.

### Request Parameters
- **`publication_id` (type `int`):** Unique identifier for the image publication.
- **`limit` (type `int`, default 10):** Maximum number of users to retrieve (between 10 and 500).
- **`offset` (type `int`, default 0):** Offset for pagination.

### Response Parameters
- **`response_model` (type `list[UserResponse]`):** List of users who have rated the specified image publication.
- **`status_code` (status code):** 200 OK - Successfully retrieved user ratings.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.
- **`user` (type `User = Depends(auth_service.get_current_user)`):** Current user making the request.

### Request Handling
1. Check the role of the user making the request.
2. If the user is not a regular user, replace the user with the publication owner to retrieve all user ratings.
3. Retrieve the specified image publication from the database.
4. Check if the publication exists; otherwise, raise a 404 NOT FOUND error.
5. Retrieve users who have rated the publication based on the publication's ratings.
6. Return the list of users who have rated the publication.

### Example Usage
```python
import requests

url = "http://<HOST>/publications/<publication_id>/rating/users"

response = requests.get(url)

print(response.status_code)
print(response.json())
```

### Notes
Accessible to all roles, but users with elevated roles can access any user's ratings for the specified image publication.

---

## `GET /admin/users/{user_id}/ratings`

### Description
Retrieves all ratings submitted by a specific user. This route is accessible only to admins and moderators.

### Request Parameters
- **`user_id` (type `int`):** Unique identifier for the user whose ratings are being retrieved.
- **`limit` (type `int`, default 10):** Maximum number of ratings to retrieve (between 10 and 500).
- **`offset` (type `int`, default 0):** Offset for pagination.

### Response Parameters
- **`response_model` (type `list[RatingResponse]`):** List of ratings submitted by the specified user.
- **`status_code` (status code):** 200 OK - Successfully retrieved user ratings.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.
- **`user` (type `User = Depends(auth_service.get_current_user)`):** Current user making the request (admin or moderator).

### Request Handling
1. Check if the user making the request is an admin or moderator; otherwise, raise a 403 FORBIDDEN error.
2. Retrieve all ratings submitted by the specified user from the database.
3. Return the list of ratings submitted by the user.

### Example Usage
```python
import requests

url = "http://<HOST>/admin/users/<user_id>/ratings"

response = requests.get(url)

print(response.status_code)
print(response.json())
```

### Notes
Accessible only to admins and moderators. Retrieves all ratings submitted by the specified user.

---

## `DELETE /publications/{publication_id}/ratings/{user_id}/delete`

### Description
Deletes a rating submitted by a specific user for a particular image publication. This route is accessible only to admins and moderators.

### Request Parameters
- **`publication_id` (type `int`):** Unique identifier for the image publication.
- **`user_id` (type `int`):** Unique identifier for the user whose rating is being deleted.

### Response Parameters
- **`status_code` (status code):** 204 NO CONTENT - Successfully deleted the specified rating.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.
- **`user` (type `User = Depends(auth_service.get_current_user)`):** Current user making the request (admin or moderator).

### Request Handling
1. Check if the user making the request is an admin or moderator; otherwise, raise a 403 FORBIDDEN error.
2. Attempt to delete the specified rating from the database.
3. If the rating is not found, raise a 404 NOT FOUND error.
4. Return a 204 NO CONTENT response upon successful deletion.

### Example Usage
```python
import requests

url = "http://<HOST>/publications/<publication_id>/ratings/<user_id>/delete"

response = requests.delete(url)

print(response.status_code)
```

### Notes
Accessible only to admins and moderators. Deletes the specified rating for the specified image publication.