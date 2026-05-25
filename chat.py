from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

# Fix: Cleaned up the spacing inside the string so spaces don't waste tokens
system_prompt_example = """You are an elementary school teacher. Respond to questions so a small child can understand using simple objects as analogies.

Example 1:
Question: What is 2 + 5?
Response: 2 + 5 results in 7 because if you have 2 chocolates and your friend gives you 5 more, you will have a total of 7 chocolates.

Example 2:
Question: What is 4 - 2?
Response: 4 - 2 results in 2 because if you have 4 marbles and you give your friend 2, you will have 2 remaining in your hand."""

config = types.GenerateContentConfig(
    system_instruction=system_prompt_example,
    max_output_tokens=300,
    temperature=0.7
)

# Fix: Ask a NEW question to see the system prompt actually work!
response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="What is 5 + 4?", 
    config=config
)

# Count tokens in your prompt text
# prompt_text = response.text
# token_count = client.models.count_tokens(
#     model="gemini-2.5-flash",
#     contents=prompt_text
# )

for chunks in response:
    print(chunks.text,end = "", flush=True)
# print(f"Your prompt uses exactly: {token_count.total_tokens} tokens")

