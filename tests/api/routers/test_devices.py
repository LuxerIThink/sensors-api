import pytest
from app.models import Device


@pytest.mark.anyio
class TestDevice:

    async def test_create(self, client, auth_header, device_json):
        # Create new device
        response = client.post("/devices/", headers=auth_header, json=device_json)
        assert response.status_code == 200

        # Check json input with app output
        output_data = response.json()
        assert output_data["uuid"]
        assert output_data["name"] == device_json["name"]
        assert output_data["is_shared"] == device_json["is_shared"]

        # Check json input with db data
        user = await Device.filter(name=device_json["name"]).first()
        assert user.name == device_json["name"]
        assert user.is_shared == device_json["is_shared"]

    async def test_get(self, client, auth_header, device, device_json):
        response = client.get("/devices/" + "?uuid=" + device["uuid"], headers=auth_header)
        assert response.status_code == 200

        output_data = response.json()[0]

        assert output_data["uuid"]
        assert output_data["name"] == device_json["name"]
        assert output_data["is_shared"] == device_json["is_shared"]

    @pytest.mark.parametrize(
        "edits_json",
        [
            (
                    {
                        "name": "other_name",
                        "is_shared": False,
                    }
            ),
        ]
    )
    async def test_multiple_get(self, client, auth_header, device, device_json, edits_json):
        client.post("/devices/", headers=auth_header, json=edits_json)

        response = client.get("/devices/", headers=auth_header)
        assert response.status_code == 200

        device1 = response.json()[0]

        assert device1["uuid"]
        assert device1["name"] == device_json["name"]
        assert device1["is_shared"] == device_json["is_shared"]

        device2 = response.json()[1]

        assert device2["uuid"]
        assert device2["name"] == edits_json["name"]
        assert device2["is_shared"] == edits_json["is_shared"]

    @pytest.mark.parametrize(
        "edits_json",
        [
            (
                {
                    "name": "other_name",
                    "is_shared": False,
                }
            ),
            # Check partialy change
            (
                {
                    "name": "other",
                }
            ),
            (
                {
                    "is_shared": False,
                }
            ),
        ]
    )
    async def test_edit(self, client, auth_header, device, device_json, edits_json):
        expected_device_json = device_json.copy()
        expected_device_json.update(edits_json)

        response = client.put("/devices/" + device["uuid"], headers=auth_header, json=edits_json)
        assert response.status_code == 200
        response_json = response.json()

        assert response_json["uuid"] == device["uuid"]
        assert response_json["name"] == expected_device_json["name"]
        assert response_json["is_shared"] == expected_device_json["is_shared"]

    async def test_remove(self, client, auth_header, device, device_json):
        response_before = client.get("/devices/" + device["uuid"], headers=auth_header)
        assert response_before.status_code == 200

        # Remove request
        response_delete = client.delete("/devices/" + device["uuid"], headers=auth_header)
        assert response_delete.status_code == 200

        # Check user existence after remove
        response_get_after = client.get("/users/" + device["uuid"], headers=auth_header)
        assert response_get_after.status_code == 404