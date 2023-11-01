import pytest
from app.models import Device


@pytest.mark.anyio
class TestDevice:
    @pytest.fixture(scope="session")
    def edited_device(self):
        return {
            "name": "other_name",
            "is_shared": True,
        }

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
        response = client.get("/devices/" + device["uuid"], headers=auth_header)
        assert response.status_code == 200

        output_data = response.json()[0]

        assert output_data["uuid"]
        assert output_data["name"] == device_json["name"]
        assert output_data["is_shared"] == device_json["is_shared"]

    async def test_edit(self, client, auth_header, device, device_json, edited_device):
        response_before_edit = client.get("/devices/" + device["uuid"], headers=auth_header)
        if response_before_edit.status_code != 200:
            raise Exception("Device not exist, but it should")

        old_device_json = response_before_edit.json()[0]
        old_device = await Device.get(uuid=old_device_json["uuid"])

        response = client.put("/devices/" + old_device_json["uuid"], headers=auth_header, json=edited_device)
        assert response.status_code == 200

        new_device_json = response.json()

        new_device = await Device.get(uuid=new_device_json["uuid"])

        assert old_device.uuid == new_device.uuid
        assert new_device_json["name"] == edited_device["name"]
        assert new_device_json["is_shared"] == edited_device["is_shared"]

    async def test_remove(self, client, auth_header, device, device_json):
        response_before = client.get("/devices/" + device["uuid"], headers=auth_header)
        if response_before.status_code != 200:
            raise Exception("Device not exist, but it should")

        # Remove request
        response_delete = client.delete("/devices/" + device["uuid"], headers=auth_header)
        assert response_delete.status_code == 200

        # Check user existence after remove
        response_get_after = client.get("/users/" + device["uuid"], headers=auth_header)
        assert response_get_after.status_code == 404