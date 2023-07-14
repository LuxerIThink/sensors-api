import pytest
from api.models.user import User


@pytest.mark.anyio
class TestCreateUserAPI:

    @pytest.mark.parametrize("input_data", [
        ({
            "username": "correct_username",
            "password": "C0r_pass",
            "email": "email@xyz.com"
        })
    ])
    async def test_create_user(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 200

        output_data = response.json()
        self._check_output_with_input(output_data, input_data)
        await self._check_password_hashed(input_data['username'], input_data['password'])

    @staticmethod
    def _check_output_with_input(output_data, input_data):
        assert output_data['uuid']
        assert output_data['username'] == input_data['username']
        assert 'password' not in output_data
        assert output_data['email'] == input_data['email']

    @staticmethod
    async def _check_password_hashed(username, password):
        user = await User.filter(username=username).first()
        assert user.password != password

    @pytest.mark.parametrize("input_data", [
        ({
            "username": "username",
            "password": "",
            "email": "xyz@xyz.com"
        })
    ])
    async def assert_existing_user(self, client, input_data):
        client.post("/users/", json=input_data)
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422

    @pytest.mark.parametrize("input_data", [
        ({
            "username": "33_chars_basic_incorrect_username",
            "password": "Passw0r!",
            "email": "ccc@xyz.pl"
        }),
        ({
            "username": "2c",
            "password": "Passw0r!",
            "email": "zzz@xyz.pl"
        })
    ])
    async def test_incorrect_data_lengths(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422

    # Incorrect lengths
    incorrect_data = {
        "username": "lx",
        "password": "password",
        "email": "x@y"
    }

    response = client.post("/users/", json=incorrect_data)
    assert response.status_code == 422



