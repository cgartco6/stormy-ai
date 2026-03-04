import unittest
from stormy.core.ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AIEngine()

    def test_generate_response(self):
        response = self.engine.generate_response("Hello")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == '__main__':
    unittest.main()
