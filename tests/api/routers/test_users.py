import pytest
from argon2 import PasswordHasher
from app.models.user import User


@pytest.mark.anyio
class TestUser:
    @pytest.fixture(scope="session")
    def edited_user(self):
        return {
            "username": "other_name",
            "password": "N0th1ng!",
            "email": "other_mail@mail.xyz",
        }

    async def test_create(self, client, user_json):
        # Create new user
        response = client.post("/users/", json=user_json)
        assert response.status_code == 200

        # Check json input with app output
        output_data = response.json()
        assert output_data["uuid"]
        assert output_data["username"] == user_json["username"]
        assert "password" not in output_data
        assert output_data["email"] == user_json["email"]

        # Check json input with db data
        password_hasher = PasswordHasher()
        user = await User.filter(username=user_json["username"]).first()
        assert user.username == user_json["username"]
        assert user.email == user_json["email"].lower()
        assert user.password != user_json["password"]
        assert password_hasher.verify(user.password, user_json["password"]) is True

    async def test_get(self, client, auth_header):
        response = client.get("/users/", headers=auth_header)
        assert response.status_code == 200

    async def test_edit(self, client, auth_header, user_json, edited_user):
        # Check user existence
        response_get_before = client.get("/users/", headers=auth_header)
        if response_get_before.status_code != 200:
            raise Exception("User not exist, but it should")

        # Get user before edit
        old_user = await User.get(email=user_json["email"])

        # Edit user request
        response = client.put("/users/", headers=auth_header, json=edited_user)
        assert response.status_code == 200

        # Get user after edit
        new_user = await User.get(email=edited_user["email"])
        new_user_json = response.json()

        # Compare data before and after put
        assert old_user.uuid == new_user.uuid
        assert new_user_json["username"] == edited_user["username"]
        assert old_user.password != new_user.password
        assert new_user_json["email"] == edited_user["email"]

    async def test_remove(self, client, auth_header):
        # Check user existence before remove
        response_get_before = client.get("/users/", headers=auth_header)
        if response_get_before.status_code != 200:
            raise Exception("User not exist, but it should")

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
        # Check is create_json and edit_json are not the same
        for key, value in edit_json.items():
            if user_json[key] == value:
                raise Exception(f"[{key}: {value}]: are the same, is incorrect")

        # Create new merged created_json and edit_json
        new_json = user_json.copy()
        new_json.update(edit_json)

        # Test edit
        response_put = client.put("/users/", headers=auth_header, json=new_json)
        assert response_put.status_code == 422
        assert all(keyword in str(response_put.json()) for keyword in keywords)

        # Remove user
        response_delete = client.delete("/users/", headers=auth_header)
        if response_delete.status_code != 200:
            raise Exception("User not deleted")

        # Test create
        response_post = client.post("/users/", json=new_json)
        assert response_post.status_code == 422
        assert all(keyword in str(response_post.json()) for keyword in keywords)

    @pytest.mark.parametrize(
        "edit_json, keywords",
        [
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
        if response_first.status_code != 200:
            raise Exception("User not exist, but it should")

        # Test
        response = client.post("/users/", json=new_json)
        assert response.status_code == 422
        assert [keyword in str(response.json()) for keyword in keywords]

    @pytest.mark.parametrize(
        "header, status, keywords",
        [
            (
                {
                    "Authorization": "Bearer eyJhbGciOiAiSFMyNTYiLCAid"
                    "HlwIjogIkpXVCJ9.eyJ1c2VyX2lkIjog"
                    "MTIzNDU2LCAiZXhwIjogMTY3OTcxMzYw"
                    "MH0.PZJlhhRLP-I4KJKu3uWls6D2_sWm"
                    "3WfVD9H09VzgXe0"
                },
                422,
                ["verification", "failed"],
            ),
        ],
    )
    async def test_wrong_token(self, client, header, status, keywords):
        response = client.get("/users/", headers=header)
        assert response.status_code == status
        assert all(keyword in str(response.json()) for keyword in keywords)
