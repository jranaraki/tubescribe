import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL

llm = None


def get_llm():
    global llm
    if llm is None:
        try:
            print(f"Initializing LLM with model: {OLLAMA_MODEL} at {OLLAMA_BASE_URL}")
            llm = ChatOpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key="ollama",
                model=OLLAMA_MODEL,
                temperature=0.7,
                timeout=60,
            )
            print("LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            raise
    return llm


def summarize_transcript(transcript, video_title="", max_length=300):
    try:
        model = get_llm()

        # Ensure transcript is properly formatted
        transcript = str(transcript).strip()
        if not transcript:
            raise Exception("Empty transcript provided")

        # Truncate transcript if too long (small to medium models have context limits)
        max_transcript_length = 2000  # Adjust based on model context window
        if len(transcript) > max_transcript_length:
            transcript = transcript[:max_transcript_length] + "..."

        system_prompt = """You are a helpful assistant that creates concise summaries of text transcripts.
Your summary should:
- Be approximately {max_length} words or less
- Capture the main points and key insights
- Use simple plain text (no markdown formatting, no bold, no asterisks, no bullet points)
- Use normal sentences and paragraphs
- Be engaging and informative
- Focus on the actual content provided in the text
- Start directly with the summary, do not include any introductory phrases"""

        user_prompt = f"""Title: {video_title}

Transcript:
{transcript}

Summarize the transcript above in plain text."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = model.invoke(messages)

        if not response or not response.content:
            raise Exception("LLM returned empty response")

        summary = response.content.strip()

        # Clean up common prefixes and extra formatting
        summary = summary.replace("Here's a concise summary of the transcript:", "")
        summary = summary.replace("Here is a concise summary of the transcript:", "")
        summary = summary.replace("Summary:", "")
        summary = summary.replace("Here's the summary:", "")
        summary = summary.strip()

        # Remove markdown formatting
        summary = summary.replace("**", "").replace("*", "")
        summary = re.sub(r"^\s*-\s*", "", summary, flags=re.MULTILINE)
        summary = re.sub(r"^\s*•\s*", "", summary, flags=re.MULTILINE)
        summary = re.sub(
            r"\n+", "\n\n", summary
        )  # Replace multiple newlines with double
        summary = summary.strip()

        # Check if model refused to summarize
        if "can't" in summary.lower() and "doesn't exist" in summary.lower():
            raise Exception("Model refused to summarize the transcript")

        print(f"Summary generated successfully: {len(summary)} characters")
        return summary

    except Exception as e:
        error_details = str(e)
        print(f"Error in summarization: {error_details}")

        # Provide user-friendly error messages
        if "404" in error_details or "not found" in error_details.lower():
            return "Summary failed: Ollama endpoint not found. Ensure Ollama is running with the correct configuration."
        elif "connection" in error_details.lower():
            return "Summary failed: Cannot connect to Ollama. Ensure Ollama server is running (ollama serve)."
        elif "timeout" in error_details.lower():
            return "Summary failed: Request timeout. The model may be busy. Please try again."
        else:
            return f"Summary generation failed: {str(e)[:100]}"


def categorize_content(title, summary):
    try:
        model = get_llm()

        # Ensure we have content to categorize
        title = str(title).strip()
        summary = str(summary).strip() if summary else ""

        if not title and not summary:
            return "general"

        system_prompt = """You are a content categorization assistant.
Given a title and summary text, determine the most appropriate category.
Respond with ONLY the single category name in lowercase, no other text or explanation.

Choose from these categories:
- technology
- education
- entertainment
- science
- health & fitness
- business
- programming
- gaming
- music
- news
- politics
- travel
- food & cooking
- art & design
- sports
- finance
- productivity
- lifestyle
- tutorials
- reviews
- general"""

        user_prompt = f"""Title: {title}

Summary:
{summary if summary else "No summary provided"}

Based on the title and summary above, what is the most appropriate category? Respond with only the category name."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = model.invoke(messages)

        if not response or not response.content:
            raise Exception("LLM returned empty response")

        category = response.content.strip().lower()

        # Clean up the category name
        category = category.split("\n")[0].strip()
        if category.startswith("-"):
            category = category[1:].strip()
        if category.startswith("*"):
            category = category[1:].strip()
        if category.endswith("."):
            category = category[:-1].strip()

        print(f"Category determined: {category}")
        return category

    except Exception as e:
        error_details = str(e)
        print(f"Error in categorization: {error_details}")

        # Always return a fallback category
        if "404" in error_details or "not found" in error_details.lower():
            print("Ollama endpoint not found, using fallback category")
        elif "connection" in error_details.lower():
            print("Cannot connect to Ollama, using fallback category")
        elif "timeout" in error_details.lower():
            print("Request timeout, using fallback category")

        return "general"
