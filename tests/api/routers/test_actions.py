import pytest


@pytest.mark.anyio
class TestActions:
    async def test_correct_login_in(self, client, correct_user, correct_user_data):
        correct_user_data.pop("email")
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post(
            "/actions/token/", data=correct_user_data, headers=header
        )
        assert response.status_code == 200

    async def test_not_existing_login_in(self, client, correct_user_data):
        correct_user_data.pop("email")
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = client.post(
            "/actions/token/", data=correct_user_data, headers=header
        )
        assert response.status_code == 404
