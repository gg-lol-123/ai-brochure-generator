import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from typing import Dict

# Configuration

MODEL = "llama3.2"

# Ollama client (used for link classification)
openai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Headers to avoid bot blocking
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}


# Website Class

class Website:
    """
    Represents a scraped website with extracted title, text and links.
    """

    def __init__(self, url: str):
        self.url = url

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            self.body = response.content
        except requests.exceptions.RequestException:
            self.body = None
            self.title = "Error fetching page"
            self.text = ""
            self.links = []
            return

        soup = BeautifulSoup(self.body, "html.parser")

        self.title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()

            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""

        links = [link.get("href") for link in soup.find_all("a")]
        self.links = [link for link in links if link]

    def get_contents(self) -> str:
        return (
            f"Webpage Title:\n{self.title}\n\n"
            f"Webpage Contents:\n{self.text}\n\n"
        )


# Link Selection Logic

link_system_prompt = """
You are provided with a list of links found on a webpage.
Decide which links are relevant to include in a brochure about the company,
such as About, Company, Careers/Jobs, Services, Case Studies, News pages.

Respond ONLY in JSON format:
{
    "links": [
        {"type": "about page", "url": "https://full.url/here"},
        {"type": "careers page", "url": "https://full.url/here"}
    ]
}

Do NOT include Terms of Service, Privacy Policy, login, email links.
"""


def get_links_user_prompt(website: Website) -> str:
    user_prompt = f"Here are the links found on {website.url}:\n\n"
    user_prompt += "\n".join(website.links)
    return user_prompt


def get_links(url: str) -> Dict:
    website = Website(url)

    response = openai_client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    return json.loads(result)


# Full Content Aggregation

def get_all_details(url: str) -> str:
    """
    Collect landing page + relevant internal pages for brochure creation.
    """
    result = "Landing page:\n"
    result += Website(url).get_contents()

    links_data = get_links(url)

    for link in links_data.get("links", []):
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()

    return result


# Brochure Prompt Builder

def get_brochure_user_prompt(company_name: str, url: str) -> str:
    user_prompt = f"You are looking at a company called: {company_name}\n\n"
    user_prompt += (
        "Here are the contents of its landing page and other relevant pages. "
        "Use this information to build a short brochure in markdown.\n\n"
    )

    user_prompt += get_all_details(url)

    # Truncate to avoid token explosion
    return user_prompt[:5000]
