import pytest


@pytest.mark.anyio
class TestActions:
    @pytest.mark.parametrize(
        "input_data",
        [
            (
                {
                    "username": "username",
                    "password": "Pa$Sw0rd",
                    "email": "email@xyz.com",
                }
            ),
        ],
    )
    async def test_login_in(self, client, input_data):
        client.post("/users/", json=input_data)
        login_data = {
            "grant_type": "password",
            "username": input_data["username"],
            "password": input_data["password"],
        }

        header = {"Content-Type": "application/x-www-form-urlencoded"}

        response = client.post("/actions/token/", data=login_data, headers=header)

        assert response.status_code == 200

    async def test_not_existing_login_in(self, client, correct_user_data):
        login_data = {key: value for key, value in correct_user_data.items() if key != "email"}
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post("/actions/token/", data=login_data, headers=header)
        assert response.status_code == 404
