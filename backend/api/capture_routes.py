from flask import Blueprint, jsonify, request

from api.helpers import error, success


def create_capture_routes(ctx):
    bp = Blueprint("capture", __name__, url_prefix="/api")

    @bp.route("/capture", methods=["POST"])
    def capture():
        payload = request.get_json(silent=True) or {}
        mode = payload.get("mode", "single")
        ok, err = ctx.capture.start(
            mode,
            dataset=payload.get("dataset"),
            label=payload.get("label"),
            count=payload.get("count", 1),
            interval_ms=payload.get("interval_ms", 200),
        )
        if not ok:
            code = err["code"]
            http_status = 409 if code == "CAPTURE_IN_PROGRESS" else 400
            if code == "INSUFFICIENT_STORAGE":
                http_status = 507
            return error(code, err["message"], http_status)
        data = {"message": "capture started", **ctx.capture.get_status()}
        if mode == "single":
            thread = ctx.capture._thread
            if thread:
                thread.join(timeout=15)
            last_error = getattr(thread, "_capture_error", None)
            data = ctx.capture.get_status()
            results = _last_results(ctx)
            if results is not None:
                data["result"] = results
                _ = last_error
        return jsonify(success(data))

    @bp.route("/capture/start", methods=["POST"])
    def start_capture():
        return capture()

    @bp.route("/capture/stop", methods=["POST"])
    def stop_capture():
        ok, err = ctx.capture.stop()
        if not ok:
            return error(err["code"], err["message"], 409)
        return jsonify(success(ctx.capture.get_status()))

    @bp.route("/capture/status", methods=["GET"])
    def capture_status():
        return jsonify(success(ctx.capture.get_status()))

    @bp.route("/captures/latest", methods=["GET"])
    def latest_capture():
        result = _last_results(ctx)
        if result is None:
            return error("NOT_FOUND", "no captures in this session", 404)
        return jsonify(success(result))

    @bp.route("/captures/<capture_id>", methods=["DELETE"])
    def delete_capture(capture_id):
        payload = request.get_json(silent=True) or {}
        ok, reason = ctx.datasets.delete_capture(
            capture_id,
            dataset=payload.get("dataset"),
            label=payload.get("label"),
        )
        if not ok:
            return error("CAPTURE_ERROR", reason, 404)
        ctx.publisher.dataset_updated({
            "dataset": payload.get("dataset"),
            "statistics": None,
        })
        return jsonify(success({"deleted": capture_id}))

    @bp.route("/captures/<capture_id>/retake", methods=["POST"])
    def retake_capture(capture_id):
        payload = request.get_json(silent=True) or {}
        result, reason = ctx.datasets.retake_capture(capture_id)
        if result is None:
            return error("CAPTURE_ERROR", reason, 404)
        return jsonify(success(result))

    return bp


def _last_results(ctx):
    return getattr(ctx.capture.worker, "last_result", None)
