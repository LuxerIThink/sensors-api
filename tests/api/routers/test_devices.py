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
        "edits",
        [
            (
                {
                    "name": "other_name",
                    "is_shared": False,
                }
            ),
        ],
    )
    async def test_edit(self, client, header, device, device_json, edits):
        # Check existence
        record_before = await Device.get(uuid=device["uuid"])

        # Edit
        edit = client.put(f"/devices/{device['uuid']}", headers=header, json=edits)
        assert edit.status_code == 200

        # Merge edits
        edited_json = device_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit.json()
        assert response["uuid"] == device["uuid"]
        assert response["name"] == edited_json["name"]
        assert response["is_shared"] == edited_json["is_shared"]

        # Check difference
        record_after = await Device.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "name": "other_name",
                    "is_shared": False,
                }
            ),
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
    async def test_edit_partially(self, client, header, device, device_json, edits):
        # Check existence
        record_before = await Device.get(uuid=device["uuid"])

        # Edit
        edit_partially = client.patch(
            f"/devices/{device['uuid']}", headers=header, json=edits
        )
        assert edit_partially.status_code == 200

        # Merge edits
        edited_json = device_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit_partially.json()
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
        assert response["uuid"] is not None
        assert response["name"] is not None
        assert response["is_shared"] is not None

        # Check existence
        get_after = client.get(f"/devices/?uuid={device['uuid']}", headers=header)
        assert get_after.json() == []

    async def test_get_all(self, client, header):
        # Preparations
        devices_json = [
            {
                "name": "test_device",
                "is_shared": True,
            },
            {
                "name": "other_device",
                "is_shared": True,
            },
            {
                "name": "other_name",
                "is_shared": False,
            },
        ]
        for device_json in devices_json:
            create = client.post("/devices/", headers=header, json=device_json)
            assert create.status_code == 200

        # Check quantity
        get = client.get("/devices/", headers=header)
        assert get.status_code == 200
        assert len(get.json()) == 3

    async def test_get_by_name(self, client, header):
        # Preparations
        devices_json = [
            {
                "name": "test_device",
                "is_shared": True,
            },
            {
                "name": "other_device",
                "is_shared": True,
            },
            {
                "name": "other_name",
                "is_shared": False,
            },
        ]
        for device_json in devices_json:
            create = client.post("/devices/", headers=header, json=device_json)
            assert create.status_code == 200

        # Check quantity
        get = client.get(f"/devices/?name={devices_json[0]['name']}", headers=header)
        assert get.status_code == 200
        assert len(get.json()) == 1

    async def test_get_by_name_partially(self, client, header):
        # Preparations
        devices_json = [
            {
                "name": "test_device",
                "is_shared": True,
            },
            {
                "name": "other_device",
                "is_shared": True,
            },
            {
                "name": "other_name",
                "is_shared": False,
            },
        ]
        for device_json in devices_json:
            create = client.post("/devices/", headers=header, json=device_json)
            assert create.status_code == 200

        # Check quantity
        get = client.get(f"/devices/?name=device", headers=header)
        assert get.status_code == 200
        assert len(get.json()) == 2

    async def test_get_by_is_shared(self, client, header):
        # Preparations
        devices_json = [
            {
                "name": "test_device",
                "is_shared": True,
            },
            {
                "name": "other_device",
                "is_shared": True,
            },
            {
                "name": "other_name",
                "is_shared": False,
            },
        ]
        for device_json in devices_json:
            create = client.post("/devices/", headers=header, json=device_json)
            assert create.status_code == 200

        # Check quantity
        get = client.get(f"/devices/?is_shared=True", headers=header)
        assert get.status_code == 200
        assert len(get.json()) == 2

    async def test_get_not_shared(self, client, header, header2):
        # Preparations
        device_json = {
            "name": "test_device",
            "is_shared": False,
        }
        create = client.post("/devices/", headers=header, json=device_json)
        assert create.status_code == 200

        # Get by other user
        get = client.get(f"/devices/?uuid={create.json()["uuid"]}", headers=header2)
        assert get.status_code == 200
        assert get.json() == []

    async def test_get_all_not_shared(self, client, header, header2):
        # Preparations
        device_json = {
            "name": "test_device",
            "is_shared": False,
        }
        create = client.post("/devices/", headers=header, json=device_json)
        assert create.status_code == 200

        # Get by other user
        get = client.get(f"/devices/", headers=header2)
        assert get.status_code == 200
        assert get.json() == []

    async def test_get_shared(self, client, header, header2):
        # Preparations
        device_json = {
            "name": "test_device",
            "is_shared": True,
        }
        create = client.post("/devices/", headers=header, json=device_json)
        assert create.status_code == 200

        # Get by other user
        get = client.get(f"/devices/?uuid={create.json()["uuid"]}", headers=header2)
        assert get.status_code == 200
        assert get.json() == [create.json()]

    async def test_get_all_shared(self, client, header, header2):
        # Preparations
        device_json = {
            "name": "test_device",
            "is_shared": True,
        }
        create = client.post("/devices/", headers=header, json=device_json)
        assert create.status_code == 200

        # Get by other user
        get = client.get(f"/devices/", headers=header2)
        assert get.status_code == 200
        assert get.json() == []
