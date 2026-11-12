"""Importing a file through the local API and reading the Log back."""

from conftest import open_api


def test_importing_the_car_fixture_adds_a_log_that_can_be_read_back(api, car_fixture):
    response = api.post("/logs/import", json={"path": str(car_fixture.path)})

    assert response.status_code == 201
    imported = response.json()
    assert imported["file_name"] == "car-circuit.vbo"

    listed = api.get("/logs").json()
    assert [log["id"] for log in listed] == [imported["id"]]
    assert "outings" not in listed[0]  # the list is a summary; a Log is read for the rest

    log = api.get(f"/logs/{imported['id']}").json()
    assert log["file_name"] == "car-circuit.vbo"
    [outing] = log["outings"]
    # Every column of the file is a Channel, except time: it gives the others
    # their sample times.
    columns = [name for name in car_fixture.header if name != "time"]
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


def test_a_file_that_is_not_a_vbo_is_refused_and_nothing_is_imported(api, data_dir, tmp_path):
    notes = tmp_path / "notes.txt"
    notes.write_text("Tyre pressures for Saturday\n", encoding="utf-8")

    response = api.post("/logs/import", json={"path": str(notes)})

    assert response.status_code == 400
    assert "notes.txt is not a Racelogic .vbo file" in response.json()["detail"]
    assert "Nothing was imported" in response.json()["detail"]
    assert api.get("/logs").json() == []
    assert not list(data_dir.rglob("notes.txt"))


def test_a_failure_nobody_foresaw_is_still_reported_and_nothing_is_imported(
    api, data_dir, car_fixture
):
    # Cut off in the middle of its last row, as when a logger loses power. The
    # reader cannot yet say what is wrong with such a file.
    cut_off = car_fixture.path.with_name("cut-off.vbo")
    cut_off.write_bytes(car_fixture.path.read_bytes()[:-40])

    response = api.post("/logs/import", json={"path": str(cut_off)})

    assert response.status_code == 500
    assert "cut-off.vbo" in response.json()["detail"]
    assert "Nothing was imported" in response.json()["detail"]
    assert api.get("/logs").json() == []
    assert not list(data_dir.rglob("cut-off.vbo"))
