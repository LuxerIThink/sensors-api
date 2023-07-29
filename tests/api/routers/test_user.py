import pytest
from argon2 import PasswordHasher
from api.models.user import User


@pytest.mark.anyio
class TestUser:
    async def test_create_correct(self, client, correct_user_data):
        response = client.post("/users/", json=correct_user_data)
        output_data = response.json()
        user = await User.filter(username=correct_user_data["username"]).first()
        password_hasher = PasswordHasher()

        # Check api response status coe
        assert response.status_code == 200

        # Check json input with api output
        assert output_data["uuid"]
        assert output_data["username"] == correct_user_data["username"]
        assert "password" not in output_data
        assert output_data["email"] == correct_user_data["email"]

        # Check json input with db data
        assert user.username == correct_user_data["username"]
        assert user.email == correct_user_data["email"]
        assert user.password != correct_user_data["password"]
        assert (
            password_hasher.verify(user.password, correct_user_data["password"]) is True
        )

    @pytest.mark.parametrize(
        "input1, input2, keywords",
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
    async def test_create_existing_user(self, client, input1, input2, keywords):
        client.post("/users/", json=input1)
        response = client.post("/users/", json=input2)
        assert response.status_code == 422
        assert [keyword in str(response.json()) for keyword in keywords]

    @pytest.mark.parametrize(
        "input_data, keywords",
        [
            # Lengths
            # too long username > 32 chars
            (
                {
                    "username": "33_chars_basic_incorrect_username",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
                ["username", "32"],
            ),
            # Too short username < 3 chars
            (
                {
                    "username": "2c",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                },
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
                ["password"],
            ),
            # Too short password
            (
                {
                    "username": "username2",
                    "password": "7_Chars",
                    "email": "email@xyz.com",
                },
                ["password", "8"],
            ),
            # No digits in password
            (
                {
                    "username": "username",
                    "password": "No_Numbers",
                    "email": "email@xyz.com",
                },
                ["password", "digit"],
            ),
            # No upper cases in password
            (
                {
                    "username": "username",
                    "password": "0_upper_cases",
                    "email": "email@xyz.com",
                },
                ["password", "uppercase"],
            ),
            # No special chars in password
            (
                {
                    "username": "username",
                    "password": "0Specials",
                    "email": "email@xyz.com",
                },
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
                ["email", "@"],
            ),
            # No text after @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "XYZ@",
                },
                ["email", "@", "after"],
            ),
            # No text before @ in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "@xyz.com",
                },
                ["email", "@", "before"],
            ),
            # No domain in email
            (
                {
                    "username": "username",
                    "password": "P4S$VVord",
                    "email": "xyz@xyz",
                },
                ["email", "@", "after"],
            ),
        ],
    )
    async def test_create_incorrect(self, client, input_data, keywords):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422
        assert all(keyword in str(response.json()) for keyword in keywords)

    async def test_get_correct(self, client, correct_token):
        header = {"Authorization": correct_token}
        response = client.get("/users/", headers=header)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "token, keywords",
        [
            (
                "Bearer eyJhbGciOiAiSFMyNTYiLCAid"
                "HlwIjogIkpXVCJ9.eyJ1c2VyX2lkIjog"
                "MTIzNDU2LCAiZXhwIjogMTY3OTcxMzYw"
                "MH0.PZJlhhRLP-I4KJKu3uWls6D2_sWm"
                "3WfVD9H09VzgXe0",
                ["verification", "failed"],
            ),
        ],
    )
    async def test_get_incorrect(self, client, token, keywords):
        header = {"Authorization": token}
        response = client.get("/users/", headers=header)
        assert response.status_code == 422
        assert all(keyword in str(response.json()) for keyword in keywords)
