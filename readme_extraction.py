import logging
from pydantic import BaseModel
from typing import List, Optional
from transformers import PreTrainedModel, PreTrainedTokenizer
import outlines
from heatmap import fetch_contributions_data  # Import the function

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the structure for the README data
class ReadmeData(BaseModel):
    project_description: Optional[str] = ""
    key_features: Optional[List[str]] = []
    installation_instructions: Optional[List[str]] = []
    usage_examples: Optional[List[str]] = []
    license: Optional[str] = ""
    contributing_guidelines: Optional[str] = ""
    project_status: Optional[str] = ""
    roadmap: Optional[List[str]] = []
    acknowledgments: Optional[List[str]] = []

# Define a template for extracting information from the README
@outlines.prompt
def extract_readme_info(readme_content: str) -> str:
    """
    Extract the following information from the README:
    - Project description
    - Key features
    - Installation instructions
    - Usage examples
    - License
    - Contributing guidelines
    - Project status
    - Roadmap (if available)
    - Acknowledgments (if available)

    README content:
    {readme_content}

    Output the extracted information in JSON format.
    """
    return f"README content:\n{readme_content}"

# Function to extract data from README
def readme_extraction(model: PreTrainedModel, tokenizer: PreTrainedTokenizer, username: str, github_token: str) -> ReadmeData:
    # Fetch contributions data to get the readme_content
    github_data = fetch_contributions_data(username, github_token)
    readme_content = github_data.get("readme_content", "")

    if not isinstance(readme_content, str):
        logger.error("Expected readme_content to be a string, but got a %s", type(readme_content).__name__)
        return ReadmeData()

    # If readme_content is empty, return an empty ReadmeData object
    if not readme_content:
        return ReadmeData()

    logger.debug(f"Extracting README data for content: {readme_content}")
    prompt = extract_readme_info(readme_content)
    
    # Generate structured JSON output using Outlines with type-annotated arguments
    generator = outlines.generate.json(model, tokenizer, ReadmeData)
    result = generator([prompt])
    
    logger.debug(f"Extracted README data: {result}")
    
    # Validate and return the ReadmeData object
    return ReadmeData(**result[0])