from flask import Blueprint, jsonify, request

from api.helpers import error, success


ERROR_MAP = {
    "CAMERA_NOT_FOUND": ("Intel RealSense camera was not detected.", 404),
    "CAMERA_DISCONNECTED": ("Camera is not connected.", 409),
    "CAMERA_CONFIGURATION_ERROR": ("Invalid camera configuration.", 400),
}


def create_camera_routes(ctx):
    bp = Blueprint("camera", __name__, url_prefix="/api/camera")

    @bp.route("/status", methods=["GET"])
    def status():
        return jsonify(success(ctx.camera.get_status()))

    @bp.route("/info", methods=["GET"])
    def info():
        return jsonify(success(ctx.camera.get_status()))

    @bp.route("/capabilities", methods=["GET"])
    def capabilities():
        return jsonify(success(ctx.camera.get_capabilities()))

    @bp.route("/settings", methods=["GET"])
    def get_settings():
        return jsonify(success(ctx.camera.get_settings()))

    @bp.route("/settings", methods=["POST"])
    def post_settings():
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return error("INVALID_CAPTURE_CONFIGURATION",
                         "request body must be an object", 400)
        ok, errors = ctx.camera.update_settings(payload)
        if not ok:
            return error("CAMERA_CONFIGURATION_ERROR",
                         "; ".join(errors), 400)
        ctx.publisher.settings_changed(ctx.camera.get_settings())
        return jsonify(success(ctx.camera.get_settings()))

    @bp.route("/connect", methods=["POST"])
    def connect():
        st = ctx.camera.connect()
        if st["status"] in ("error", "disconnected"):
            return error("CAMERA_NOT_FOUND",
                         ERROR_MAP["CAMERA_NOT_FOUND"][0], 404)
        return jsonify(success(st))

    @bp.route("/disconnect", methods=["POST"])
    def disconnect():
        return jsonify(success(ctx.camera.disconnect()))

    return bp


def create_depth_routes(ctx):
    bp = Blueprint("depth", __name__, url_prefix="/api")

    @bp.route("/depth", methods=["GET"])
    def depth():
        try:
            x = int(request.args.get("x"))
            y = int(request.args.get("y"))
        except (TypeError, ValueError):
            return error("INVALID_REQUEST",
                         "query parameters x and y must be integers", 400)
        return jsonify(success(ctx.depth.query(x, y)))

    return bp
