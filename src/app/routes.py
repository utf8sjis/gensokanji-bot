def register_routes(app) -> None:
    @app.route("/")
    def root() -> str:
        return "Hello, World!"
