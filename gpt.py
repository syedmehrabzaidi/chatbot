# from azure.openai import AzureOpenAI
import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv

load_dotenv()



endpoint = os.getenv("ENDPOINT_URL", "https://openai-dev-model.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-35-turbo")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

print("------------subscription_key------------",subscription_key)

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
