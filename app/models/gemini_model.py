import os
from openai import OpenAI
from dotenv import load_dotenv


# Load Environment Variables

load_dotenv(override=True)
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables.")


# Configuration

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL = "gemini-2.5-flash"

gemini_client = OpenAI(
    api_key=google_api_key,
    base_url=GEMINI_BASE_URL
)


# Streaming Function

def stream_gemini(prompt: str):
    """
    Streams response from Gemini using OpenAI-compatible endpoint.
    Yields incremental text chunks.
    """

    stream = gemini_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
