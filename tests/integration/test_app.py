class TestApp:
    def test_hello_world(self, app_client):
        # When:
        response = app_client.get("/")

        # Then:
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "Hello, World!"
