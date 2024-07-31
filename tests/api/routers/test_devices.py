import pytest
from app.models import Device


@pytest.mark.anyio
class TestDevice:

    async def test_create(self, client, header, device_json):
        # Check existence
        get = client.get("/devices/", headers=header)
        assert get.json() == []

        # Create
        create = client.post("/devices/", headers=header, json=device_json)
        assert create.status_code == 200

        # Check response
        response = create.json()
        assert response["uuid"]
        assert response["name"] == device_json["name"]
        assert response["is_shared"] == device_json["is_shared"]

        # Check record
        record = await Device.filter(uuid=response["uuid"]).first()
        assert record.name == device_json["name"]
        assert record.is_shared == device_json["is_shared"]

    async def test_get(self, client, header, device, device_json):
        # Get
        get = client.get(f"/devices/?uuid={device['uuid']}", headers=header)
        assert get.status_code == 200

        # Check response
        response = get.json()[0]
        assert response["uuid"]
        assert response["name"] == device_json["name"]
        assert response["is_shared"] == device_json["is_shared"]

    @pytest.mark.parametrize(
        "device2_json",
        [
            (
                {
                    "name": "other_name",
                    "is_shared": False,
                }
            ),
        ],
    )
    async def test_multiple_get(self, client, header, device, device2_json):
        # Add second record
        create2 = client.post("/devices/", headers=header, json=device2_json)
        assert create2.status_code == 200

        # Check quantity
        get = client.get("/devices/", headers=header)
        assert get.status_code == 200
        assert len(get.json()) == 2

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "name": "other_name",
                    "is_shared": False,
                }
            ),
            # Check partially change
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
        ],
    )
    async def test_edit(self, client, header, device, device_json, edits):
        # Check existence
        record_before = await Device.get(uuid=device["uuid"])

        # Edit
        put = client.put(f"/devices/{device['uuid']}", headers=header, json=edits)
        assert put.status_code == 200

        # Merge edits
        edited_json = device_json.copy()
        edited_json.update(edits)

        # Check response
        response = put.json()
        assert response["uuid"] == device["uuid"]
        assert response["name"] == edited_json["name"]
        assert response["is_shared"] == edited_json["is_shared"]

        # Check difference
        record_after = await Device.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

    async def test_remove(self, client, header, device):
        # Remove
        delete = client.delete(f"/devices/{device['uuid']}", headers=header)
        assert delete.status_code == 200

        # Check response
        response = delete.json()
        assert response["uuid"]
        assert response["name"]
        assert response["is_shared"]

        # Check existence
        get_after = client.get(f"/devices/?uuid={device['uuid']}", headers=header)
        assert get_after.json() == []
