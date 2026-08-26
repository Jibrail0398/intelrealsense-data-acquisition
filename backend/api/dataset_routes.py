from flask import Blueprint, jsonify, request

from api.helpers import error, success


def create_dataset_routes(ctx):
    bp = Blueprint("datasets", __name__, url_prefix="/api/datasets")

    @bp.route("", methods=["GET"])
    def list_datasets():
        return jsonify(success({"datasets": ctx.datasets.list_datasets()}))

    @bp.route("", methods=["POST"])
    def create_dataset():
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        ok, reason = ctx.datasets.create_dataset(name)
        if not ok:
            code = "INVALID_DATASET"
            message = reason
            if reason == "dataset already exists":
                return error(code, message, 409)
            return error(code, message, 400)
        return jsonify(success({"name": name})), 201

    @bp.route("/<dataset_id>", methods=["GET"])
    def get_dataset(dataset_id):
        dataset = ctx.datasets.get_dataset(dataset_id)
        if dataset is None:
            return error("INVALID_DATASET", "dataset not found", 404)
        return jsonify(success(dataset))

    @bp.route("/<dataset_id>/labels", methods=["GET"])
    def list_labels(dataset_id):
        if not ctx.datasets.is_valid_name(dataset_id):
            return error("INVALID_DATASET", "invalid dataset name", 400)
        labels = ctx.datasets.labels.list_labels(dataset_id)
        return jsonify(success({"labels": labels}))

    @bp.route("/<dataset_id>/labels", methods=["POST"])
    def create_label(dataset_id):
        payload = request.get_json(silent=True) or {}
        label = payload.get("name") or payload.get("label")
        ok, reason = ctx.datasets.create_label(dataset_id, label)
        if not ok:
            http_status = 409 if reason == "label already exists" else 400
            if reason == "dataset not found":
                http_status = 404
            return error("INVALID_LABEL", reason, http_status)
        return jsonify(success({"name": label})), 201

    @bp.route("/<dataset_id>/statistics", methods=["GET"])
    def statistics(dataset_id):
        stats = ctx.statistics.compute(dataset_id)
        if stats is None:
            return error("INVALID_DATASET", "dataset not found", 404)
        return jsonify(success(stats))

    @bp.route("/<dataset_id>/validate", methods=["GET"])
    def validate(dataset_id):
        result = ctx.datasets.validate_dataset(dataset_id)
        return jsonify(success(result))

    return bp


def create_storage_routes(ctx):
    bp = Blueprint("storage", __name__, url_prefix="/api/storage")

    @bp.route("", methods=["GET"])
    def storage_info():
        info = ctx.storage.get_info()
        ctx.publisher.storage_updated(info)
        return jsonify(success(info))

    @bp.route("/path", methods=["POST"])
    def set_path():
        payload = request.get_json(silent=True) or {}
        path = payload.get("path")
        if not path or not isinstance(path, str):
            return error("STORAGE_ERROR", "field 'path' is required", 400)
        ok, reason = ctx.storage.set_root(path)
        if not ok:
            return error("STORAGE_ERROR", reason, 400)
        ctx.storage.ensure_root()
        ctx.publisher.storage_updated(ctx.storage.get_info())
        return jsonify(success(ctx.storage.get_info()))

    return bp
