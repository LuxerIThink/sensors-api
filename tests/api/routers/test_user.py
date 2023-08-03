import pytest
from argon2 import PasswordHasher
from api.models.user import User


@pytest.mark.anyio
class TestUser:

    @pytest.mark.parametrize(
        "data, status, keywords",
        [
            # Correct
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                200,
                [],
            ),
            # Incorrects
            # Lengths
            # too long username > 32 chars
            (
                {
                    "username": "33_chars_basic_incorrect_username",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                422,
                ["username", "32"],
            ),
            # Too short username < 3 chars
            (
                {
                    "username": "2c",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                422,
                ["username", "3"],
            ),
            # Password
            # Empty password
            (
                {
                    "username": "username",
                    "password": "",
                    "email": "email@xyz.com",
                },
                422,
                ["password"],
            ),
            # Too short password
            (
                {
                    "username": "username2",
                    "password": "7_Chars",
                    "email": "email@xyz.com",
                },
                422,
                ["password", "8"],
            ),
            # No digits in password
            (
                {
                    "username": "username",
                    "password": "No_Numbers",
                    "email": "email@xyz.com",
                },
                422,
                ["password", "digit"],
            ),
            # No upper cases in password
            (
                {
                    "username": "username",
                    "password": "0_upper_cases",
                    "email": "email@xyz.com",
                },
                422,
                ["password", "uppercase"],
            ),
            # No special chars in password
            (
                {
                    "username": "username",
                    "password": "0Specials",
                    "email": "email@xyz.com",
                },
                422,
                ["password", "special"],
            ),
            # Email
            # No @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "eee",
                },
                422,
                ["email", "@"],
            ),
            # No text after @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "XYZ@",
                },
                422,
                ["email", "@", "after"],
            ),
            # No text before @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "@xyz.com",
                },
                422,
                ["email", "@", "before"],
            ),
            # No domain in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "xyz@xyz",
                },
                422,
                ["email", "@", "after"],
            ),
        ],
    )
    async def test_create(self, client, data, status, keywords):
        response = client.post("/users/", json=data)
        assert response.status_code == status
        match status:
            case 422:
                assert all(keyword in str(response.json()) for keyword in keywords)
            case 200:
                password_hasher = PasswordHasher()

                user = await User.filter(username=data["username"]).first()
                output_data = response.json()

                # Check json input with api output
                assert output_data["uuid"]
                assert output_data["username"] == data["username"]
                assert "password" not in output_data
                assert output_data["email"] == data["email"]

                # Check json input with db data
                assert user.username == data["username"]
                assert user.email == data["email"]
                assert user.password != data["password"]
                assert password_hasher.verify(user.password, data["password"]) is True

    @pytest.mark.parametrize(
        "data1, data2, keywords",
        [
            # By username
            (
                {
                    "username": "username",
                    "password": "Pa$Sw0rd",
                    "email": "email@xyz.com",
                },
                {
                    "username": "username",
                    "password": "P4S$word",
                    "email": "xyz@email.com",
                },
                ["username"],
            ),
            # By email
            (
                {
                    "username": "username1",
                    "password": "P4$Sw0rd",
                    "email": "email@xyz.com",
                },
                {
                    "username": "username2",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                ["email"],
            ),
            # By email check chars sizes
            (
                {
                    "username": "username3",
                    "password": "P4$Sw0rd",
                    "email": "email@xyz.com",
                },
                {
                    "username": "username4",
                    "password": "P4S$VVord",
                    "email": "Email@xyz.com",
                },
                ["email"],
            ),
        ],
    )
    async def test_create_existing_user(self, client, data1, data2, keywords):
        client.post("/users/", json=data1)
        response = client.post("/users/", json=data2)
        assert response.status_code == 422
        assert [keyword in str(response.json()) for keyword in keywords]

    async def test_get_correct(self, client, create_header):
        response = client.get("/users/", headers=create_header)
        assert response.status_code == 200

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
    async def test_get_incorrect(self, client, header, keywords):
        response = client.get("/users/", headers=header)
        assert response.status_code == 422
        assert all(keyword in str(response.json()) for keyword in keywords)

    @pytest.mark.parametrize(
        "edited_user, status",
        [
            (
                {
                    "username": "other_name",
                    "password": "N0th1ng!",
                    "email": "other_mail@mail.xyz",
                },
                200,
            ),
            # Incorrects
            # Lengths
            # too long username > 32 chars
            (
                {
                    "username": "33_chars_basic_incorrect_username",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # Too short username < 3 chars
            (
                {
                    "username": "2c",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # Password
            # Empty password
            (
                {
                    "username": "username",
                    "password": "",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # Too short password
            (
                {
                    "username": "username2",
                    "password": "7_Chars",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # No digits in password
            (
                {
                    "username": "username",
                    "password": "No_Numbers",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # No upper cases in password
            (
                {
                    "username": "username",
                    "password": "0_upper_cases",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # No special chars in password
            (
                {
                    "username": "username",
                    "password": "0Specials",
                    "email": "email@xyz.com",
                },
                422,
            ),
            # Email
            # No @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "eee",
                },
                422,
            ),
            # No text after @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "XYZ@",
                },
                422,
            ),
            # No text before @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "@xyz.com",
                },
                422,
            ),
            # No domain in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "xyz@xyz",
                },
                422,
            ),
        ],
    )
    async def test_edit(self, client, create_header, user_data, edited_user, status):
        old_user = await User.get(email=user_data["email"])
        response = client.put("/users/", headers=create_header, json=edited_user)
        assert response.status_code == status
        match status:
            case 200:
                new_user = await User.get(email=edited_user["email"])
                new_user_json = response.json()
                assert old_user.uuid == new_user.uuid
                assert new_user_json["username"] == edited_user["username"]
                assert old_user.password != new_user.password
                assert new_user_json["email"] == edited_user["email"]

    async def test_remove(self, client, create_header):
        response_get_before = client.get("/users/", headers=create_header)
        assert response_get_before.status_code == 200
        response_delete = client.delete("/users/", headers=create_header)
        assert response_delete.status_code == 200
        response_get_after = client.get("/users/", headers=create_header)
        assert response_get_after.status_code == 404
