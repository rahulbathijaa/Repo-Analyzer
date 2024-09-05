from typing import Dict, Any
import modal
import os
import transformers
import torch
import json
from transformers import BitsAndBytesConfig
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from repo_analyzer import analyze_repo
from heatmap import fetch_contributions_data, process_contributions, generate_visual_attributes, generate_heatmap_json
from modal import asgi_app 
import logging
import requests
from readme_extraction import readme_extraction


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = "meta-llama/Meta-Llama-3.1-8B-Instruct"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# Define the image with all necessary dependencies
llm_image = modal.Image.debian_slim().pip_install(
    "transformers",
    "torch",
    "sentencepiece",
    "accelerate",
    "bitsandbytes",
    "requests",
    "aiohttp",
    "pydantic",
    "jinja2",
    "outlines",
    "matplotlib",
    "seaborn",
    "pandas",
    "fastapi",
    "fastapi-cors"
)

volume = modal.Volume.from_name("llm-model-volume", create_if_missing=True)
modal_app = modal.App("meta-llama-project")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@modal_app.cls(
    gpu="A10G",
    image=llm_image,
    volumes={"/root/model_cache": volume},
    secrets=[modal.Secret.from_name("huggingface-secret"), modal.Secret.from_name("github-secret")],
    mounts=[modal.Mount.from_local_dir(".", remote_path="/root/app")]
)
class LLMInference:
    def __init__(self):
        self.tokenizer = None
        self.model = None

    @modal.enter()
    def setup(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        cache_dir = "/root/model_cache"
        os.makedirs(cache_dir, exist_ok=True)

        # Configuration for quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_auth_token=ACCESS_TOKEN, cache_dir=cache_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            use_auth_token=ACCESS_TOKEN,
            cache_dir=cache_dir,
            device_map="auto",
            quantization_config=quantization_config
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Save the model with safe serialization
        self.model.save_pretrained(cache_dir, safe_serialization=True)

    @modal.method()
    def analyze_repos(self, username: str):
        github_token = os.environ["GITHUB_TOKEN"]
        
        try:
            # Fetch contributions data (which includes user profile)
            contributions_data = fetch_contributions_data(username, github_token)
            user_profile = contributions_data["user_profile"]
            
            # Analyze repo
            repo_analysis = analyze_repo(username, github_token, self.model, self.tokenizer)
            
            # Process contributions for heatmap
            processed_contributions = process_contributions(contributions_data["repo_analysis"][0]["commits"])
            insights = generate_visual_attributes(processed_contributions)
            heatmap_json = generate_heatmap_json(processed_contributions, insights)
            
            # Call readme_extraction function to process README
            github_data = fetch_contributions_data(username, github_token)
            readme_analysis = github_data["repo_analysis"][0]["readme_content"] 

            
            final_output = {
                "user_profile": user_profile,
                "repo_analysis": repo_analysis,
                "heatmap_data": heatmap_json,
                "readme_analysis": readme_analysis
            }

            logger.info(f"Final structured output: {json.dumps(final_output, indent=2)}")

            return final_output
        except Exception as e:
            logger.error(f"Failed to analyze repos: {str(e)}")
            raise

# Create an instance of LLMInference
llm = LLMInference()

@modal_app.function(image=llm_image)
@asgi_app()
def fastapi_app():


    @app.get("/api/analyze")
    async def analyze_endpoint(username: str):
        try:
            # Use the llm instance to call analyze_repos
            structured_output = llm.analyze_repos.remote(username)
            logger.info(f"API response: {json.dumps(structured_output, indent=2)}")
            return structured_output
        except Exception as e:
            logger.error(f"Failed to analyze repos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to analyze repos: {str(e)}")

    return app

@modal_app.function(
    image=llm_image,
    secrets=[modal.Secret.from_name("github-secret")],
    gpu="any"
)
def test_analyze_repos(username: str = "rahulbathijaa"):
    # Set tokens directly (NOT RECOMMENDED for production use)


    # Create an instance of LLMInference
    llm = LLMInference()

    # Call the analyze_repos method
    result = llm.analyze_repos.remote(username)

    # Print the result
    print(json.dumps(result, indent=2))

# This allows the function to be run directly with Modal
if __name__ == "__main__":
    modal.run(test_analyze_repos)