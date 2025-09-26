"""
AI Services using Google Gemini
Handles content summarization and tagging
"""
import os
import json
import google.generativeai as genai
from typing import Dict, List, Any

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")


def safe_json_parse(text: str, fallback: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Safely parse JSON from text with fallback
    
    Args:
        text: Text to parse as JSON
        fallback: Fallback dictionary if parsing fails
        
    Returns:
        Parsed JSON or fallback
    """
    if fallback is None:
        fallback = {"summary_bullets": [], "tags": []}
    
    try:
        # Try to find JSON in the text
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start != -1 and end > start:
            json_text = text[start:end]
            return json.loads(json_text)
        else:
            return fallback
    except (json.JSONDecodeError, ValueError):
        return fallback


def summarize_and_tag(md_text: str) -> Dict[str, Any]:
    """
    Summarize content and generate tags using Gemini
    
    Args:
        md_text: Markdown text to process
        
    Returns:
        Dictionary with summary_bullets and tags
    """
    if not md_text or len(md_text.strip()) < 50:
        return {"summary_bullets": [], "tags": []}
    
    # Limit text length to avoid token limits
    text_to_process = md_text[:8000]
    
    prompt = """Metni 5 maddede özetle ve 5 kısa etiket üret. 
    
Yanıtı JSON formatında ver:
{
  "summary_bullets": ["madde 1", "madde 2", "madde 3", "madde 4", "madde 5"],
  "tags": ["etiket1", "etiket2", "etiket3", "etiket4", "etiket5"]
}

Metin:
"""
    
    try:
        response = model.generate_content([prompt, text_to_process])
        text = (response.text or "").strip()
        
        result = safe_json_parse(text)
        
        # Ensure we have the expected structure
        if "summary_bullets" not in result:
            result["summary_bullets"] = []
        if "tags" not in result:
            result["tags"] = []
        
        # Limit to 5 items each
        result["summary_bullets"] = result["summary_bullets"][:5]
        result["tags"] = result["tags"][:5]
        
        return result
        
    except Exception as e:
        print(f"Error in AI processing: {e}")
        return {"summary_bullets": [], "tags": []}


def generate_summary(md_text: str) -> str:
    """
    Generate a simple summary of the content
    
    Args:
        md_text: Markdown text to summarize
        
    Returns:
        Summary string
    """
    result = summarize_and_tag(md_text)
    return "\n".join(result.get("summary_bullets", []))


def generate_tags(md_text: str) -> List[str]:
    """
    Generate tags for the content
    
    Args:
        md_text: Markdown text to tag
        
    Returns:
        List of tags
    """
    result = summarize_and_tag(md_text)
    return result.get("tags", [])


def is_ai_available() -> bool:
    """
    Check if AI service is available
    
    Returns:
        True if AI service is configured and available
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        return api_key and api_key != "your-gemini-api-key-here"
    except Exception:
        return False