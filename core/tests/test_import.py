"""Importing a file through the local API and reading the Log back."""

from conftest import open_api


def test_importing_the_car_fixture_adds_a_log_that_can_be_read_back(api, car_fixture):
    response = api.post("/logs/import", json={"path": str(car_fixture.path)})

    assert response.status_code == 201
    imported = response.json()
    assert imported["file_name"] == "car-circuit.vbo"

    assert [log["id"] for log in api.get("/logs").json()] == [imported["id"]]

    log = api.get(f"/logs/{imported['id']}").json()
    assert log["file_name"] == "car-circuit.vbo"
    [outing] = log["outings"]
    # Every column of the file is a Channel, except time: it gives the others
    # their sample times.
    columns = [name for name in car_fixture.channel_names if name != "time"]
    assert [channel["name"] for channel in outing["channels"]] == [
        f"vbo.{name}" for name in columns
    ]
    assert {channel["samples"] for channel in outing["channels"]} == {car_fixture.sample_count}


def test_a_log_is_still_listed_after_the_core_is_restarted(api, data_dir, car_fixture):
    imported = api.post("/logs/import", json={"path": str(car_fixture.path)}).json()

    restarted = open_api(data_dir)

    assert [log["id"] for log in restarted.get("/logs").json()] == [imported["id"]]
    assert restarted.get(f"/logs/{imported['id']}").json() == api.get(
        f"/logs/{imported['id']}"
    ).json()
