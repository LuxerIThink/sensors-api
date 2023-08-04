import pytest
from api.models.user import User


@pytest.mark.anyio
class TestActions:

    @pytest.fixture(scope="function")
    def header(self):
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        return header

    async def test_login(self, client, user, auth_json, header):
        response = client.post("/actions/token/", data=auth_json, headers=header)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "edit_json, status",
        [
            ({"password": "An0thr$$"}, 422),
            ({"username": "another"}, 404),
        ],
    )
    async def test_wrong_creditals(
        self, client, user, auth_json, edit_json, status, header
    ):
        # Check is auth_json and edit_json are not the same
        for key, value in edit_json.items():
            if auth_json[key] == value:
                raise Exception(f"[{key}: {value}]: are the same, is incorrect")
        # Create new merged auth_json and edit_json
        new_json = auth_json.copy()
        new_json.update(edit_json)
        # Test
        response = client.post("/actions/token/", data=new_json, headers=header)
        assert response.status_code == status
