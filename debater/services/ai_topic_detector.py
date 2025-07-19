import json
import logging
from typing import Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)


class AITopicDetector:
    """AI-powered topic and position detection using OpenAI"""

    def __init__(self, api_key: str = None):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)

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

            CRITICAL: Look for directive phrases that tell the bot what to do:
            - "Convince me that..." → bot should defend that position, user takes opposite
            - "Defend the position that..." → bot should defend that position, user takes opposite
            - "Argue that..." → bot should defend that position, user takes opposite
            - "Take the side of..." → bot should defend that position, user takes opposite
            - "Support..." → bot should defend that position, user takes opposite

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
                "bot_position": "what the bot should defend",
                "user_position": "what the user believes or wants (opposite of bot)"
            }}
            """

            # Try gpt-4 first, fallback to 3.5-turbo
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1
                )
            except Exception:
                logger.warning("gpt-4 not available, falling back to gpt-3.5-turbo")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1
                )

            content = response.choices[0].message.content.strip()
            logger.info(f"AI response: {content}")

            # Parse JSON response
            result = json.loads(content)
            return result["topic"], result["bot_position"], result["user_position"]

        except Exception as e:
            raise Exception(f"AI topic detection failed: {e}")