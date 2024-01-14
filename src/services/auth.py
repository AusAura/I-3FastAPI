from src.repositories.comments import dummy_user

class Auth:
    def get_current_user(self):
        return dummy_user

auth_service = Auth()