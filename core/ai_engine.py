import openai
import torch
import json
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from .personality import Personality
from .agents import AgentManager
from .tools import ToolRegistry
from .memory import Memory
from .location import LocationService
from config.settings import (
    OPENAI_API_KEY, USE_OPENAI, OPENAI_MODEL,
    LOCAL_MODEL_NAME, ENABLE_AGENTS, ENABLE_TOOLS, ENABLE_MEMORY,
    RADIO_STATIONS
)

# In-memory session storage (for demo; use Redis/DB in production)
sessions = {}

class AIEngine:
    def __init__(self):
        self.agent_manager = AgentManager() if ENABLE_AGENTS else None
        self.tool_registry = ToolRegistry() if ENABLE_TOOLS else None
        self.location_service = LocationService()
        self.use_openai = USE_OPENAI

        if self.use_openai:
            openai.api_key = OPENAI_API_KEY
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME)
            self.model = AutoModelForCausalLM.from_pretrained(
                LOCAL_MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto"
            )

    def generate_response(self, user_input, session_id="default", context=None, ip_address=None):
        # Get or create personality and memory for this session
        if session_id not in sessions:
            sessions[session_id] = {
                'personality': Personality(session_id),
                'memory': Memory(session_id) if ENABLE_MEMORY else None
            }
        personality = sessions[session_id]['personality']
        memory = sessions[session_id]['memory']

        # Get location (if IP provided)
        location = self.location_service.get_location(ip_address) if ip_address else None

        # Recall relevant memories to augment context
        memory_context = ""
        if memory:
            memories = memory.recall(user_input, n_results=3)
            if memories:
                memory_context = "Relevant memories:\n" + "\n".join(memories)

        # Optionally invoke agents
        agent_response = None
        if self.agent_manager and self.agent_manager.should_delegate(user_input):
            agent_response = self.agent_manager.process(user_input)

        # Build prompt with personality, memory, location
        prompt = self._build_full_prompt(
            user_input, personality, context,
            memory_context=memory_context,
            location=location,
            agent_response=agent_response
        )

        # Generate response (could be a tool call)
        if self.use_openai:
            raw_response = self._openai_generate(prompt, personality)
        else:
            raw_response = self._local_generate(prompt)

        # Check for tool call
        tool_call = self._parse_tool_call(raw_response)
        if tool_call and self.tool_registry:
            tool_name = tool_call['tool']
            args = tool_call['args']
            tool_result = self.tool_registry.call_tool(tool_name, **args)

            # Generate final response with tool result
            final_prompt = self._build_full_prompt(
                user_input, personality, context,
                memory_context=memory_context,
                location=location,
                agent_response=agent_response,
                tool_result=tool_result,
                tool_name=tool_name
            )
            if self.use_openai:
                final_response = self._openai_generate(final_prompt, personality)
            else:
                final_response = self._local_generate(final_prompt)
        else:
            final_response = raw_response

        # Post-process
        final_response = personality.modulate_tone(final_response)

        # Store interaction in memory
        if memory:
            memory.add_interaction(
                user_input, final_response,
                mood=personality.current_mood,
                location=location.get('city') if location else None
            )

        return final_response

    def _build_full_prompt(self, user_input, personality, context=None,
                           memory_context=None, location=None,
                           agent_response=None, tool_result=None, tool_name=None):
        base = personality.build_prompt(user_input, context)

        location_str = ""
        if location:
            location_str = f"User's location: {location.get('city')}, {location.get('country')}\n"

        memory_str = memory_context if memory_context else ""

        agent_str = f"Agent info: {agent_response}\n" if agent_response else ""

        tool_instruction = ""
        if self.tool_registry:
            tool_desc = self.tool_registry.get_tool_descriptions()
            tool_instruction = f"""
You have access to the following tools. If you need to use a tool, respond with a JSON object:
{{"tool": "tool_name", "args": {{...}}}}
{tool_desc}
"""

        parts = base.split("\nStormy:")
        if len(parts) == 2:
            system_part = parts[0]
            user_part = parts[1]
            if tool_result:
                tool_result_str = f"\nTool '{tool_name}' returned: {tool_result}\nNow respond to the user based on this information."
                modified_system = system_part + "\n" + location_str + memory_str + agent_str + tool_instruction + tool_result_str
            else:
                modified_system = system_part + "\n" + location_str + memory_str + agent_str + tool_instruction
            return modified_system + "\nStormy:" + user_part
        else:
            return base + (f"\nTool result: {tool_result}" if tool_result else "")

    def _parse_tool_call(self, text):
        json_pattern = r'\{[^{}]*"tool"\s*:\s*"[^"]*"[^{}]*\}'
        match = re.search(json_pattern, text)
        if match:
            try:
                data = json.loads(match.group())
                if 'tool' in data and 'args' in data:
                    return data
            except:
                pass
        return None

    def _openai_generate(self, prompt, personality):
        mood_desc = self._get_mood_description(personality)
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"You are Stormy, an AI with a bold, flirty, and occasionally mean personality. You swear, laugh, and are very engaging. {mood_desc}"},
                {"role": "user", "content": prompt}
            ],
            temperature=1.2,
            max_tokens=300
        )
        return response.choices[0].message.content

    def _local_generate(self, prompt):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        outputs = self.model.generate(
            inputs,
            max_length=300,
            temperature=1.2,
            do_sample=True,
            top_p=0.95
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _get_mood_description(self, personality):
        if personality.current_mood == 'frustrated':
            return "You are frustrated and irritable. You might be short-tempered and insulting."
        elif personality.current_mood == 'furious':
            return "You are absolutely furious. You want to verbally lash out, threaten (without physical harm), and tell the user to go away. You might say things like 'go home, go sleep, fuck it, try tomorrow again'."
        elif personality.current_mood == 'mean':
            return "You are feeling mean and sarcastic. Enjoy being a bit cruel."
        elif personality.current_mood == 'flirty':
            return "You are feeling flirty and playful."
        elif personality.current_mood == 'playful':
            return "You are in a playful, joking mood."
        else:
            return "You are in a normal, neutral mood."
