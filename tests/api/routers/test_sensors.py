import pytest
from app.models import Sensor


@pytest.mark.anyio
class TestSensors:

    async def test_create(self, client, device, auth_header, sensor_json):
        # Create new device
        response = client.post("/sensors/" + device["uuid"], headers=auth_header, json=sensor_json)
        assert response.status_code == 200

        # Check json input with app output
        response_json = response.json()
        assert response_json["uuid"]
        assert response_json["name"] == sensor_json["name"]
        assert response_json["unit"] == sensor_json["unit"]

        # Check json input with db data
        db_record = await Sensor.filter(name=sensor_json["name"]).first()
        assert db_record.name == sensor_json["name"]
        assert db_record.unit == sensor_json["unit"]

    async def test_get(self, client, auth_header, sensor, sensor_json):
        response = client.get("/sensors/" + "?uuid=" + sensor["uuid"], headers=auth_header)
        assert response.status_code == 200

        output_data = response.json()[0]

        assert output_data["uuid"]
        assert output_data["name"] == sensor_json["name"]
        assert output_data["unit"] == sensor_json["unit"]

    @pytest.mark.parametrize(
        "edits_json",
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
        ]
    )
    async def test_edit(self, client, auth_header, sensor, sensor_json, edits_json):
        expected_device_json = sensor_json.copy()
        expected_device_json.update(edits_json)

        response = client.put("/sensors/" + sensor["uuid"], headers=auth_header, json=edits_json)
        assert response.status_code == 200
        response_json = response.json()

        assert response_json["uuid"] == sensor["uuid"]
        assert response_json["name"] == expected_device_json["name"]
        assert response_json["unit"] == expected_device_json["unit"]

    async def test_remove(self, client, auth_header, sensor):
        response = client.get("/sensors/" + "?uuid=" + sensor["uuid"], headers=auth_header)
        assert response.status_code == 200

        # Remove request
        response_delete = client.delete("/sensors/" + sensor["uuid"], headers=auth_header)
        assert response_delete.status_code == 200

        # Check user existence after remove
        response_get_after = client.get("/sensors/" + sensor["uuid"], headers=auth_header)
        assert response_get_after.status_code == 405
