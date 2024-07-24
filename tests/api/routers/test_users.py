import pytest
from argon2 import PasswordHasher
from app.models.user import User


@pytest.mark.anyio
class TestUser:

    @pytest.fixture(scope="session")
    def password_hasher(self):
        password_hasher = PasswordHasher()
        return password_hasher

    async def test_create(self, client, password_hasher, user_json):
        # Create user
        response = client.post("/users/", json=user_json)
        assert response.status_code == 200
        response_json = response.json()

        # Get user from db
        user = await User.get(uuid=response_json["uuid"])

        # Check input json with db
        assert user_json["username"] == user.username
        assert user_json["password"] != user.password
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert user_json["email"].lower() == user.email

        # Check response json with db
        assert response_json["uuid"] == str(user.uuid)
        assert response_json["username"] == user.username
        assert "password" not in response_json
        assert response_json["email"] == user.email

    async def test_get(self, client, password_hasher, auth_header, user_json):
        # Get user
        response = client.get("/users/", headers=auth_header)
        assert response.status_code == 200
        response_json = response.json()

        # Get user from db
        user = await User.get(uuid=response_json["uuid"])

        # Check input json with db
        assert user_json["username"] == user.username
        assert user_json["password"] != user.password
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert user_json["email"].lower() == user.email

        # Check response json with db
        assert response_json["uuid"] == str(user.uuid)
        assert response_json["username"] == user.username
        assert "password" not in response_json
        assert response_json["email"] == user.email

    @pytest.mark.parametrize(
        "edits_json",
        [
            (
                {
                    "username": "other_name",
                    "password": "N0th1ng!",
                    "email": "other_mail@mail.com",
                }
            ),
            (
                {
                    "username": "other_username",
                }
            ),
            (
                {
                    "password": "0th3rP4$$",
                }
            ),
            (
                {
                    "email": "new_mail@mail.com",
                }
            ),
        ]
    )
    async def test_edit(self, client, password_hasher, auth_header, user_json, edits_json):
        # Merge default json with edits
        expected_user_json = user_json.copy()
        expected_user_json.update(edits_json)

        # Check user existence before edit
        response_before = client.get("/users/", headers=auth_header)

        # Get user from db before edit
        user_before = await User.get(uuid=response_before.json()["uuid"])

        # Edit user
        response = client.put("/users/", headers=auth_header, json=edits_json)
        assert response.status_code == 200
        response_json = response.json()

        # Get user from db after edit
        user = await User.get(uuid=response_json["uuid"])

        # Check UUID before and after edit
        assert user_before.uuid == user.uuid

        # Check input json with db
        assert expected_user_json["username"] == user.username
        assert expected_user_json["password"] != user.password
        assert password_hasher.verify(user.password, expected_user_json["password"]) is True
        assert expected_user_json["email"].lower() == user.email

        # Check response json with db
        assert response_json["uuid"] == str(user.uuid)
        assert response_json["username"] == user.username
        assert "password" not in response_json
        assert response_json["email"] == user.email

    async def test_remove(self, client, password_hasher, auth_header, user_json):
        # Check user existence before remove
        response_before = client.get("/users/", headers=auth_header)
        assert response_before.status_code == 200

        # Get user from db
        user = await User.get(uuid=response_before.json()["uuid"])

        # Remove user
        response_delete = client.delete("/users/", headers=auth_header)
        assert response_delete.status_code == 200
        response_json = response_delete.json()

        # Check input json with db
        assert user_json["username"] == user.username
        assert user_json["password"] != user.password
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert user_json["email"].lower() == user.email

        # Check response json with db
        assert response_json["uuid"] == str(user.uuid)
        assert response_json["username"] == user.username
        assert "password" not in response_json
        assert response_json["email"] == user.email

        # Try to get user after remove
        response_get_after = client.get("/users/", headers=auth_header)
        assert response_get_after.status_code == 404

    @pytest.mark.parametrize(
        "edits_json, keywords",
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
    async def test_validators(self, client, auth_header, user_json, edits_json, keywords):

        # Merge default json with edits
        edited_user_json = user_json.copy()
        edited_user_json.update(edits_json)

        # Try to edit user
        response_put = client.put("/users/", headers=auth_header, json=edited_user_json)
        assert response_put.status_code == 422
        # Check response message
        assert all(keyword in str(response_put.json()) for keyword in keywords)

        # Remove user
        response_delete = client.delete("/users/", headers=auth_header)
        assert response_delete.status_code == 200

        # Try to create user
        response_post = client.post("/users/", json=edited_user_json)
        assert response_post.status_code == 422
        # Check response message
        assert all(keyword in str(response_post.json()) for keyword in keywords)

    @pytest.mark.parametrize(
        "edits_json, keywords",
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
    async def test_create_existing_user(self, client, user_json, edits_json, keywords):
        # Merge default json with edits
        edited_user_json = user_json.copy()
        edited_user_json.update(edits_json)

        # Create first user
        response_first = client.post("/users/", json=user_json)
        assert response_first.status_code == 200

        # Try to create the user with same data second time
        response = client.post("/users/", json=edited_user_json)
        assert response.status_code == 422
        # Check response message
        assert [keyword in str(response.json()) for keyword in keywords]

    @pytest.mark.parametrize(
        "edits_json",
        [
            (
                {
                    "uuid": "xD",
                }
            ),
        ]
    )
    async def test_edit_uuid(self, client, password_hasher, auth_header, user_json, edits_json):
        # Check user existence before edit
        response_before = client.get("/users/", headers=auth_header)

        # Edit user
        response = client.put("/users/", headers=auth_header, json=edits_json)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "auth_header, keywords",
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
    async def test_wrong_token(self, client, auth_header, keywords):
        # Try to get user
        response = client.get("/users/", headers=auth_header)
        assert response.status_code == 422
        # Check response message
        assert all(keyword in str(response.json()) for keyword in keywords)
