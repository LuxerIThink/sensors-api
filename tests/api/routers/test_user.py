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

    @pytest.mark.parametrize("input_data", [
        ({
            "username": "username1",
            "password": "",
            "email": "yyy@xyz.pl"
        }),
        ({
            "username": "username2",
            "password": "7_Chars",
            "email": "xyz@xyz.com"
        }),
        ({
            "username": "username3",
            "password": "No_Numbers",
            "email": "xyz@xyz.net"
        }),
        ({
            "username": "username4",
            "password": "0_upper_cases",
            "email": "xyz@zyx.pl"
        }),
        ({
            "username": "username5",
            "password": "0Specials",
            "email": "xyz@mail.com"
        }),
    ])
    async def test_incorrect_password(self, client, input_data):
        response = client.post("/users/", json=input_data)
        assert response.status_code == 422




