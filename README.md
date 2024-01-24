# Auth Service API Documentation

This comprehensive documentation covers all the essential routes for the Auth service, providing a clear guide for developers working with authentication and user management functionalities.

---

## `POST /api/auth/signup`

### Description
Registers a new user in the system. Upon successful registration, the user receives a JWT token for subsequent requests.

### Request Parameters
- **`body` (type `UserSchema`):** Object containing the new user's information.

### Response Parameters
- **`response_model` (type `UserResponse`):** Response object containing information about the created user.
- **`status_code` (status code):** 201 CREATED - Successfully created a new user.

### Dependencies
- **`bt` (type `BackgroundTasks`):** Object for invoking background tasks.
- **`request` (type `Request`):** Object containing request data.
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Check for an existing user with the provided email address in the database.
2. If the user exists, return a conflict (409 CONFLICT) response with a message that the account already exists.
3. Otherwise, hash the user's password for security.
4. Create a new user in the database using the information from the request.
5. Add a background task to send an email to the user with the provided email address, username, and a URL for registration confirmation.
6. Return a response object with the created user.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/signup"

payload = {
  "email": "user@example.com",
  "username": "new_user",
  "password": "secure_password"
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
```

### Notes
Ensure the user's password meets security requirements and that no existing account with the provided email address exists in the system before using this route.

---

## `POST /api/auth/login`

### Description
Authenticates a user in the system and provides JWT tokens for subsequent requests.

### Request Parameters
- **`body` (type `OAuth2PasswordRequestForm`):** Object containing authentication data like email (using `username`) and password.

### Response Parameters
- **`response_model` (type `TokenSchema`):** Response object containing JWT tokens for the user.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Retrieve the user using the email address from the database.
2. Check if the user has confirmed their email address.
3. Verify if the user's account is not blocked by the administrator.
4. Confirm the entered password is correct.
5. Generate JWT token and update the refresh token in the database.
6. Return a response object with the generated tokens.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/login"

payload = {
  "username": "user@example.com",
  "password": "secure_password"
}

response = requests.post(url, data=payload)

print(response.status_code)
print(response.json())
```

### Notes
Ensure that the provided data is correct, and the user has a confirmed email address and is not blocked by the administrator before using this route.

---

## `POST /api/auth//logout`

### Description
Logs the user out of the system and invalidates JWT tokens. After calling this route, the user loses the ability to make requests to the system.

### Request Parameters
- **`credentials` (type `HTTPAuthorizationCredentials`):** Object containing authorization data (refresh token).

### Response Parameters
- **`status_code` (status code):** 200 OK - Successful user logout.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Decode the refresh token and obtain the user's email address.
2. Retrieve the user using the email address from the database.
3. Verify if the refresh token is valid and belongs to the specified user.
4. Set the user status to "inactive," invalidate the tokens, and update the information in the database.
5. Return a response object confirming successful user logout.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/logout"

headers = {
  "Authorization": "Bearer <refresh_token>"
}

response = requests.post(url, headers=headers)

print(response.status_code)
print(response.json())
```

### Notes
Ensure the refresh token is valid and the user is active in the system before using this route.

---

## `GET /api/auth/refresh_token`

### Description
Refreshes JWT tokens. Upon successful invocation, the user receives new access and refresh tokens for subsequent requests.

### Request Parameters
- **`credentials` (type `HTTPAuthorizationCredentials`):** Object containing authorization data (refresh

 token).

### Response Parameters
- **`response_model` (type `TokenSchema`):** Response object containing new JWT tokens for the user.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Decode the refresh token and obtain the user's email address.
2. Retrieve the user using the email address from the database.
3. Verify if the refresh token is valid and belongs to the specified user.
4. Generate a new JWT token and update the refresh token in the database.
5. Return a response object with the newly generated tokens.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/refresh_token"

headers = {
  "Authorization": "Bearer <refresh_token>"
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())
```

### Notes
Ensure the refresh token is valid and the user is active in the system before using this route.

---

## `GET /api/auth/confirmed_email/{token}`

### Description
Confirms the user's email address using a token received in their email after registration.

### Request Parameters
- **`token` (type `str`):** Token used to confirm the email address.

### Response Parameters
- **200 OK:** Successful email confirmation.
- **400 BAD REQUEST:** Error in confirming the email address (e.g., invalid token).

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Obtain the email address from the token.
2. Retrieve the user using the email address from the database.
3. Check if the user exists and if their email address is not already confirmed.
4. Confirm the user's email address in the database.
5. Return a response object confirming successful email confirmation.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/confirmed_email/<token>"

response = requests.get(url)

print(response.status_code)
print(response.json())
```

### Notes
Ensure the email confirmation token is valid and the email address is not already confirmed in the system before using this route.

---

## `POST /api/auth/request_email`

### Description
Sends a repeat email for confirming the user's email address.

### Request Parameters
- **`body` (type `RequestEmail`):** Object containing the user's email address for resending the confirmation email.

### Response Parameters
- **200 OK:** Email for confirming the email address sent successfully.
- **200 OK:** Email address already confirmed, hence email not sent (returns an appropriate message).

### Dependencies
- **`background_tasks` (type `BackgroundTasks`):** Object for invoking background tasks.
- **`request` (type `Request`):** Object containing request data.
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Retrieve the user using the email address from the database.
2. Check if the user's email address is already confirmed.
3. Add a background task to send an email to the user with the specified email address, username, and a URL for registration confirmation.
4. Return a response object confirming successful email sending or a message that the email address is already confirmed.

### Example Usage
```python
import requests

url = "/api/auth/request_email"

payload = {
  "email": "user@example.com"
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
```

### Notes
Ensure that the user exists in the system before using this route.

---

## `POST /api/auth/block_user/{user_id}`

### Description
Changes a user's activity status by blocking or unblocking their account.

### Request Parameters
- **`user_id` (type `int`):** Unique identifier of the user to be blocked or unblocked.
- **`is_active` (type `bool`):** `True` to unblock the user, `False` to block.

### Response Parameters
- **200 OK:** Successfully updated the user's activity status.
- **404 NOT FOUND:** User with the specified `user_id` not found in the system.

### Dependencies
- **`db` (type `AsyncSession = Depends(get_db)`):** Database connection.

### Request Handling
1. Retrieve the user using the unique identifier `user_id` from the database.
2. Verify if the user exists in the system.
3. Change the user's activity status according to the provided `is_active` value.
4. Save the changes in the database.
5. Return a response object confirming successful update of the user's activity status.

### Example Usage
```python
import requests

url = "http://<HOST>/api/auth/block_user/<USER_ID>"

payload = {
  "is_active": False
}

response = requests.post(url, json=payload)

print(response.status_code)
print(response.json())
```

### Notes
Before using this route, ensure that the user with the specified `user_id` exists on the system.