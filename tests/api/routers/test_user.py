import pytest
from api.models.user import User


@pytest.mark.anyio
class TestCreateUserAPI:
    @pytest.mark.parametrize(
        "input_data",
        [
            (
                {
                    "username": "username",
                    "password": "Pa$Sw0rd",
                    "email": "email@xyz.com",
                }
            )
        ],
    )
    async def test_create_user(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "input_data",
        [
            (
                {
                    "username": "username",
                    "password": "Pa$Sw0rd",
                    "email": "email@xyz.com",
                }
            )
        ],
    )
    async def test_create_user(self, client, input_data):
        response = client.post("/users/", json=input_data)
        output_data = response.json()
        assert output_data["uuid"]
        assert output_data["username"] == input_data["username"]
        assert "password" not in output_data
        assert output_data["email"] == input_data["email"]

    @pytest.mark.parametrize(
        "input_data",
        [
            (
                {
                    "username": "username",
                    "password": "Pa$Sw0rd",
                    "email": "email@xyz.com",
                }
            )
        ],
    )
    async def test_is_password_hashed(self, client, input_data):
        client.post("/users/", json=input_data)
        user = await User.filter(username=input_data["username"]).first()
        assert user.password != input_data["password"]

    @pytest.mark.parametrize(
        "input_data1, input_data2",
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
            ),
        ],
    )
    async def test_create_existing_user(self, client, input_data1, input_data2):
        client.post("/users/", json=input_data1)
        response = client.post("/users/", json=input_data2)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "input_data",
        [
            # too long username > 32 chars
            (
                {
                    "username": "33_chars_basic_incorrect_username",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com",
                }
            ),
            # Too short username < 3 chars
            (
                {
                    "username": "2c",
                    "password": "P4S$VVord",
                    "email": "email@xyz.com"
                }
            ),
        ],
    )
    async def test_incorrect_data_lengths(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "input_data",
        [
            # Empty password
            (
                {
                    "username": "username",
                    "password": "",
                    "email": "email@xyz.com"
                }
            ),
            # Too short password
            ({"username": "username2", "password": "7_Chars", "email": "xyz@xyz.com"}),
            # No numbers in password
            (
                {
                    "username": "username",
                    "password": "No_Numbers",
                    "email": "email@xyz.com"
                }
            ),
            # No upper cases in password
            (
                {
                    "username": "username",
                    "password": "0_upper_cases",
                    "email": "email@xyz.com"
                }
            ),
            # No special chars in password
            (
                {
                    "username": "username",
                    "password": "0Specials",
                    "email": "email@xyz.com"
                }
            ),
        ],
    )
    async def test_incorrect_password(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422
