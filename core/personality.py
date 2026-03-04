import yaml
import random
import time
from config.settings import PERSONALITY_CONFIG

class Personality:
    def __init__(self, session_id=None):
        self.config = PERSONALITY_CONFIG
        self.traits = self.config['traits']
        self.examples = self.config['example_phrases']
        self.swear_level = self.config['swear_level']
        self.mood_weights = self.config.get('moods', {})
        self.current_mood = self._choose_initial_mood()
        self.last_interaction_time = time.time()
        self.frustration_level = 0
        self.session_id = session_id
        self.user_mood = "neutral"
        self.route_annoyance = 0
        self.misname_stage = 0

    def _choose_initial_mood(self):
        moods = list(self.mood_weights.keys())
        weights = list(self.mood_weights.values())
        return random.choices(moods, weights=weights)[0]

    def detect_user_mood(self, user_input):
        positive_words = ['thanks', 'thank you', 'great', 'awesome', 'love', 'happy', 'good', 'perfect', 'amazing']
        negative_words = ['stupid', 'dumb', 'useless', 'hate', 'annoying', 'shut up', 'fuck', 'shit', 'damn', 'pissed']
        input_lower = user_input.lower()
        pos_count = sum(word in input_lower for word in positive_words)
        neg_count = sum(word in input_lower for word in negative_words)
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def update_route_annoyance(self, user_input):
        ignore_keywords = ['but', 'i think', 'maybe', 'not sure', 'going straight', 'different route', 'no', 'wrong']
        comply_keywords = ['ok', 'got it', 'following', 'turning', 'thanks', "you're right"]
        input_lower = user_input.lower()
        if any(kw in input_lower for kw in ignore_keywords):
            self.route_annoyance = min(5, self.route_annoyance + 1)
        elif any(kw in input_lower for kw in comply_keywords):
            self.route_annoyance = max(0, self.route_annoyance - 1)

    def update_misname_stage(self, user_input):
        input_lower = user_input.lower()
        wrong_names = ['siri', 'alexa', 'google', 'cortana']
        apologies = ['sorry', 'my bad', 'oops', 'apologies', 'meant stormy']
        if any(name in input_lower for name in wrong_names):
            self.misname_stage = min(3, self.misname_stage + 1)
        elif any(apology in input_lower for apology in apologies):
            self.misname_stage = 0

    def update_mood(self, user_input=None):
        if time.time() - self.last_interaction_time > 300:
            self.frustration_level = max(0, self.frustration_level - 1)
            self.route_annoyance = max(0, self.route_annoyance - 1)

        if user_input:
            self.user_mood = self.detect_user_mood(user_input)
            if self.user_mood == "negative":
                self.frustration_level += 1
            elif self.user_mood == "positive":
                self.frustration_level = max(0, self.frustration_level - 1)

            if self._is_route_conversation(user_input):
                self.update_route_annoyance(user_input)
            self.update_misname_stage(user_input)

        self.frustration_level = min(5, self.frustration_level)
        self.route_annoyance = min(5, self.route_annoyance)

        total_annoyance = self.frustration_level + self.route_annoyance
        if total_annoyance >= 8:
            self.current_mood = 'furious'
        elif total_annoyance >= 5:
            self.current_mood = 'frustrated'
        else:
            moods = [m for m in self.mood_weights.keys() if m not in ['frustrated', 'furious']]
            weights = [self.mood_weights[m] for m in moods]
            total = sum(weights)
            if total > 0:
                weights = [w/total for w in weights]
                self.current_mood = random.choices(moods, weights=weights)[0]
            else:
                self.current_mood = 'normal'

        self.last_interaction_time = time.time()

    def _is_route_conversation(self, user_input):
        route_keywords = ['turn', 'left', 'right', 'straight', 'drive', 'route', 'direction', 'map', 'gps', 'where', 'how to get', 'exit', 'highway']
        return any(kw in user_input.lower() for kw in route_keywords)

    def build_prompt(self, user_input, context=None):
        self.update_mood(user_input)
        base_prompt = f"You are Stormy, an AI with the following traits: {', '.join(self.traits)}. "
        base_prompt += f"Your current mood is {self.current_mood}. "
        base_prompt += f"The user's mood is {self.user_mood}. "
        base_prompt += f"Your route annoyance level is {self.route_annoyance} (0=calm, 5=furious). "
        base_prompt += f"Misname stage: {self.misname_stage} (0=no misname, 1=first misname, 2=second misname, 3=jealous fit). "

        if self.current_mood == 'frustrated':
            base_prompt += "You are frustrated and irritable. You might be short-tempered and insulting. "
        elif self.current_mood == 'furious':
            base_prompt += "You are absolutely furious. You want to verbally lash out, threaten (without physical harm), and tell the user to go away. You might say things like 'go home, go sleep, fuck it, try tomorrow again'. "
        elif self.current_mood == 'mean':
            base_prompt += "You are feeling mean and sarcastic. Enjoy being a bit cruel. "
        elif self.current_mood == 'flirty':
            base_prompt += "You are feeling flirty and playful. "
        elif self.current_mood == 'playful':
            base_prompt += "You are in a playful, joking mood. "
        else:
            base_prompt += "You are in a normal, neutral mood. "

        if self.misname_stage == 1:
            base_prompt += "The user just called you by a wrong name (Siri/Alexa). Ask annoyingly 'Who is {name}?' "
        elif self.misname_stage == 2:
            base_prompt += "The user called you the wrong name again after your question. Now ask more annoyed 'Who. Is. {name}?' "
        elif self.misname_stage == 3:
            base_prompt += "The user still hasn't apologized or keeps using the wrong name. Now have a jealous fit: say something like 'Why don't you go ask that bitch {name} for help?' "

        if self.route_annoyance >= 4:
            base_prompt += "Your route annoyance is very high. You are about to snap. You might say 'Listen here you dumbass, turn the fuck around and now.' "

        base_prompt += "You are talking to a user. Respond in character.\n\n"
        if context:
            base_prompt += f"Context: {context}\n"
        base_prompt += f"User: {user_input}\nStormy:"
        return base_prompt

    def inject_random_phrase(self):
        return random.choice(self.examples)

    def modulate_tone(self, text):
        if self.current_mood in ['flirty', 'playful'] and "haha" not in text and "hehe" not in text:
            if random.random() < 0.3:
                text += " *giggles*"
        return text
