
import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_autocomplete(self):
        response = self.app.get("/autocomplete?city=New")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 5)  # assuming 5 cities match "New"

    def test_search_history(self):
        response = self.app.get("/search_history")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 0)  # no searches yet

    def test_weather(self):
        response = self.app.post("/", data={"city": "New York"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Weather in New York", response.data)

if __name__ == "__main__":
    unittest.main()