import pytest
from argon2 import PasswordHasher
from app.models.user import User


@pytest.mark.anyio
class TestUser:

    async def test_create(self, client, user_json):
        # Check are there any records
        get = client.get("/users/")
        assert get.status_code == 401

        # Create
        create = client.post("/users/", json=user_json)
        assert create.status_code == 200

        # Check response
        response = create.json()
        assert response["uuid"]
        assert response["username"] == user_json["username"]
        assert "password" not in response
        assert response["email"] == user_json["email"].lower()

        # Check db record
        user = await User.get(uuid=response["uuid"])
        assert user.username == user_json["username"]
        assert user.password != user_json["password"]
        password_hasher = PasswordHasher()
        assert password_hasher.verify(user.password, user_json["password"]) is True
        assert user.email == user_json["email"].lower()

    async def test_get(self, client, header, user_json):
        # Get
        get = client.get("/users/", headers=header)
        assert get.status_code == 200

        # Check response
        response = get.json()
        assert response["uuid"]
        assert response["username"] == user_json["username"]
        assert "password" not in user_json["password"]
        assert response["email"] == user_json["email"].lower()

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "username": "other_name",
                    "password": "N0th1ng!",
                    "email": "other_mail@mail.com",
                }
            ),
        ],
    )
    async def test_edit(self, client, header, user, user_json, edits):
        # Check existence
        record_before = await User.get(uuid=user["uuid"])

        # Edit
        edit = client.put("/users/", headers=header, json=edits)
        assert edit.status_code == 200

        # Merge edits
        edited_json = user_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit.json()
        assert response["uuid"] == user["uuid"]
        assert response["username"] == edited_json["username"]
        assert "password" not in response
        assert response["email"] == edited_json["email"].lower()

        # Check difference
        record_after = await User.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

        # Check record
        assert record_after.password != edited_json["password"]
        password_hasher = PasswordHasher()
        assert (
            password_hasher.verify(record_after.password, edited_json["password"])
            is True
        )
        assert record_after.email == edited_json["email"].lower()

    @pytest.mark.parametrize(
        "edits",
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
                    "password": "0th3rP4$$",
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
        ],
    )
    async def test_edit_partially(self, client, header, user, user_json, edits):
        # Check existence
        record_before = await User.get(uuid=user["uuid"])

        # Edit
        edit_partially = client.patch("/users/", headers=header, json=edits)
        assert edit_partially.status_code == 200

        # Merge edits
        edited_json = user_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit_partially.json()
        assert response["uuid"] == user["uuid"]
        assert response["username"] == edited_json["username"]
        assert "password" not in response
        assert response["email"] == edited_json["email"].lower()

        # Check difference
        record_after = await User.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

        # Check record
        assert record_after.password != edited_json["password"]
        password_hasher = PasswordHasher()
        assert (
            password_hasher.verify(record_after.password, edited_json["password"])
            is True
        )
        assert record_after.email == edited_json["email"].lower()

    async def test_remove(self, client, header, user_json):
        # Remove
        delete = client.delete("/users/", headers=header)
        assert delete.status_code == 200

        # Check response
        response = delete.json()
        assert response["uuid"]
        assert response["username"]
        assert "password" not in response
        assert response["email"]

        # Check existence
        get_after = client.get("/users/", headers=header)
        assert get_after.status_code == 404

    @pytest.mark.parametrize(
        "edits, keys",
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
    async def test_validators(self, client, header, user_json, edits, keys):
        # Edit partially
        patch = client.patch("/users/", headers=header, json=edits)
        assert patch.status_code == 422
        assert all(key in str(patch.json()) for key in keys)

        # Edit to default
        edit_to_default = client.put("/users/", headers=header, json=user_json)
        assert edit_to_default.status_code == 200

        # Merge edits
        edited_json = user_json.copy()
        edited_json.update(edits)

        # Try to edit
        edit = client.put("/users/", headers=header, json=edited_json)
        assert edit.status_code == 422
        assert all(key in str(edit.json()) for key in keys)

        # Remove
        delete = client.delete("/users/", headers=header)
        assert delete.status_code == 200

        # Try to create
        post = client.post("/users/", json=edited_json)
        assert post.status_code == 422
        assert all(key in str(post.json()) for key in keys)

    @pytest.mark.parametrize(
        "edits, keys",
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
    async def test_create_again(self, client, user, user_json, edits, keys):
        # Merge edits
        edited_json = user_json.copy()
        edited_json.update(edits)

        # Try to create again
        create_same = client.post("/users/", json=edited_json)
        assert create_same.status_code == 422
        assert [key in str(create_same.json()) for key in keys]

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "uuid": "xD",
                }
            ),
        ],
    )
    async def test_edit_uuid(self, client, header, user_json, edits):
        edit = client.put("/users/", headers=header, json=edits)
        assert edit.status_code == 422

    @pytest.mark.parametrize(
        "header, keys",
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
    async def test_wrong_token(self, client, header, keys):
        get = client.get("/users/", headers=header)
        assert get.status_code == 422
        assert all(key in str(get.json()) for key in keys)
