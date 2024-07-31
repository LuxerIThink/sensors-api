import pytest
from app.models import Measurement


@pytest.mark.anyio
class TestMeasurement:

    async def test_create(self, client, sensor, header, measurement_json):
        # Check existence
        get = client.get("/measurements/", headers=header)
        assert get.json() == []

        # Create
        create = client.post(
            f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
        )
        assert create.status_code == 200

        # Check response
        response = create.json()
        assert response["uuid"]
        assert response["time"] == measurement_json["time"]
        assert response["value"] == measurement_json["value"]

        # Check record
        record = await Measurement.get(uuid=response["uuid"])
        assert record.time.strftime("%Y-%m-%dT%H:%M:%SZ") == measurement_json["time"]
        assert record.value == measurement_json["value"]

    async def test_get(self, client, header, measurement, measurement_json):
        # Get
        get = client.get(f"/measurements/?uuid={measurement['uuid']}", headers=header)
        assert get.status_code == 200

        # Check response
        response_get_json = get.json()[0]
        assert response_get_json["uuid"]
        assert response_get_json["time"] == measurement_json["time"]
        assert response_get_json["value"] == measurement_json["value"]

    @pytest.mark.parametrize(
        "measurement2_json",
        [
            (
                {
                    "time": "1999-01-01T00:00:00Z",
                    "value": -15,
                }
            ),
        ],
    )
    async def test_multiple_get(
        self, client, header, sensor, measurement, measurement2_json
    ):
        # Add second object
        create2 = client.post(
            f"/measurements/{sensor['uuid']}", headers=header, json=measurement2_json
        )
        assert create2.status_code == 200

        # Check record quantity
        response_get = client.get("/measurements/", headers=header)
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    @pytest.mark.parametrize(
        "edits",
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
        ],
    )
    async def test_edit(self, client, header, measurement, measurement_json, edits):
        # Check existence
        record_before = await Measurement.get(uuid=measurement["uuid"])

        # Edit
        put = client.put(
            f"/measurements/{measurement['uuid']}", headers=header, json=edits
        )
        assert put.status_code == 200

        # Merge edits
        edited_json = measurement_json.copy()
        edited_json.update(edits)

        # Check response
        response = put.json()
        assert response["uuid"] == measurement["uuid"]
        assert response["time"] == edited_json["time"]
        assert response["value"] == edited_json["value"]

        # Check difference
        record_after = await Measurement.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

    async def test_remove(self, client, header, measurement):
        # Remove
        delete = client.delete(f"/measurements/{measurement['uuid']}", headers=header)
        assert delete.status_code == 200

        # Check response
        response = delete.json()
        assert response["uuid"]
        assert response["time"]
        assert response["value"]

        # Check existence
        get_after = client.get(
            f"/measurements/?uuid={measurement['uuid']}", headers=header
        )
        assert get_after.json() == []
