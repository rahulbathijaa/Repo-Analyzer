import json
import logging
from typing import List, Optional
import outlines
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define the structure for the README data
class ReadmeData(BaseModel):
    project_description: str
    key_features: List[str]
    installation_instructions: List[str]
    usage_examples: List[str]
    license: str
    contributing_guidelines: str
    project_status: str
    roadmap: Optional[List[str]]
    acknowledgments: Optional[List[str]]

# Define a template for extracting information from the README
@outlines.prompt
def extract_readme_info(readme_content):
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

# Function to extract data from README
def extract_readme_data(model, tokenizer, readme_content: str) -> ReadmeData:
    logger.debug(f"Extracting README data for content: {readme_content}")
    prompt = extract_readme_info(readme_content)
    logger.debug(f"Generated prompt: {prompt}")
    
    generator = outlines.generate.json(model, tokenizer, ReadmeData)
    result = generator([prompt])
    logger.debug(f"Extracted README data: {result}")
    
    # Validate and create the ReadmeData object
    return ReadmeData(**result[0])

# Function to generate UI components based on the extracted data
def generate_ui_components(data: ReadmeData) -> dict:
    logger.debug(f"Generating UI components for data: {data}")
    ui_components = {
        "header": {
            "type": "header",
            "content": data.project_description
        },
        "features": {
            "type": "list",
            "items": data.key_features
        },
        "installation": {
            "type": "ordered_list",
            "items": data.installation_instructions
        },
        "usage": {
            "type": "code_block",
            "content": "\n".join(data.usage_examples)
        },
        "license": {
            "type": "text",
            "content": data.license
        },
        "contributing": {
            "type": "text",
            "content": data.contributing_guidelines
        },
        "status": {
            "type": "badge",
            "content": data.project_status
        }
    }

    if data.roadmap:
        ui_components["roadmap"] = {
            "type": "list",
            "items": data.roadmap
        }

    if data.acknowledgments:
        ui_components["acknowledgments"] = {
            "type": "list",
            "items": data.acknowledgments
        }

    logger.debug(f"Generated UI components: {ui_components}")
    return ui_components

# Main function to process README and generate output
def process_readme(model, tokenizer, readme_content: str) -> dict:
    logger.debug(f"Processing README content: {readme_content}")
    readme_data = extract_readme_data(model, tokenizer, readme_content)
    ui_components = generate_ui_components(readme_data)

    output = {
        "extracted_data": readme_data.dict(),
        "ui_components": ui_components
    }

    logger.debug(f"Processed README output: {output}")
    return output