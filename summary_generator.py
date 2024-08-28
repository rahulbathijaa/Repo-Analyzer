import transformers
import torch

async def generate_summary(profile_data: dict, model, tokenizer):
    # Initialize the text generation pipeline
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.float16,
        device_map="auto"  # Ensure the model runs on GPU if available
    )

    # Construct the prompt using profile data
    prompt = f"""
    Generate a detailed and engaging summary for the following GitHub profile:
    Username: {profile_data['username']}
    Years on GitHub: {profile_data['years_on_github']}
    Public Repos: {profile_data['public_repos']}
    Followers: {profile_data['followers']}
    Following: {profile_data['following']}
    Bio: {profile_data['bio']}

    The summary should highlight the user's expertise, contributions, growth, and notable projects. It should be written in a narrative style similar to the following example:

    Rahul has been an active contributor to GitHub since 2018, where his expertise in Python, JavaScript, and TypeScript shines through. His contributions in the field of AI and serverless computing have been instrumental in advancing real-time AI solutions. With 543 commits in the last three years, his consistency and growth are evident. Notably, Rahul's collaborations with 12 other developers underscore his commitment to teamwork and innovation, particularly in developing robust chatbot solutions and cutting-edge AI tools. Based on his recent contributions, it's clear that Rahul is at the forefront of serverless AI technologies, pushing boundaries in both functionality and scalability.
    """

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

    # Remove the prompt from the generated text
    if "Generate a detailed and engaging summary for the following GitHub profile:" in generated_text:
        generated_text = generated_text.split("Generate a detailed and engaging summary for the following GitHub profile:")[1].strip()

    return generated_text
