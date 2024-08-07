import pytest
from app.models import Sensor


@pytest.mark.anyio
class TestSensors:

    async def test_create(self, client, device, header, sensor_json):
        # Check existence
        get = client.get("/sensors/", headers=header)
        assert get.json() == []

        # Create
        create = client.post(
            f"/sensors/{device['uuid']}", headers=header, json=sensor_json
        )
        assert create.status_code == 200

        # Check response
        response = create.json()
        assert response["uuid"]
        assert response["name"] == sensor_json["name"]
        assert response["unit"] == sensor_json["unit"]

        # Check record
        record = await Sensor.filter(uuid=response["uuid"]).first()
        assert record.name == sensor_json["name"]
        assert record.unit == sensor_json["unit"]

    async def test_get(self, client, header, sensor, sensor_json):
        # Get
        get = client.get(f"/sensors/?uuid={sensor['uuid']}", headers=header)
        assert get.status_code == 200

        # Check response
        response = get.json()[0]
        assert response["uuid"]
        assert response["name"] == sensor_json["name"]
        assert response["unit"] == sensor_json["unit"]

    @pytest.mark.parametrize(
        "sensor2_json",
        [
            (
                {
                    "name": "other_name",
                    "unit": "other_unit",
                }
            ),
        ],
    )
    async def test_multiple_get(self, client, header, device, sensor, sensor2_json):
        # Add second object
        create1 = client.post(
            f"/sensors/{device['uuid']}", headers=header, json=sensor2_json
        )
        assert create1.status_code == 200

        # Check quantity
        response_get = client.get("/sensors/", headers=header)
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "name": "other_name",
                    "unit": "other_device",
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
                    "unit": "other_device",
                }
            ),
        ],
    )
    async def test_edit(self, client, header, sensor, sensor_json, edits):
        # Check existence
        record_before = await Sensor.get(uuid=sensor["uuid"])

        # Edit
        put = client.put(f"/sensors/{sensor["uuid"]}", headers=header, json=edits)
        assert put.status_code == 200

        # Merge edits
        edited_json = sensor_json.copy()
        edited_json.update(edits)

        # Check response
        response = put.json()
        assert response["uuid"] == sensor["uuid"]
        assert response["name"] == edited_json["name"]
        assert response["unit"] == edited_json["unit"]

        # Check difference
        record_after = await Sensor.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

    async def test_remove(self, client, header, sensor):
        # Remove
        delete = client.delete(f"/sensors/{sensor['uuid']}", headers=header)
        assert delete.status_code == 200

        # Check response
        response_put_json = delete.json()
        assert response_put_json["uuid"]
        assert response_put_json["name"]
        assert response_put_json["unit"]

        # Check existence
        get_after = client.get(f"/sensors/?uuid={sensor['uuid']}", headers=header)
        assert get_after.json() == []
