from fastapi import APIRouter, HTTPException, status
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.web_search_service import WebSearchService
from app.services.ai_factory import AIServiceFactory

router = APIRouter()
search_service = WebSearchService()


@router.post("/", response_model=SearchResponse)
async def search_web(request: SearchRequest):
    """Search the web and get AI-summarized results"""

    try:
        # Perform search
        results = await search_service.search(
            request.query,
            request.num_results,
            request.lang,
        )

        # Convert to SearchResult objects
        search_results = [
            SearchResult(**result) for result in results
        ]

        # Generate summary using AI
        ai_service = AIServiceFactory.get_service()

        # Prepare context for AI
        context = f"Web search results for '{request.query}':\n\n"
        for i, result in enumerate(results, 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet']}\n\n"

        # Get AI summary
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes web search results.",
            },
            {
                "role": "user",
                "content": f"Please provide a concise summary of these search results:\n\n{context}",
            },
        ]

        summary = await ai_service.chat(messages, temperature=0.3)

        return SearchResponse(
            query=request.query,
            results=search_results,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )
