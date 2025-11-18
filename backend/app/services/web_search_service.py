from typing import List, Dict
import httpx
from bs4 import BeautifulSoup
from googlesearch import search as google_search


class WebSearchService:
    """Service for web searching and scraping"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def search(
        self,
        query: str,
        num_results: int = 5,
        lang: str = "tr",
    ) -> List[Dict[str, str]]:
        """
        Search the web using Google

        Args:
            query: Search query
            num_results: Number of results to return
            lang: Language code

        Returns:
            List of search results with title, url, and snippet
        """
        results = []

        try:
            # Get search results from Google
            search_results = google_search(
                query,
                num_results=num_results,
                lang=lang,
                advanced=True,
            )

            for result in search_results:
                results.append({
                    "title": result.title if hasattr(result, 'title') else query,
                    "url": result.url if hasattr(result, 'url') else str(result),
                    "snippet": result.description if hasattr(result, 'description') else "",
                })

        except Exception as e:
            print(f"Search error: {e}")

        return results

    async def fetch_page_content(
        self,
        url: str,
        extract_text: bool = True,
    ) -> str:
        """
        Fetch and extract content from a web page

        Args:
            url: URL to fetch
            extract_text: Extract clean text from HTML

        Returns:
            Page content (HTML or extracted text)
        """
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            if not extract_text:
                return response.text

            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text

    async def search_and_summarize(
        self,
        query: str,
        num_results: int = 3,
    ) -> str:
        """
        Search the web and provide a summary of results

        Args:
            query: Search query
            num_results: Number of results to fetch

        Returns:
            Summary of search results
        """
        results = await self.search(query, num_results)

        summary = f"Search results for '{query}':\n\n"

        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   URL: {result['url']}\n"
            if result['snippet']:
                summary += f"   {result['snippet']}\n"
            summary += "\n"

        return summary
