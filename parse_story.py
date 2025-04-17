import json
import os
from datetime import datetime

import absl.app
import absl.flags
from ollama import ChatResponse, chat

from utils import create_dps, create_pad

FLAGS = absl.flags.FLAGS
absl.flags.DEFINE_list(
    "story_names", None, "Comma-separated list of story names to process."
)


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
    if artifact is None:
        # Ask model to regenerate the PAD artifact
        if artifact_type == "JSON":
            regenerate_prompt = "There is an error extracting the JSON artifact from the previous response. Please regenerate the JSON artifact. Make sure to wrap the JSON artifact in ```json``` tags."
        else:
            regenerate_prompt = f"There is an error extracting the {artifact_type} artifact from the previous response. Please regenerate the {artifact_type} artifact. Make sure to wrap the {artifact_type} artifact in <{artifact_type}></{artifact_type}> tags."
        messages.append({"role": "user", "content": regenerate_prompt})
        response, messages = chat_round(
            model, messages, story_name, date_time, "pad.txt"
        )
        artifact = parse_response_json(
            response.message.content, model, messages, story_name, date_time
        )
        print("Regenerated Artifact: ", artifact)
    else:
        # Check if each action in the artifact has at least one postcondition
        actions_with_no_postconditions = []
        for action in artifact:
            if (
                len(action["postconditions"]["emotional_links"]) == 0
                and len(action["postconditions"]["tensions"]) == 0
            ):
                actions_with_no_postconditions.append(action["action"])
        if len(actions_with_no_postconditions) > 0:
            print(
                "The following actions have no postconditions: ",
                actions_with_no_postconditions,
            )
            regenerate_prompt = f"The following actions have no postconditions: \n\n{actions_with_no_postconditions}.\n Please regenerate the JSON object to include postconditions for these actions. Or if the action has no relevant postconditions, remove the action from the JSON object. Make sure to wrap the JSON object in ```json``` tags."
            messages.append({"role": "user", "content": regenerate_prompt})
            response, messages = chat_round(
                model, messages, story_name, date_time, "regen_post.txt"
            )
            artifact = parse_response_json(
                response.message.content, model, messages, story_name, date_time
            )
            print("Regenerated Artifact: ", artifact)
        # If an action has any emotional links, make sure `subject` and `object` are not '-'
        actions_with_invalid_links = []
        for action in artifact:
            if len(action["postconditions"]["emotional_links"]) > 0 or (
                "preconditions" in action
                and len(action["preconditions"]["emotional_links"]) > 0
            ):
                if ("subject" in action and action["subject"] == "-") or (
                    "object" in action and action["object"] == "-"
                ):
                    actions_with_invalid_links.append(action["action"])
        if len(actions_with_invalid_links) > 0:
            print(
                "The following actions have emotional links but are missing a `subject` or `object`: ",
                actions_with_invalid_links,
            )
            regenerate_prompt = f"The following actions have emotional links but are missing a `subject` or `object`: \n\n{actions_with_invalid_links}.\n Please regenerate the JSON object to include the correct `subject` or `object` values for these actions and update `n_characters` appropriately. If after review, there are no reasonable direct or indirect objects to set `object`, remove the problematic emotional links from the JSON object. Make sure to wrap the JSON object in ```json``` tags."
            messages.append({"role": "user", "content": regenerate_prompt})
            response, messages = chat_round(
                model, messages, story_name, date_time, "regen_links.txt"
            )
            artifact = parse_response_json(
                response.message.content, model, messages, story_name, date_time
            )
            print("Regenerated Artifact: ", artifact)

        # If an action has a tension but `to` is '-'
        actions_with_invalid_tensions = []
        for action in artifact:
            for tension in action["postconditions"]["tensions"]:
                if tension["to"] == "-":
                    actions_with_invalid_tensions.append(action["action"])
        if len(actions_with_invalid_tensions) > 0:
            print(
                "The following actions have tensions but are missing a `to`: ",
                actions_with_invalid_tensions,
            )
            regenerate_prompt = f"The following actions have tensions but are missing a `to`: \n\n{actions_with_invalid_tensions}.\n Please regenerate the JSON object to include the correct `to` values for these actions. `to` must be set to 'a' if the subject character is receiving the tension or 'b' if the object character is receiving the tension. It is illogical to set `to` to '-' meaning no character is receiving the tension. If no character is receiving the tension, remove the problematic tension. Also make sure `from` refers to the character ('a' or 'b') causing the tension. Make sure to wrap the JSON object in ```json``` tags."
            messages.append({"role": "user", "content": regenerate_prompt})
            response, messages = chat_round(
                model, messages, story_name, date_time, "regen_tensions.txt"
            )
            artifact = parse_response_json(
                response.message.content, model, messages, story_name, date_time
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


def parse_response_json(response_content, model, messages, story_name, date_time):
    json_string = extract_substring_between(response_content, "```json", "```")
    print("JSON string: ", json_string)
    try:
        json_object = json.loads(json_string)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: ", e)
        json_object = None
        # Prompt the model to regenerate the JSON object
        regenerate_prompt = f"There is an error extracting the JSON object from the previous response. Here is the error: \n\n```{e}\n```\n\n Please regenerate the JSON object to correct the error. Make sure to wrap the JSON object in ```json``` tags."
        messages.append({"role": "user", "content": regenerate_prompt})
        response, messages = chat_round(
            model, messages, story_name, date_time, "regen.txt"
        )
        json_object = json.loads(response.message.content)
        print("Regenerated JSON: ", json_object)
    return json_object


def process_story(story_name: str):
    # Get start time
    start_time = datetime.now()
    model = os.getenv("OLLAMA_MODEL")
    print("OLLAMA MODEL: ", model)
    # Get date and time
    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Load story from stories/<story_name>.txt
    story = ""
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
    json_object = parse_response_json(
        response.message.content, model, messages, story_name, date_time
    )
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
    json_object = parse_response_json(
        response.message.content, model, messages, story_name, date_time
    )
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
    json_object = parse_response_json(
        response.message.content, model, messages, story_name, date_time
    )
    print(json_object)
    # Verify JSON object
    json_object, messages = verify_artifact(
        json_object, messages, model, story_name, date_time, "JSON"
    )
    # Save JSON object as artifact
    log_artifact(json.dumps(json_object), story_name, date_time, "story_actions.json")

    json_dir = os.path.join("artifacts", story_name, date_time)
    # Create DPS file
    try:
        create_dps(json_object, json_dir)
        # Create PAD file
        create_pad(json_object, json_dir)
    except KeyError as error:
        regenerate_prompt = f"There is an error extracting data from the JSON object from the previous response. Here is the error: \n\n```{error}\n```\n\n Please regenerate the JSON object to correct the error. Make sure to wrap the JSON artifact in ```json``` tags."

        messages.append({"role": "user", "content": regenerate_prompt})
        response, messages = chat_round(
            model, messages, story_name, date_time, "pad.txt"
        )
        json_object = parse_response_json(
            response.message.content, model, messages, story_name, date_time
        )
        print("Regenerated JSON: ", json_object)
        create_dps(json_object, json_dir)
        # Create PAD file
        create_pad(json_object, json_dir)

    # Print elapsed time
    elapsed_time = datetime.now() - start_time
    print("Elapsed time: ", elapsed_time)


def process_all_stories():
    # Get all stories in the stories directory
    stories = os.listdir("stories")
    for story in stories:
        if story.endswith(".txt"):
            story_name = story.split(".")[0]
            print("Processing story: ", story_name)
            process_story(story_name)


def main(argv):
    if FLAGS.story_names:
        for story_name in FLAGS.story_names:
            print("Processing story: ", story_name)
            process_story(story_name)
    else:
        process_all_stories()


if __name__ == "__main__":
    absl.app.run(main)
