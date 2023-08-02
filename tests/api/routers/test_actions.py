import pytest


@pytest.mark.anyio
class TestActions:
    async def test_correct_login_in(self, client, create_user, user_data):
        user_data.pop("email")
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post("/actions/token/", data=user_data, headers=header)
        assert response.status_code == 200

    async def test_not_existing_login_in(self, client, user_data):
        user_data.pop("email")
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post("/actions/token/", data=user_data, headers=header)
        assert response.status_code == 404
