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
        "edits",
        [
            (
                {
                    "time": "2020-07-30T14:48:00Z",
                    "value": 1.0,
                }
            ),
        ],
    )
    async def test_edit(self, client, header, measurement, measurement_json, edits):
        # Check existence
        record_before = await Measurement.get(uuid=measurement["uuid"])

        # Edit
        edit = client.put(
            f"/measurements/{measurement['uuid']}", headers=header, json=edits
        )
        assert edit.status_code == 200

        # Merge edits
        edited_json = measurement_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit.json()
        assert response["uuid"] == measurement["uuid"]
        assert response["time"] == edited_json["time"]
        assert response["value"] == edited_json["value"]

        # Check difference
        record_after = await Measurement.get(uuid=response["uuid"])
        assert record_before.uuid == record_after.uuid
        assert record_before.all() != record_after.all()

    @pytest.mark.parametrize(
        "edits",
        [
            (
                {
                    "time": "2020-07-30T14:48:00Z",
                    "value": 1.0,
                }
            ),
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
    async def test_edit_partially(
        self, client, header, measurement, measurement_json, edits
    ):
        # Check existence
        record_before = await Measurement.get(uuid=measurement["uuid"])

        # Edit
        edit_partially = client.patch(
            f"/measurements/{measurement['uuid']}", headers=header, json=edits
        )
        assert edit_partially.status_code == 200

        # Merge edits
        edited_json = measurement_json.copy()
        edited_json.update(edits)

        # Check response
        response = edit_partially.json()
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

    async def test_get_all(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get("/measurements/", headers=header)
        assert response_get.status_code == 200
        assert len(response_get.json()) == 3

    async def test_get_above_time(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get(
            "/measurements/?start_time=1999-01-01T00%3A00%3A00Z", headers=header
        )
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    async def test_get_below_time(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get(
            "/measurements/?finish_time=1999-01-01T00%3A00%3A00Z", headers=header
        )
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    async def test_get_between_time(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get(
            "/measurements/?start_time=1998-12-31T23%3A59%3A59.999Z&finish_time=1999-01-01T00%3A00%3A00Z",
            headers=header,
        )
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    async def test_get_above_value(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get("/measurements/?min_value=4.9", headers=header)
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    async def test_get_below_value(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get("/measurements/?max_value=5", headers=header)
        assert response_get.status_code == 200
        assert len(response_get.json()) == 2

    async def test_get_between_values(self, client, header, sensor):
        # Preparations
        measurements_json = [
            {
                "time": "2024-07-30T14:48:00Z",
                "value": 5.0,
            },
            {
                "time": "1998-12-31T23:59:59.999Z",
                "value": 10,
            },
            {
                "time": "1999-01-01T00:00:00Z",
                "value": -15,
            },
        ]
        for measurement_json in measurements_json:
            create = client.post(
                f"/measurements/{sensor['uuid']}", headers=header, json=measurement_json
            )
            assert create.status_code == 200

        # Check quantity
        response_get = client.get(
            "/measurements/?min_value=4.9&max_value=5", headers=header
        )
        assert response_get.status_code == 200
        assert len(response_get.json()) == 1

    async def test_get_not_shared(self, client, header2, measurement):
        get = client.get(f"/measurements/?uuid={measurement["uuid"]}", headers=header2)
        assert get.status_code == 200
        assert get.json() == []

    async def test_get_sensor_not_shared(self, client, header2, sensor):
        get = client.get(
            f"/measurements/?sensor_uuid={sensor["uuid"]}", headers=header2
        )
        assert get.status_code == 200
        assert get.json() == []

    async def test_get_all_not_shared(self, client, header2, measurement):
        get = client.get(f"/measurements/", headers=header2)
        assert get.status_code == 200
        assert get.json() == []

    async def test_get_shared(self, client, header2, measurement_shared):
        get = client.get(
            f"/measurements/?uuid={measurement_shared["uuid"]}", headers=header2
        )
        assert get.status_code == 200
        assert get.json() == [measurement_shared]

    async def test_get_sensor_shared(
        self, client, header2, sensor_shared, measurement_shared, measurement_shared2
    ):
        get = client.get(
            f"/measurements/?sensor_uuid={sensor_shared["uuid"]}", headers=header2
        )
        assert get.status_code == 200
        assert len(get.json()) == 2

    async def test_get_all_shared(self, client, header2, measurement_shared):
        get = client.get(f"/measurements/", headers=header2)
        assert get.status_code == 200
        assert get.json() == []
