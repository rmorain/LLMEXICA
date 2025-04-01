import os
from datetime import datetime

from ollama import ChatResponse, chat


def log_response(
    response: ChatResponse, story_name: str, date_time: str, file_name: str
):
    # Save response to a file in the responses directory
    # `responses/<story_name>/<date_time>/<file_name>`
    # Create directory if it does not exist
    directory = f"responses/{story_name}/{date_time}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{file_name}", "w") as f:
        f.write(response.message.content)
    print("Saved response to file: ", f.name)


def chat_round(model, messages, story_name, date_time, file_name):
    response = chat(
        model=model,
        messages=messages,
    )
    print(response.message.content)
    log_response(response, story_name, date_time, file_name)
    messages.append(
        {
            "role": response.message.role,
            "content": response.message.content,
        },
    )
    return response, messages


def parse_response_json(response: str):
    """Given a response, parse it and return a JSON object."""
    # Split response into lines
    lines = response.split("\n")
    # Initialize JSON object
    json_object = {}
    # Parse response
    for line in lines:
        # Split line into key and value
        key, value = line.split(": ")
        # Add key and value to JSON object
        json_object[key] = value
    return json_object


def main():
    model = os.getenv("OLLAMA_MODEL")
    print("OLLAMA MODEL: ", model)
    # Get date and time
    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

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

    # Load story from stories/jaguar_knight.txt
    story = ""
    story_name = "jaguar_knight"
    with open(f"stories/{story_name}.txt", "r") as f:
        print("Reading story from file: ", f.name)
        story = f.read()
        print("Story: ", story)

    # Get story actions
    # Load story action prompts from prompts/story_action.txt
    story_action_prompt = ""
    with open("prompts/story_action.txt", "r") as f:
        print("Reading story action prompt from file: ", f.name)
        story_action_prompt = f.read()
    # Add story to the prompt
    story_action_prompt = story_action_prompt.replace("<STORY>", story)
    print("Story Action Prompt: ", story_action_prompt)
    # Build messages list with the story action prompt
    messages = [
        {
            "role": "user",
            "content": story_action_prompt,
        },
    ]
    response, messages = chat_round(
        model, messages, story_name, date_time, "story_action.txt"
    )
    # Get story DPS
    # Read story DPS prompt from prompts/dps.txt
    dps_prompt = ""
    with open("prompts/dps.txt", "r") as f:
        print("Reading DPS prompt from file: ", f.name)
        dps_prompt = f.read()
    # Continue conversation with the DPS prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": dps_prompt,
        },
    )
    response, messages = chat_round(model, messages, story_name, date_time, "dps.txt")

    # Parse response for txt file

    # Get emotional preconditions
    # Read emotional preconditions prompt from prompts/emotional_preconditions.txt
    emotional_preconditions_prompt = ""
    with open("prompts/emotional_preconditions.txt", "r") as f:
        print("Reading emotional preconditions prompt from file: ", f.name)
        emotional_preconditions_prompt = f.read()
    # Continue conversation with the emotional preconditions prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": emotional_preconditions_prompt,
        },
    )
    response, messages = chat_round(
        model,
        messages,
        story_name,
        date_time,
        "emotional_preconditions.txt",
    )
    # Parse response for JSON file
    json_object = parse_response_json(response.message.content)
    print(json_object)
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/emotional_preconditions.json",
        "w",
    ) as f:
        f.write(response.message.content)
    print("Saved JSON object to file: ", f.name)

    # Get tension preconditions
    # Read tension preconditions prompt from prompts/tension_preconditions.txt
    tension_preconditions_prompt = ""
    with open("prompts/tension_preconditions.txt", "r") as f:
        print("Reading tension preconditions prompt from file: ", f.name)
        tension_preconditions_prompt = f.read()
    # Continue conversation with the tension preconditions prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": tension_preconditions_prompt,
        },
    )
    response, messages = chat_round(
        model,
        messages,
        story_name,
        date_time,
        "tension_preconditions.txt",
    )
    # Parse response for JSON file
    json_object = parse_response_json(response.message.content)
    print(json_object)
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/tension_preconditions.json",
        "w",
    ) as f:
        f.write(response.message.content)
    print("Saved JSON object to file: ", f.name)

    # Get postconditions
    # Read postconditions prompt from prompts/postconditions.txt
    postconditions_prompt = ""
    with open("prompts/postconditions.txt", "r") as f:
        print("Reading postconditions prompt from file: ", f.name)
        postconditions_prompt = f.read()
    # Continue conversation with the postconditions prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": postconditions_prompt,
        },
    )
    response, messages = chat_round(
        model, messages, story_name, date_time, "postconditions.txt"
    )
    # Parse response for JSON file
    json_object = parse_response_json(response.message.content)
    print(json_object)
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/postconditions.json",
        "w",
    ) as f:
        f.write(response.message.content)
    print("Saved JSON object to file: ", f.name)

    # Get verify prompt
    # Read verify prompt from prompts/verify.txt
    verify_prompt = ""
    with open("prompts/verify.txt", "r") as f:
        print("Reading verify prompt from file: ", f.name)
        verify_prompt = f.read()
    # Continue conversation with the verify prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": verify_prompt,
        },
    )
    response, messages = chat_round(
        model, messages, story_name, date_time, "verify.txt"
    )
    # Parse response for JSON file
    json_object = parse_response_json(response.message.content)
    print(json_object)
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/verify.json",
        "w",
    ) as f:
        f.write(response.message.content)

    # Get pad prompt
    # Read pad prompt from prompts/pad.txt
    pad_prompt = ""
    with open("prompts/pad.txt", "r") as f:
        print("Reading pad prompt from file: ", f.name)
        pad_prompt = f.read()
    # Continue conversation with the pad prompt including previous messages
    messages.append(
        {
            "role": "user",
            "content": pad_prompt,
        },
    )
    response, messages = chat_round(model, messages, story_name, date_time, "pad.txt")
    # Parse response for JSON file
    json_object = parse_response_json(response.message.content)
    print(json_object)
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/pad.json",
        "w",
    ) as f:
        f.write(response.message.content)
    print("Saved JSON object to file: ", f.name)


if __name__ == "__main__":
    main()
