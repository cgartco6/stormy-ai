import unittest
from stormy.core.personality import Personality

class TestPersonality(unittest.TestCase):
    def setUp(self):
        self.personality = Personality()

    def test_build_prompt(self):
        prompt = self.personality.build_prompt("Hi")
        self.assertIn("Stormy", prompt)

    def test_inject_phrase(self):
        phrase = self.personality.inject_random_phrase()
        self.assertIsInstance(phrase, str)

if __name__ == '__main__':
    unittest.main()
