from openai import OpenAI
MODEL = "llama3.2"

# Ollama must be running locally:
# Run: ollama serve

ollama_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


# Streaming Function

def stream_ollama(prompt: str):
    """
    Streams response from local Ollama (llama3.2).
    Yields incremental text chunks.
    """

    stream = ollama_client.chat.completions.create(
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
