import json
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


def log_artifact(artifact: str, story_name: str, date_time: str, file_name: str):
    # Save artifact to a file in the artifacts directory
    # `artifacts/<story_name>/<date_time>/<file_name>`
    # Create directory if it does not exist
    directory = f"artifacts/{story_name}/{date_time}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(f"{directory}/{file_name}", "w") as f:
        f.write(artifact)
    print("Saved artifact to file: ", f.name)


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


def verify_artifact(artifact, messages, model, story_name, date_time, artifact_type):
    if artifact is not None:
        return artifact, messages
    # Ask model to regenerate the PAD artifact
    if artifact_type == "JSON":
        regenerate_prompt = "There is an error extracting the JSON artifact from the previous response. Please regenerate the JSON artifact. Make sure to wrap the JSON artifact in ```json``` tags."
    else:
        regenerate_prompt = f"There is an error extracting the {artifact_type} artifact from the previous response. Please regenerate the {artifact_type} artifact. Make sure to wrap the {artifact_type} artifact in <{artifact_type}></{artifact_type}> tags."
    messages.append({"role": "user", "content": regenerate_prompt})
    response, messages = chat_round(model, messages, story_name, date_time, "pad.txt")
    artifact = extract_substring_between(
        response.message.content, f"<{artifact_type}>", f"</{artifact_type}>"
    )
    print("Regenerated Artifact: ", artifact)

    return artifact, messages


def extract_substring_between(text, start_substring, end_substring):
    """
    Extracts the substring between two specified substrings within a larger string.

    Args:
        text: The string to search within.
        start_substring: The substring marking the start of the extraction.
        end_substring: The substring marking the end of the extraction.

    Returns:
        The extracted substring, or None if either start or end substring is not found.
    """
    # Remove everything between <think> and </think> from the text
    think_end_index = text.find("</think>")
    if think_end_index != -1:
        text = text[think_end_index + len("</think>") :]

    start_index = text.find(start_substring)
    if start_index == -1:
        return None

    end_index = text.find(end_substring, start_index + len(start_substring))
    if end_index == -1:
        return None

    return text[start_index + len(start_substring) : end_index]


def parse_response_json(response_content):
    json_string = extract_substring_between(response_content, "```json", "```")
    print("JSON string: ", json_string)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: ", e)
        json_object = None
    return json_object


def main():
    # Get start time
    start_time = datetime.now()
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
    dps_artifact = extract_substring_between(
        response.message.content, "<DPS>", "</DPS>"
    )
    print("DPS Artifact: ", dps_artifact)
    # Verify DPS artifact
    dps_artifact, messages = verify_artifact(
        dps_artifact, messages, model, story_name, date_time, "DPS"
    )
    # Save DPS artifact to a file
    log_artifact(dps_artifact, story_name, date_time, "dps.txt")

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
    json_string = extract_substring_between(response.message.content, "```json", "```")
    print("JSON string: ", json_string)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: ", e)
        json_object = None
    # Save JSON object to a file
    with open(
        f"responses/{story_name}/{date_time}/emotional_preconditions.json",
        "w",
    ) as f:
        json.dump(json_object, f, indent=4)
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
    # Verify JSON object
    json_object, messages = verify_artifact(
        json_object, messages, model, story_name, date_time, "JSON"
    )
    # Save JSON object as artifact
    log_artifact(json.dumps(json_object), story_name, date_time, "story_actions.json")

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
    # Parse response for PAD artifact
    pad_artifact = extract_substring_between(
        response.message.content, "<PAD>", "</PAD>"
    )
    print("PAD Artifact: ", pad_artifact)
    # Verify PAD artifact
    pad_artifact, messages = verify_artifact(
        pad_artifact, messages, model, story_name, date_time, "PAD"
    )
    # Save PAD artifact to a file
    log_artifact(pad_artifact, story_name, date_time, "pad.txt")

    # Print elapsed time
    elapsed_time = datetime.now() - start_time
    print("Elapsed time: ", elapsed_time)


if __name__ == "__main__":
    main()
