import pytest


@pytest.mark.anyio
class TestActions:

    @pytest.mark.parametrize(
        "edits, status",
        [
            ({}, 200),
            ({"password": "An0thr$$"}, 422),
            ({"username": "another"}, 404),
        ],
    )
    async def test_auth(self, client, user, auth_json, edits, status):
        # Merge edits
        json = auth_json.copy()
        json.update(edits)

        # Test request
        header_type = {"Content-Type": "application/x-www-form-urlencoded"}
        post = client.post("/actions/token/", data=json, headers=header_type)
        assert post.status_code == status
