import os

from api.camera_routes import create_camera_routes, create_depth_routes
from api.capture_routes import create_capture_routes
from api.dataset_routes import create_dataset_routes, create_storage_routes


def register_blueprints(app, ctx):
    app.register_blueprint(create_camera_routes(ctx))
    app.register_blueprint(create_depth_routes(ctx))
    app.register_blueprint(create_capture_routes(ctx))
    app.register_blueprint(create_dataset_routes(ctx))
    app.register_blueprint(create_storage_routes(ctx))

    @app.route("/api/health", methods=["GET"])
    def health():
        return {"success": True, "data": {
            "status": "ok",
            "mock_camera": ctx.config.mock_camera,
            "pid": os.getpid(),
        }}
