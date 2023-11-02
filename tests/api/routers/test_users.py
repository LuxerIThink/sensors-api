import pytest
from argon2 import PasswordHasher
from app.models.user import User


@pytest.mark.anyio
class TestUser:

    @pytest.fixture(scope="session")
    def password_hasher(self):
        password_hasher = PasswordHasher()
        return password_hasher

    async def test_create(self, client):
        # Input json
        user_json = {
            "username": "username",
            "password": "Pa$Sw0rd",
            "email": "email@xyz.com",
        }

        # Preparations
        password_hasher = PasswordHasher()

        # Create new user
        response = client.post("/users/", json=user_json)
        assert response.status_code == 200

        # Get data
        response_json = response.json()
        user = await User.get(username=user_json["username"])

        # Check input -> db
        assert user_json["username"] == user.username
        assert user_json["password"] != user.password
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert response_json["email"].lower() == user.email

        # Check db -> output
        assert str(user.uuid) == response_json["uuid"]
        assert user.username == response_json["username"]
        assert "password" not in response_json
        assert user.email == user_json["email"].lower()

    async def test_get(self, client, auth_header, password_hasher, user_json):
        # Get actual user
        response = client.get("/users/", headers=auth_header)
        assert response.status_code == 200

        # Get data
        response_json = response.json()
        user = await User.get(username=user_json["username"])

        # Check input -> db
        assert user_json["username"] == user.username
        assert user_json["password"] != user.password
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert response_json["email"].lower() == user.email

        # Check db -> output
        assert str(user.uuid) == response_json["uuid"]
        assert user.username == response_json["username"]
        assert "password" not in response_json
        assert user.email == user_json["email"].lower()

    async def test_edit(self, client, auth_header, password_hasher, user_json):
        # Input data
        new_user_json = {
            "username": "other_name",
            "password": "N0th1ng!",
            "email": "other_mail@mail.xyz",
        }

        # Check is base user data and other user data are not the same
        for key, value in new_user_json.items():
            if user_json[key] == value:
                raise Exception(f"[{key}: {value}]: are the same, but they shouldn't")

        # Check user existence
        response_get_before = client.get("/users/", headers=auth_header)
        if response_get_before.status_code != 200:
            raise Exception("User not exist, but it should")

        # Get user before edit
        old_user = await User.get(email=user_json["email"].lower())

        # Edit user request
        response = client.put("/users/", headers=auth_header, json=new_user_json)
        assert response.status_code == 200

        # Get data
        response_json = response.json()
        user = await User.get(email=new_user_json["email"].lower())

        # Check UUID
        assert old_user.uuid == user.uuid

        # Check output data
        assert response_json["uuid"] == str(user.uuid)
        assert response_json["username"] == new_user_json["username"]
        assert "password" not in response_json
        assert response_json["email"] == new_user_json["email"].lower()

        # Check input with db
        assert user.username == new_user_json["username"]
        assert user.password != new_user_json["password"]
        assert password_hasher.verify(user.password, new_user_json["password"]) is True
        assert user.email == new_user_json["email"].lower()

    async def test_remove(self, client, auth_header):
        # Check user existence before remove
        response_get_before = client.get("/users/", headers=auth_header)
        assert response_get_before.status_code == 200

        # Remove request
        response_delete = client.delete("/users/", headers=auth_header)
        assert response_delete.status_code == 200

        # Check user existence after remove
        response_get_after = client.get("/users/", headers=auth_header)
        assert response_get_after.status_code == 404

    @pytest.mark.parametrize(
        "edit_json, keywords",
        [
            # Lengths
            # too long username > 32 chars
            (
                {"username": "33_chars_basic_incorrect_username"},
                ["username", "32"],
            ),
            # Too short username < 3 chars
            (
                {"username": "2c"},
                ["username", "3"],
            ),
            # Password
            # Empty password
            (
                {"password": ""},
                ["password"],
            ),
            # Too short password
            (
                {"password": "7_Chars"},
                ["password", "8"],
            ),
            # No digits in password
            (
                {"password": "No_Numbers"},
                ["password", "digit"],
            ),
            # No upper cases in password
            (
                {"password": "0_upper_cases"},
                ["password", "uppercase"],
            ),
            # No special chars in password
            (
                {"password": "0Specials"},
                ["password", "special"],
            ),
            # Email
            # No @ in email
            (
                {"email": "eee"},
                ["email", "@"],
            ),
            # No text after @ in email
            (
                {"email": "XYZ@"},
                ["email", "@", "after"],
            ),
            # No text before @ in email
            (
                {"email": "@xyz.com"},
                ["email", "@", "before"],
            ),
            # No domain in email
            (
                {"email": "xyz@xyz"},
                ["email", "@", "after"],
            ),
        ],
    )
    async def test_validators(self, client, auth_header, user_json, edit_json, keywords):
        # Create new merged created_json and edit_json
        new_json = user_json.copy()
        new_json.update(edit_json)

        # Check is create_json and edit_json are not the same
        for key, value in edit_json.items():
            if user_json[key] == value:
                raise Exception(f"[{key}: {value}]: are the same, is incorrect")

        # Test edit
        response_put = client.put("/users/", headers=auth_header, json=new_json)
        assert response_put.status_code == 422
        assert all(keyword in str(response_put.json()) for keyword in keywords)

        # Remove user
        response_delete = client.delete("/users/", headers=auth_header)
        if response_delete.status_code != 200:
            raise Exception("User not deleted, but it should")

        # Test create
        response_post = client.post("/users/", json=new_json)
        assert response_post.status_code == 422
        # Check response message
        assert all(keyword in str(response_post.json()) for keyword in keywords)

    @pytest.mark.parametrize(
        "edit_json, keywords",
        [
            # By username and email
            (
                {},
                ["username", "email", "duplicate"],
            ),
            # By username
            (
                {"email": "email@xyz.com"},
                ["username", "duplicate"],
            ),
            # By email
            (
                {"username": "username2"},
                ["email", "duplicate"],
            ),
            # By email different char sizes
            (
                {
                    "username": "username4",
                    "email": "Email@xyz.com",
                },
                ["email", "duplicate"],
            ),
        ],
    )
    async def test_create_existing_user(self, client, user_json, edit_json, keywords):
        # Create new merged create_json and edit_json
        new_json = user_json.copy()
        new_json.update(edit_json)
        response_first = client.post("/users/", json=user_json)

        # Create first user
        assert response_first.status_code == 200

        # Test creating the same user
        response = client.post("/users/", json=new_json)
        assert response.status_code == 422
        # Check response message
        assert [keyword in str(response.json()) for keyword in keywords]

    @pytest.mark.parametrize(
        "header, keywords",
        [
            (
                {
                    "Authorization": "Bearer eyJhbGciOiAiSFMyNTYiLCAid"
                    "HlwIjogIkpXVCJ9.eyJ1c2VyX2lkIjog"
                    "MTIzNDU2LCAiZXhwIjogMTY3OTcxMzYw"
                    "MH0.PZJlhhRLP-I4KJKu3uWls6D2_sWm"
                    "3WfVD9H09VzgXe0"
                },
                ["verification", "failed"],
            ),
        ],
    )
    async def test_wrong_token(self, client, header, keywords):
        response = client.get("/users/", headers=header)
        assert response.status_code == 422
        # Check response message
        assert all(keyword in str(response.json()) for keyword in keywords)
