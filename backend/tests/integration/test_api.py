from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np

API = "/api/v1"


def test_create_project_builds_folder_tree(project, dest):
    assert [c["name"] for c in project["classes"]] == ["stunting", "tidak stunting"]
    assert project["formats"] == ["jpg", "png", "tiff", "png16", "npy"]  # registry order
    for fmt in ("jpg", "png", "tiff", "png16", "npy"):
        for cls in ("stunting", "tidak stunting"):
            assert (dest / fmt / cls).is_dir()


def test_project_validation(client, dest):
    bad = {"name": "x", "destination_dir": str(dest), "formats": ["bmp"], "classes": ["a"]}
    res = client.post(f"{API}/projects", json=bad)
    assert res.status_code == 422
    assert "bmp" in res.json()["error"]["message"]

    dup = {**bad, "formats": ["png"], "classes": ["a", "A"]}
    assert client.post(f"{API}/projects", json=dup).status_code == 422

    relative = {**bad, "formats": ["png"], "destination_dir": "relative/path"}
    assert client.post(f"{API}/projects", json=relative).status_code == 400


def test_burst_capture_writes_pairs_and_history(client, project, dest):
    cls = project["classes"][1]
    nxt = client.get(f"{API}/capture/next-name", params={"project_id": project["id"], "class_id": cls["id"]}).json()
    assert nxt["image_name"] == "tidak stunting-0001"

    res = client.post(f"{API}/capture", json={
        "project_id": project["id"], "class_id": cls["id"], "images_per_take": 3, "burst_interval_ms": 0,
    })
    assert res.status_code == 200, res.text
    shots = res.json()["captures"]
    assert [s["image_name"] for s in shots] == [f"tidak stunting-000{i}" for i in (1, 2, 3)]
    assert len({s["burst_id"] for s in shots}) == 1

    png = dest / "png" / "tidak stunting" / "tidak stunting-0003.png"
    npy = dest / "npy" / "tidak stunting" / "tidak stunting-0003.npy"
    assert png.is_file() and npy.is_file()
    depth = np.load(npy)
    assert depth.dtype == np.uint16 and depth.shape == (shots[2]["height"], shots[2]["width"])

    page = client.get(f"{API}/history", params={"project_id": project["id"]}).json()
    assert page["total"] == 3
    assert page["items"][0]["image_name"] == "tidak stunting-0003"  # newest first
    assert page["items"][0]["project_name"] == project["name"]
    assert page["items"][0]["captured_at"].endswith("Z")

    tomorrow = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    later = client.get(f"{API}/history", params={"project_id": project["id"], "date_from": tomorrow})
    assert later.json()["total"] == 0

    thumb = client.get(f"{API}/history/{shots[0]['id']}/thumbnail")
    assert thumb.status_code == 200 and thumb.headers["content-type"] == "image/jpeg"

    counts = {c["name"]: c["count"] for c in client.get(f"{API}/projects/{project['id']}").json()["classes"]}
    assert counts == {"stunting": 0, "tidak stunting": 3}


def test_numbering_continues_after_files_on_disk(client, project, dest):
    cls = project["classes"][0]
    stray = dest / "png" / "stunting" / "stunting-0041.png"
    stray.touch()
    nxt = client.get(f"{API}/capture/next-name", params={"project_id": project["id"], "class_id": cls["id"]}).json()
    assert nxt["image_name"] == "stunting-0042"


def test_rename_class_moves_files(client, project, dest):
    cls = project["classes"][0]
    client.post(f"{API}/capture", json={"project_id": project["id"], "class_id": cls["id"], "images_per_take": 1})
    res = client.patch(f"{API}/projects/{project['id']}/classes/{cls['id']}", json={"name": "severe"})
    assert res.status_code == 200, res.text

    assert (dest / "png" / "severe" / "severe-0001.png").is_file()
    assert not (dest / "png" / "stunting").exists()
    item = client.get(f"{API}/history", params={"project_id": project["id"]}).json()["items"][0]
    assert item["class_name"] == "severe" and item["image_name"] == "severe-0001"
    assert Path(item["files"]["npy"]).is_file()


def test_class_management_and_session(client, project):
    pid = project["id"]
    res = client.post(f"{API}/projects/{pid}/classes", json={"name": "normal"})
    assert [c["name"] for c in res.json()["classes"]][-1] == "normal"
    assert client.post(f"{API}/projects/{pid}/classes", json={"name": "Normal"}).status_code == 409

    session = client.put(f"{API}/session", json={"active_project_id": pid}).json()
    assert session["active_class_id"] == project["classes"][0]["id"]

    new_id = res.json()["classes"][-1]["id"]
    client.put(f"{API}/session", json={"active_project_id": pid, "active_class_id": new_id})
    client.delete(f"{API}/projects/{pid}/classes/{new_id}")
    assert client.get(f"{API}/session").json()["active_class_id"] is None

    res = client.patch(f"{API}/projects/{pid}", json={"formats": ["png", "npy"]})
    assert res.json()["formats"] == ["png", "npy"]


def test_camera_settings(client):
    options = client.get(f"{API}/camera/options").json()
    rgb = next(s for s in options if s["key"] == "rgb_camera")
    assert any(o["name"] == "exposure" for o in rgb["options"])

    res = client.put(f"{API}/camera/options", json={"sensor": "rgb_camera", "option": "exposure", "value": 300})
    rgb = next(s for s in res.json() if s["key"] == "rgb_camera")
    values = {o["name"]: o["value"] for o in rgb["options"]}
    assert values["exposure"] == 300 and values["enable_auto_exposure"] == 0
    assert client.get(f"{API}/camera/config").json()["options"]["rgb_camera"]["exposure"] == 300

    out_of_range = {"sensor": "rgb_camera", "option": "exposure", "value": 10**9}
    assert client.put(f"{API}/camera/options", json=out_of_range).status_code == 400

    bad = client.put(f"{API}/camera/config", json={
        "align_to_color": True, "filters": {"decimation": {"enabled": True, "magnitude": 2}},
    })
    assert bad.status_code == 400 and "Decimation" in bad.json()["error"]["message"]

    preview = {"colormap": "bone", "min_distance": 0.3, "max_distance": 3}
    ok = client.put(f"{API}/camera/config", json={"preview": preview})
    assert ok.json()["preview"]["colormap"] == "bone"

    caps = client.get(f"{API}/camera/capabilities").json()
    assert caps["color"][0]["width"] >= caps["color"][-1]["width"]

    reset = client.post(f"{API}/camera/options/reset").json()
    rgb = next(s for s in reset if s["key"] == "rgb_camera")
    assert next(o for o in rgb["options"] if o["name"] == "exposure")["value"] == 156


def test_capture_rules_validation(client):
    assert client.put(f"{API}/settings/capture-rules", json={"images_per_take": 5, "burst_interval_ms": 100,
                                                            "timer_seconds": 7}).status_code == 422
    res = client.put(f"{API}/settings/capture-rules", json={"images_per_take": 5, "burst_interval_ms": 100,
                                                           "timer_seconds": 10})
    assert res.json()["timer_seconds"] == 10


def test_delete_capture_removes_files(client, project, dest):
    cls = project["classes"][0]
    shot = client.post(f"{API}/capture", json={"project_id": project["id"], "class_id": cls["id"],
                                               "images_per_take": 1}).json()["captures"][0]
    assert client.delete(f"{API}/history/{shot['id']}").status_code == 204
    assert not any(Path(p).exists() for p in shot["files"].values())


def test_directory_browser(client, tmp_path):
    (tmp_path / "child").mkdir()
    listing = client.get(f"{API}/system/directories", params={"path": str(tmp_path)}).json()
    assert [e["name"] for e in listing["entries"]] == ["child"]
    made = client.post(f"{API}/system/directories", json={"parent": str(tmp_path), "name": "new"})
    assert made.status_code == 201 and (tmp_path / "new").is_dir()


def _make_project(client, name, dest, classes):
    res = client.post(f"{API}/projects", json={
        "name": name, "destination_dir": str(dest), "formats": ["png", "npy"], "classes": classes,
    })
    assert res.status_code == 201, res.text
    return res.json()


def _shoot(client, project, class_index=0, n=1):
    cls = project["classes"][class_index]
    res = client.post(f"{API}/capture", json={"project_id": project["id"], "class_id": cls["id"],
                                              "images_per_take": n, "burst_interval_ms": 0})
    return res.json()["captures"]


def test_delete_project_keeps_files_by_default(client, tmp_path):
    project = _make_project(client, "Keep files", tmp_path / "keep", ["a"])
    shot = _shoot(client, project)[0]
    res = client.delete(f"{API}/projects/{project['id']}")
    assert res.status_code == 200
    assert res.json() == {"deleted_captures": 1, "deleted_files": 0, "deleted_folders": 0, "errors": []}
    assert all(Path(p).is_file() for p in shot["files"].values())
    assert client.get(f"{API}/projects/{project['id']}").status_code == 404
    assert client.get(f"{API}/history", params={"project_id": project["id"]}).json()["total"] == 0


def test_delete_project_with_files_spares_other_content(client, tmp_path):
    dest = tmp_path / "wipe"
    project = _make_project(client, "Wipe files", dest, ["a", "b"])
    _shoot(client, project, 0, n=2)
    (dest / "notes.txt").write_text("the user's own file")

    res = client.delete(f"{API}/projects/{project['id']}", params={"delete_files": True}).json()
    assert res["deleted_files"] == 4 and res["errors"] == []
    assert not (dest / "png").exists() and not (dest / "npy").exists()
    assert (dest / "notes.txt").is_file()  # not the project's, so kept, and so is dest


def test_delete_project_with_files_removes_empty_destination(client, tmp_path):
    dest = tmp_path / "only-project"
    project = _make_project(client, "Only project", dest, ["a"])
    _shoot(client, project)
    client.delete(f"{API}/projects/{project['id']}", params={"delete_files": True})
    assert not dest.exists()


def test_delete_project_with_files_spares_shared_folder(client, tmp_path):
    dest = tmp_path / "shared"
    first = _make_project(client, "Shared one", dest, ["a"])
    second = _make_project(client, "Shared two", dest, ["a"])
    mine = _shoot(client, first)[0]
    theirs = _shoot(client, second)[0]

    client.delete(f"{API}/projects/{first['id']}", params={"delete_files": True})
    assert not any(Path(p).exists() for p in mine["files"].values())
    assert all(Path(p).is_file() for p in theirs["files"].values())
