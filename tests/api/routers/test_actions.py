import pytest


@pytest.mark.anyio
class TestActions:
    async def test_correct_login_in(self, client, correct_user_data):
        client.post("/users/", json=correct_user_data)
        login_data = {
            key: value for key, value in correct_user_data.items() if key != "email"
        }
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post("/actions/token/", data=login_data, headers=header)
        assert response.status_code == 200

    async def test_not_existing_login_in(self, client, correct_user_data):
        login_data = {
            key: value for key, value in correct_user_data.items() if key != "email"
        }
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post("/actions/token/", data=login_data, headers=header)
        assert response.status_code == 404
