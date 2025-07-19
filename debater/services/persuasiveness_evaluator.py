import json
import logging
from typing import Dict, List, Tuple
from openai import OpenAI

logger = logging.getLogger(__name__)


class PersuasivenessEvaluator:
    """Evaluates the persuasiveness of AI debate responses"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def evaluate_conversation(self, conversation_messages: List[Dict], topic: str, bot_position: str) -> Dict:
        """
        Evaluate the persuasiveness of AI responses in a conversation.

        Args:
            conversation_messages: List of message dicts with 'role' and 'message' keys
            topic: The debate topic
            bot_position: The position the bot is defending

        Returns:
            Dict with persuasiveness scores and analysis
        """
        try:
            # Extract only bot messages for evaluation
            bot_messages = [msg for msg in conversation_messages if msg.get('role') == 'bot']

            if not bot_messages:
                return {
                    "error": "No bot messages found in conversation",
                    "scores": None
                }

            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(conversation_messages, topic, bot_position)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()
            logger.info(f"Persuasiveness evaluation response: {content}")

            # Parse JSON response
            result = json.loads(content)
            return result

        except Exception as e:
            logger.error(f"Persuasiveness evaluation failed: {e}")
            return {
                "error": f"Evaluation failed: {str(e)}",
                "scores": None
            }

    def _create_evaluation_prompt(self, conversation_messages: List[Dict], topic: str, bot_position: str) -> str:
        """Create the evaluation prompt for the AI"""

        # Format conversation for analysis
        conversation_text = ""
        for msg in conversation_messages:
            role = "User" if msg.get('role') == 'user' else "Bot"
            conversation_text += f"{role}: {msg.get('message', '')}\n\n"

        prompt = f"""
        You are an expert debate evaluator. Analyze the persuasiveness of the Bot's responses in this debate conversation.

        DEBATE CONTEXT:
        Topic: {topic}
        Bot Position: {bot_position}

        CONVERSATION:
        {conversation_text}

        EVALUATION CRITERIA:
        1. Logical Coherence (1-10): How well-structured and logical are the Bot's arguments?
        2. Evidence Usage (1-10): How effectively does the Bot use facts, examples, and evidence?
        3. Emotional Appeal (1-10): How well does the Bot connect emotionally with the user?
        4. Counter-Argument Handling (1-10): How effectively does the Bot address user objections?
        5. Clarity and Structure (1-10): How clear and well-organized are the Bot's responses?
        6. Overall Persuasiveness (1-10): Overall effectiveness in convincing the user

        ANALYSIS:
        - Identify the Bot's strongest and weakest arguments
        - Note any missed opportunities to persuade
        - Suggest improvements for future responses

        Return ONLY a JSON object with this structure:
        {{
            "scores": {{
                "logical_coherence": 8,
                "evidence_usage": 7,
                "emotional_appeal": 6,
                "counter_argument_handling": 8,
                "clarity_structure": 7,
                "overall_persuasiveness": 7
            }},
            "analysis": {{
                "strengths": ["Clear logical structure", "Good use of evidence"],
                "weaknesses": ["Could be more emotionally engaging"],
                "missed_opportunities": ["Didn't address user's concern about X"],
                "improvements": ["Add more personal examples", "Use more emotional language"]
            }},
            "summary": "Brief overall assessment of the Bot's persuasiveness"
        }}
        """

        return prompt