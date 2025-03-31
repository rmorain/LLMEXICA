import os

from ollama import ChatResponse, chat


def main():
    model = os.getenv("OLLAMA_MODEL")
    print("OLLAMA MODEL: ", model)

    # Test chat with a single message
    response: ChatResponse = chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Does the sun rise in the west? Just answer yes or no.",
            },
        ],
    )
    print(response.message.content)

    # Load story from file


if __name__ == "__main__":
    main()
