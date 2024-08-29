import transformers
import torch
from outlines.text import PromptTemplate
from outlines.text import Caching

async def generate_summary(profile_data: dict, model, tokenizer):
    # Initialize the text generation pipeline
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16,
        device_map="auto"  # Ensure the model runs on GPU if available
    )
    
    # Define a more dynamic prompt template using Outlines
    template = PromptTemplate("""
    {{ username }} has been a GitHub member for {{ years_on_github }} years.
    They have {{ public_repos }} public repositories and are followed by {{ followers }} people.
    Throughout their journey, they have followed {{ following }} developers.
    Their bio reads: {{ bio }}.
    
    This user is particularly known for their contributions in {{ expertise_area }}.
    Some of their most notable work includes {{ notable_projects }}. Their career milestones include {{ milestones }}.
    """)
    
    # Populate the template with user profile data
    prompt = template.render(
        username=profile_data['username'],
        years_on_github=profile_data['years_on_github'],
        public_repos=profile_data['public_repos'],
        followers=profile_data['followers'],
        following=profile_data['following'],
        bio=profile_data['bio'],
        expertise_area="AI and serverless computing",  # Example: You can make this dynamic based on profile data
        notable_projects="developing robust chatbot solutions",  # Dynamic example
        milestones="pushing boundaries in both functionality and scalability"  # Dynamic example
    )
    
    # Caching setup to avoid redundant generations
    cache = Caching(cache_path=".cache")  # Adjust the path as needed
    cache_key = f"summary_{profile_data['username']}"
    
    if cache.exists(cache_key):
        return cache.get(cache_key)
    
    # Generate the output with more deterministic parameters
    outputs = pipeline(
        prompt,
        max_new_tokens=300,  # Adjust the length of the output
        do_sample=False,    # Disable sampling to make the output deterministic
        temperature=0.7,    # Control randomness
        top_p=0.9,          # Nucleus sampling
        num_return_sequences=1  # Return only one result
    )

    # Extract the generated text
    generated_text = outputs[0]["generated_text"]

    # Post-process the generated text to ensure it is a single paragraph
    generated_text = generated_text.replace("\n", " ").strip()

    # Cache the generated text for future use
    cache.set(cache_key, generated_text)

    return generated_text
