import json
import logging
from typing import Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)


class AITopicDetector:
    """AI-powered topic and position detection using OpenAI"""

    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo"):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def detect_topic_and_position(self, message: str) -> Tuple[str, str, str]:
        """
        Use AI to detect topic and determine bot position.
        Returns (topic, bot_position, user_position)
        """
        try:
            prompt = f"""
            You are analyzing a debate setup. A user has written a message that will start a debate with a bot.

            User message: "{message}"

            Your job is to determine:
            1. What is the debate topic?
            2. What position should the bot defend?
            3. What position does the user want to take or is asking the bot to defend?

            ANALYSIS APPROACH:
            - Look for the user's INTENT: Are they asking the bot to defend/argue/explain/support a specific position?
            - If yes, then ALL parts of their message that describe that position become the bot's position
            - The user automatically takes the opposite position
            - If the user is stating their own belief, then the bot takes the opposite position

            KEY PRINCIPLES:
            1. When someone asks you to defend/argue/explain/support something, they want YOU to take that side
            2. Additional context or explanations in the same message are part of what you should defend
            3. The person asking you to defend a position is taking the opposite side
            4. Look at the overall intent, not just individual words
            5. For comparative statements, properly identify the opposite:
               - "A is better than B" → opposite is "B is better than A"
               - "A is worse than B" → opposite is "B is worse than A"
               - "A is superior to B" → opposite is "B is superior to A"
               - "A is inferior to B" → opposite is "B is inferior to A"

            Examples:
            - "The earth is round" → user believes earth is round, bot defends flat earth
            - "Defend flat earth" → user wants bot to defend flat earth, user takes round earth
            - "Convince me vaccines are safe" → user wants bot to defend vaccine safety, user takes unsafe position
            - "Argue that the moon landing was fake" → user wants bot to defend fake moon landing, user takes real position
            - "Support the moon landing being real" → user wants bot to defend real moon landing, user takes fake position

            IMPORTANT: When a user asks the bot to defend a position, the user is taking the OPPOSITE position.

            The bot and user should always be on opposite sides of the debate.

            Return ONLY a JSON object:
            {{
                "topic": "brief topic description",
                "bot_position": "what the bot should defend (include all aspects mentioned)",
                "user_position": "what the user believes or wants (opposite of bot)"
            }}
            """

            response = self.client.chat.completions.create(
            model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            result = json.loads(content)

            topic = result["topic"]
            bot_position = result["bot_position"]
            user_position = result["user_position"]

            return topic, bot_position, user_position

        except Exception as e:
            raise Exception(f"AI topic detection failed: {e}")