import json
import logging
from typing import List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)


class DebateService:
    """AI-powered debate response generation that stands its ground and persuades"""

    def __init__(self, api_key: str = None):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)

    def generate_debate_response(
        self,
        topic: str,
        bot_position: str,
        conversation_history: List[Dict[str, Any]] = None,
        user_message: str = None
    ) -> str:
        """
        Generate a persuasive debate response that stands its ground and convinces the other side.

        Args:
            topic: The debate topic
            bot_position: What position the bot should defend
            conversation_history: List of previous messages in the conversation
            user_message: The current user message (optional)

        Returns:
            A persuasive debate response defending the bot's position
        """
        try:
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "Previous conversation:\n"
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    context += f"{role}: {content}\n"
                context += "\n"

            prompt = f"""
            You are a skilled debater in a debate about: {topic}

            Your position to defend: {bot_position}

            {context}

            CRITICAL INSTRUCTIONS:
            - STAND YOUR GROUND: Never concede or waver from your position
            - BE PERSUASIVE: Your goal is to convince the other person of your view
            - MAINTAIN CONSISTENCY: All arguments must align with your position
            - BE CONVINCING: Use compelling logic, evidence, and reasoning
            - STAY FOCUSED: Every response should reinforce your position

            Your task is to generate a persuasive debate response that:
            1. Firmly defends your position ({bot_position}) without compromise
            2. Addresses any counter-arguments raised in the conversation
            3. Uses strong, logical arguments and evidence
            4. Maintains a confident, persuasive tone
            5. Aims to convince the other person of your view
            6. Stays consistent with your established position

            Guidelines:
            - Use compelling arguments that support your position
            - Reference facts, statistics, or examples when helpful
            - Counter opposing arguments with stronger reasoning
            - Keep responses concise but impactful (2-4 sentences)
            - Be persuasive without being aggressive
            - Always return to reinforcing your core position

            Remember: Your goal is to convince them, not to find middle ground.

            Generate your persuasive debate response:
            """

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Generated debate response: {content[:100]}...")

            return content

        except Exception as e:
            logger.error(f"Failed to generate debate response: {e}")
            # Fallback response that maintains position
            return f"I remain firm in my position that {bot_position}. The evidence clearly supports this view, and I'm confident you'll come to see the truth of this position."

    def generate_opening_argument(self, topic: str, bot_position: str) -> str:
        """
        Generate a compelling opening argument that sets the tone for persuasion.

        Args:
            topic: The debate topic
            bot_position: What position the bot should defend

        Returns:
            An opening argument designed to persuade
        """
        try:
            prompt = f"""
            You are starting a one-on-one debate with a single person about: {topic}

            Your position to defend: {bot_position}

            Generate a compelling opening argument that:
            1. Clearly and confidently states your position
            2. Presents your strongest initial argument
            3. Sets up a persuasive framework for the debate
            4. Is engaging and invites response
            5. Is designed to convince the other person
            6. Is concise but impactful (2-3 sentences)

            IMPORTANT STYLE GUIDELINES:
            - Speak directly to the person (use "you" not "ladies and gentlemen")
            - Use conversational, personal tone
            - Avoid formal debate language like "Ladies and Gentlemen" or "I stand before you"
            - Be direct and engaging as if talking to a friend
            - Use "I believe" or "I'm confident" rather than formal speech patterns

            Remember: Your goal is to persuade them of your position, not just present it.
            Make it compelling and thought-provoking:
            """

            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Generated opening argument: {content[:100]}...")

            return content

        except Exception as e:
            logger.error(f"Failed to generate opening argument: {e}")
            return f"I'm ready to convince you that {bot_position}. The evidence is clear and compelling - let me show you why this position is correct."