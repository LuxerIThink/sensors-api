import pytest
from app.models import Measurement
from datetime import datetime


@pytest.mark.anyio
class TestMeasurement:

    async def test_create(self, client, sensor, auth_header, measurement_json):
        # Create new device
        response = client.post("/measurements/" + sensor["uuid"], headers=auth_header, json=measurement_json)
        assert response.status_code == 200

        # Check json input with app output
        response_json = response.json()
        assert response_json["uuid"]
        assert response_json["time"] == measurement_json["time"]
        assert response_json["value"] == measurement_json["value"]

    async def test_get(self, client, auth_header, measurement, measurement_json):
        response = client.get("/measurements/" + "?uuid=" + measurement["uuid"], headers=auth_header)
        assert response.status_code == 200

        response_json = response.json()[0]

        assert response_json["uuid"]
        assert response_json["time"] == measurement_json["time"]
        assert response_json["value"] == measurement_json["value"]

    @pytest.mark.parametrize(
        "edits_json",
        [
            (
                {
                    "time": "2020-07-30T14:48:00Z",
                    "value": 1.0,
                }
            ),
            # Check partially change
            (
                {
                    "time": "2019-05-30T10:42:00Z",
                }
            ),
            (
                {
                    "value": -6,
                }
            ),
        ]
    )
    async def test_edit(self, client, auth_header, measurement, measurement_json, edits_json):
        expected_device_json = measurement_json.copy()
        expected_device_json.update(edits_json)

        response = client.put("/measurements/" + measurement["uuid"], headers=auth_header, json=edits_json)
        assert response.status_code == 200
        response_json = response.json()

        assert response_json["uuid"] == measurement["uuid"]
        assert response_json["time"] == expected_device_json["time"]
        assert response_json["value"] == expected_device_json["value"]

    async def test_remove(self, client, auth_header, measurement):
        response = client.get("/measurements/" + "?uuid=" + measurement["uuid"], headers=auth_header)
        assert response.status_code == 200

        # Remove request
        response_delete = client.delete("/measurements/" + measurement["uuid"], headers=auth_header)
        assert response_delete.status_code == 200

        # Check user existence after remove
        response_get_after = client.get("/measurements/" + measurement["uuid"], headers=auth_header)
        assert response_get_after.status_code == 405
