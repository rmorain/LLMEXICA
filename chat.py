import os

from ollama import ChatResponse, chat

model = os.getenv("OLLAMA_MODEL")
print("OLLAMA MODEL: ", model)

response: ChatResponse = chat(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print(response["message"]["content"])
# or access fields directly from the response object
print(response.message.content)
