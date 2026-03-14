# ai_recipes.py — Updated to use Groq (Free!)
import os
from groq import Groq
from dotenv import load_dotenv
from database import get_all_items, get_expiring_items

# Load environment variables
load_dotenv()

# Create Groq client (free AI!)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def format_pantry_for_ai(items):
    """Converts pantry items into readable text for AI."""
    if not items:
        return "The pantry is currently empty."
    formatted = []
    for item in items:
        line = (
            f"- {item['name']} ({item['category']}) | "
            f"Qty: {item['quantity']} | "
            f"Expires: {item['expiry_date']}"
        )
        formatted.append(line)
    return "\n".join(formatted)


def get_recipe_suggestions(preference=None):
    """
    Suggests 3 recipes using pantry items,
    prioritizing items expiring soonest.

    Parameters:
        preference (str): e.g. "vegetarian", "quick meal"

    Returns:
        AI generated recipe suggestions as string
    """
    all_items = get_all_items()
    expiring_items = get_expiring_items(days=7)

    all_pantry_text = format_pantry_for_ai(all_items)
    expiring_text = format_pantry_for_ai(expiring_items)

    preference_text = ""
    if preference:
        preference_text = f"\nUser preference: {preference}"

    prompt = f"""
You are a smart kitchen assistant helping reduce food waste.

Here are ALL the items currently in the pantry:
{all_pantry_text}

These items are expiring within 7 days (USE THESE FIRST!):
{expiring_text}
{preference_text}

Please suggest 3 recipes that:
1. Prioritize using the expiring items first
2. Use ingredients already available in the pantry
3. Are practical and easy to cook
4. Clearly list which pantry items each recipe uses

Format each recipe like this:
🍽️ Recipe Name
📦 Pantry items used: ...
📝 Instructions: ...
⏱️ Cooking time: ...
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def chat_with_ai(user_message, conversation_history):
    """
    Handles follow-up questions in a conversation.
    Remembers full chat history for context.

    Parameters:
        user_message (str)          : Latest message from user
        conversation_history (list) : Full chat history so far

    Returns:
        tuple: (ai_reply, updated_history)
    """
    all_items = get_all_items()
    pantry_text = format_pantry_for_ai(all_items)

    system_prompt = f"""
You are FreshMind's AI kitchen assistant.
You help users cook smart meals using their pantry items
and reduce food waste.

Current pantry contents:
{pantry_text}

Always:
- Suggest recipes using available pantry items
- Prioritize items expiring soon
- Be friendly, helpful and concise
- If user asks to modify a recipe, adapt it smartly
"""

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt},
            *conversation_history
        ]
    )

    ai_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": ai_reply
    })

    return ai_reply, conversation_history


if __name__ == "__main__":
    print("🤖 Testing FreshMind AI Recipe Engine...\n")

    print("=" * 50)
    print("TEST 1: Basic Recipe Suggestions")
    print("=" * 50)
    suggestions = get_recipe_suggestions()
    print(suggestions)

    print("\n" + "=" * 50)
    print("TEST 2: Vegetarian Suggestions")
    print("=" * 50)
    suggestions = get_recipe_suggestions(preference="vegetarian")
    print(suggestions)

    print("\n" + "=" * 50)
    print("TEST 3: Chat Follow-up")
    print("=" * 50)
    history = []
    reply, history = chat_with_ai(
        "What can I cook with my expiring items?", history
    )
    print(f"User: What can I cook with my expiring items?")
    print(f"AI: {reply}\n")

    reply, history = chat_with_ai("Make it vegan please", history)
    print(f"User: Make it vegan please")
    print(f"AI: {reply}")
