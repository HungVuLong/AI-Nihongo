"""FastAPI application for AI-Nihongo."""

from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    
    # Create mock classes if FastAPI is not available
    class FastAPI:
        def __init__(self, **kwargs): pass
        def add_middleware(self, *args, **kwargs): pass
        def on_event(self, event): return lambda f: f
        def get(self, path): return lambda f: f
        def post(self, path, **kwargs): return lambda f: f
    
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    HTTPException = Exception
    Depends = lambda x: x

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from ..core.agent import AIAgent
from ..core.config import settings


# Pydantic models for API
class MessageRequest(BaseModel):
    """Request model for sending messages."""
    message: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Response model for messages."""
    response: str
    analysis: Optional[Dict[str, Any]] = None


class AnalysisRequest(BaseModel):
    """Request model for text analysis."""
    text: str


class TranslationRequest(BaseModel):
    """Request model for translation."""
    text: str
    target_language: str = "en"


class TranslationResponse(BaseModel):
    """Response model for translation."""
    original_text: str
    translated_text: str
    target_language: str


# Global agent instance
agent = AIAgent()


async def get_agent() -> AIAgent:
    """Dependency to get the initialized agent."""
    if not agent.is_initialized:
        await agent.initialize()
    return agent


# Create FastAPI app
app = FastAPI(
    title="AI-Nihongo API",
    description="AI agent for Japanese language learning and processing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("Starting AI-Nihongo API...")
    try:
        await agent.initialize()
        logger.info("AI-Nihongo API started successfully")
    except Exception as e:
        logger.error(f"Failed to start AI-Nihongo API: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AI-Nihongo API...")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI-Nihongo API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent_initialized": agent.is_initialized}


@app.post("/chat", response_model=MessageResponse)
async def chat(
    request: MessageRequest,
    ai_agent: AIAgent = Depends(get_agent)
):
    """
    Chat with the AI agent.
    
    Args:
        request: Message request containing user input
        ai_agent: Initialized AI agent
        
    Returns:
        AI response with optional analysis
    """
    try:
        response = await ai_agent.process_message(
            message=request.message,
            context=request.context,
            user_id=request.user_id
        )
        
        return MessageResponse(response=response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_text(
    request: AnalysisRequest,
    ai_agent: AIAgent = Depends(get_agent)
):
    """
    Analyze Japanese text.
    
    Args:
        request: Analysis request containing text to analyze
        ai_agent: Initialized AI agent
        
    Returns:
        Detailed analysis of the Japanese text
    """
    try:
        analysis = await ai_agent.analyze_japanese_text(request.text)
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    ai_agent: AIAgent = Depends(get_agent)
):
    """
    Translate text to target language.
    
    Args:
        request: Translation request
        ai_agent: Initialized AI agent
        
    Returns:
        Translation result
    """
    try:
        translated = await ai_agent.translate_text(
            text=request.text,
            target_language=request.target_language
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            target_language=request.target_language
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-grammar")
async def explain_grammar(
    request: AnalysisRequest,
    ai_agent: AIAgent = Depends(get_agent)
):
    """
    Explain the grammar of Japanese text.
    
    Args:
        request: Analysis request containing Japanese text
        ai_agent: Initialized AI agent
        
    Returns:
        Grammar explanation
    """
    try:
        explanation = await ai_agent.explain_grammar(request.text)
        return {"text": request.text, "explanation": explanation}
        
    except Exception as e:
        logger.error(f"Grammar explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "ai_nihongo.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )