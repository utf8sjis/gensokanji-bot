def register_routes(app):
    @app.route("/")
    def root() -> str:
        return "Hello, World!"
