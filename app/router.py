from utils.scraper import get_brochure_user_prompt
from models.ollama_model import stream_ollama
from models.gemini_model import stream_gemini


def stream_brochure(company_name: str, url: str, model: str, language: str = "English"):
    """
    Main routing function.
    - Builds brochure prompt
    - Routes to selected model
    - Streams accumulated output (for Gradio compatibility)
    """

    # Build Website Content

    website_content = get_brochure_user_prompt(company_name, url)

    # Language Handling

    if language.lower() == "english":
        prompt = f"""
Generate a professional company brochure for {company_name}.

Here is the website content:
{website_content}

Output in Markdown format.
"""
    else:
        prompt = f"""
Generate a professional company brochure for {company_name}.
Write it in {language}.
Use natural, idiomatic phrasing.

Here is the website content:
{website_content}

Output in Markdown format.
"""

    # Model Routing

    if model == "llama3.2":
        generator = stream_ollama(prompt)

    elif model == "gemini":
        generator = stream_gemini(prompt)

    else:
        raise ValueError("Unknown model selected.")

    # Streaming (Accumulated for Gradio)

    response = ""

    for chunk in generator:
        response += chunk
        yield response
