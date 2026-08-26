import json
import os
import shutil
import tempfile
import time
import unittest

os.environ["MOCK_CAMERA"] = "true"

import app as app_module
from config import config as app_config


class BackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp_storage = tempfile.mkdtemp(prefix="rs-test-")
        cls.original_storage = app_config.storage_path
        app_config.storage_path = cls.tmp_storage
        app_module.ctx.storage.set_root(cls.tmp_storage)
        cls.client = app_module.app.test_client()
        app_module.ctx.camera.stop()
        time.sleep(0.2)
        app_module.ctx.camera.start()
        deadline = time.time() + 10
        while time.time() < deadline:
            if app_module.ctx.camera.frame_buffer.has_frames():
                break
            time.sleep(0.1)
        assert app_module.ctx.camera.frame_buffer.has_frames(), \
            "mock camera did not produce frames"

    @classmethod
    def tearDownClass(cls):
        try:
            app_module.ctx.capture.stop()
        except Exception:
            pass
        app_module.ctx.camera.stop()
        shutil.rmtree(cls.tmp_storage, ignore_errors=True)
        app_config.storage_path = cls.original_storage
        app_config.save()

    def _wait_capture_done(self, timeout=30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if app_module.ctx.capture.state in (
                "completed", "stopped", "error",
            ):
                return app_module.ctx.capture.state
            time.sleep(0.05)
        return "timeout"

    def test_01_health(self):
        r = self.client.get("/api/health")
        body = r.get_json()
        self.assertTrue(body["success"])

    def test_02_create_dataset_and_label(self):
        r = self.client.post("/api/datasets", json={"name": "rice_disease"})
        self.assertEqual(r.status_code, 201)
        r = self.client.post(
            "/api/datasets/rice_disease/labels", json={"name": "brownspot"})
        self.assertEqual(r.status_code, 201)
        r = self.client.post("/api/datasets", json={"name": "rice_disease"})
        self.assertEqual(r.status_code, 409)
        r = self.client.post(
            "/api/datasets/nope/labels", json={"name": "x"})
        self.assertEqual(r.status_code, 404)

    def test_03_camera_endpoints(self):
        r = self.client.get("/api/camera/capabilities")
        body = r.get_json()
        self.assertTrue(body["success"])
        self.assertIn("rgb_resolutions", body["data"])

        r = self.client.get("/api/camera/settings")
        self.assertTrue(r.get_json()["success"])

    def test_04_single_capture(self):
        state = None
        ok, err = app_module.ctx.capture.start(
            "single", "rice_disease", "brownspot")
        self.assertTrue(ok, err)
        state = self._wait_capture_done()
        self.assertEqual(state, "completed")

        rgb = os.path.join(self.tmp_storage, "rice_disease", "brownspot",
                           "rgb", "000001.png")
        depth = os.path.join(self.tmp_storage, "rice_disease", "brownspot",
                             "depth", "000001.npy")
        meta = os.path.join(self.tmp_storage, "rice_disease", "brownspot",
                            "metadata", "000001.json")
        self.assertTrue(os.path.exists(rgb), "rgb png missing")
        self.assertTrue(os.path.exists(depth), "depth npy missing")
        self.assertTrue(os.path.exists(meta), "metadata missing")
        with open(meta) as f:
            m = json.load(f)
        self.assertEqual(m["depth_scale"], 0.001)

    def test_05_burst_capture(self):
        ok, err = app_module.ctx.capture.start(
            "burst", "rice_disease", "brownspot", count=3, interval_ms=100)
        self.assertTrue(ok, err)
        state = self._wait_capture_done()
        self.assertEqual(state, "completed")
        rgb_dir = os.path.join(self.tmp_storage, "rice_disease", "brownspot", "rgb")
        files = sorted(f for f in os.listdir(rgb_dir) if f.endswith(".png"))
        self.assertEqual(len(files), 4)
        self.assertEqual(files[-1], "000004.png")

    def test_06_concurrent_capture_rejected(self):
        ok, err = app_module.ctx.capture.start(
            "continuous", "rice_disease", "brownspot", interval_ms=50)
        self.assertTrue(ok, err)
        deadline = time.time() + 10
        while time.time() < deadline and \
                app_module.ctx.capture.state != "capturing":
            time.sleep(0.05)
        ok2, err2 = app_module.ctx.capture.start(
            "single", "rice_disease", "brownspot")
        self.assertFalse(ok2)
        self.assertEqual(err2["code"], "CAPTURE_IN_PROGRESS")
        ok3, _ = app_module.ctx.capture.stop()
        self.assertTrue(ok3)
        state = self._wait_capture_done()
        self.assertIn(state, ("stopped", "completed"))

    def test_07_invalid_capture(self):
        ok, err = app_module.ctx.capture.start(
            "burst", "rice_disease", "nonexistent_label", count=1)
        self.assertFalse(ok)
        ok, err = app_module.ctx.capture.start(
            "burst", "no_such_ds", "x", count=1)
        self.assertFalse(ok)
        ok, err = app_module.ctx.capture.start("hyperdrive", "rice_disease", "brownspot")
        self.assertFalse(ok)
        self.assertEqual(err["code"], "INVALID_CAPTURE_CONFIGURATION")

    def test_08_statistics(self):
        r = self.client.get("/api/datasets/rice_disease/statistics")
        body = r.get_json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertGreater(data["total"], 0)
        self.assertGreater(data["paired"], 0)
        self.assertEqual(data["paired"], data["total"])

    def test_09_depth_endpoint(self):
        r = self.client.get("/api/depth?x=320&y=240")
        body = r.get_json()
        self.assertTrue(body["success"])
        d = body["data"]
        self.assertTrue(d["valid"])
        self.assertAlmostEqual(d["distance_m"],
                               d["depth_raw"] * d["depth_scale"], places=4)
        r = self.client.get("/api/depth?x=-5&y=0")
        self.assertFalse(r.get_json()["data"]["valid"])

    def test_10_storage(self):
        r = self.client.get("/api/storage")
        body = r.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["path"], os.path.abspath(self.tmp_storage))
        self.assertGreater(body["data"]["free_bytes"], 0)
        r = self.client.post("/api/storage/path", json={})
        self.assertFalse(r.get_json()["success"])

    def test_11_validate_dataset(self):
        rgb_dir = os.path.join(self.tmp_storage, "rice_disease", "brownspot", "rgb")
        files = sorted(f for f in os.listdir(rgb_dir) if f.endswith(".png"))
        orphan = "999999.png"
        shutil.copy(os.path.join(rgb_dir, files[0]),
                    os.path.join(rgb_dir, orphan))
        r = self.client.get("/api/datasets/rice_disease/validate")
        body = r.get_json()
        issues = body["data"]["issues"]
        match = [i for i in issues
                 if i["id"] == "999999" and i["issue"] == "missing_depth"]
        self.assertTrue(match)
        os.remove(os.path.join(rgb_dir, orphan))

    def test_12_delete_capture(self):
        r = self.client.delete("/api/captures/000004")
        self.assertTrue(r.get_json()["success"])
        base = os.path.join(self.tmp_storage, "rice_disease", "brownspot")
        self.assertFalse(os.path.exists(os.path.join(base, "rgb", "000004.png")))
        self.assertFalse(os.path.exists(os.path.join(base, "depth", "000004.npy")))

    def test_13_retake_capture(self):
        r = self.client.post("/api/captures/000003/retake")
        body = r.get_json()
        self.assertTrue(body["success"])
        rgb_dir = os.path.join(self.tmp_storage, "rice_disease", "brownspot", "rgb")
        remaining = [f for f in os.listdir(rgb_dir) if f.endswith(".png")]
        expected_next = f"{max(int(os.path.splitext(f)[0]) for f in remaining) + 1:06d}" \
            if remaining else "000001"
        self.assertEqual(body["data"]["new_id"], expected_next)
        base = os.path.join(self.tmp_storage, "rice_disease", "brownspot")
        self.assertFalse(os.path.exists(os.path.join(base, "rgb", "000003.png")))


if __name__ == "__main__":
    unittest.main()
