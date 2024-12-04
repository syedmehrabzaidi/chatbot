# from azure.openai import AzureOpenAI
import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv

load_dotenv()



endpoint = os.getenv("ENDPOINT_URL", "https://openai-dev-model.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")


# Initialize the client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# Define the request data
# request_data = {
#     "entry_type": "professional",
#     "description": "i am developer"
# }
def gpt(request_data):
    # Create the completion request
    completion = client.chat.completions.create(
    model=deployment,
    messages=[
        {
            "role": "system",
            "content": "You are an AI assistant that helps people find information."
        },
        {
            "role": "user",
            "content": f"Generate a response in the following format based on the given data:\n\n"
                       f"Request Data:\n{request_data}\n\n"
                       f"Response Format:\n{{\n"
                       f"    \"company_name\": \"\",\n"
                       f"    \"keywords\": \"\",\n"
                       f"    \"detail_description\": \"\"\n"
                       f"}}\n\n"
                       f"Generate the response based on the description provided."
        }
        ],
        max_tokens=800,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    # Parse the JSON response
    response_json = json.loads(completion.to_json())
    print("---messages----------------",response_json)


    # Extract the content field
    content = response_json['choices'][0]['message']['content']

    # Print the extracted content
    print(content)

    # If you need to return it in a specific format, you can parse the content string
    content_dict = json.loads(content)
    formatted_content = json.dumps(content_dict, indent=4)
    print(formatted_content)
    return formatted_content


def generate_cv_gpt(description: str) -> str:
    prompt = f"""
    Based on the following job description, generate CV pointers in STAR format for multiple companies.
    Job Description: {description}

    Provide output in the format:
    Company name:
    1. Pointer in STAR format
    2. Pointer in STAR format
    Company name:
    1. Pointer in STAR format
    2. Pointer in STAR format
    """

    response = client.chat.completions.create(
        model=deployment,
        # model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,  # Limit the token count as per requirement
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    print("-----response gpt----------------------------------",response)
    # Return GPT response content
    return response.choices[0].message.content


def generate_appraisal_pointers(from_date: str, to_date: str) -> str:
    # Formulate the GPT prompt
    prompt = f"""
    Based on the given date range from {from_date} to {to_date}, generate appraisal report pointers in the following format:
    
    Appraisal Report pointers:
    Month / Year
    1. Pointer in STAR format
    2. Pointer in STAR format

    Month / Year
    1. Pointer in STAR format
    2. Pointer in STAR format
    """

    # Make the API call to OpenAI
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,  # Limit the token count as per requirement
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None,
        stream=False
    )
    
    # Extract GPT response content
    return response['choices'][0]['message']['content']