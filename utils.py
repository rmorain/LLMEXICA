import json
import os

EMOTIONAL_LINK_TYPES = {"friendship": 1, "love": 2}

TENSION_TYPES = {
    "character_dead": "Ad",
    "Lr": "life_at_risk",
    "Hr": "health_at_risk",
    "Pr": "prisoner",
    "Ce": "clashing_emotions",
    "Lc": "love_competition",
}


def create_dps(story_json, json_dir):
    # Function to convert a story in JSON format to DPS language format
    # Create the DPS file
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    # Open the file in write mode
    file_path = os.path.join(json_dir, "dps.txt")
    with open(file_path, "w") as file:
        # Write the DPS header
        file.write("STO\n")
        for action in story_json:
            # Get action name, subject, and object
            action_name = action["action"]
            subject = action["subject"] if action["subject"] != "-" else ""
            object = action["object"] if action["object"] != "-" else ""
            # Write the action to the file
            file.write(f"{subject} {action_name} {object}".strip() + "\n")
    print(f"DPS file created at {file_path}")
    return file_path


def create_pad(story_json, json_dir):
    # Function to convert a story in JSON format to PAD language format
    # Create the PAD file
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    # Open the file in write mode
    file_path = os.path.join(json_dir, "pad.txt")
    with open(file_path, "w") as file:
        for action in story_json:
            # Action name, num characters
            action_name = action["action"]
            num_characters = action["num_characters"]
            file.write(f"ACT {action_name} {num_characters}\n")
            # Preconditions (if any)
            emotional_preconditions = action["preconditions"]["emotional_links"]
            tensions = action["preconditions"]["tensions"]
            if len(emotional_preconditions) > 0 or len(tensions) > 0:
                file.write("PRE\n")
                # Write emotional preconditions
                # Type, magnitude, from, to
                for precondition in emotional_preconditions:
                    magnitude = precondition["magnitude"]
                    if magnitude > 0:
                        magnitude = "+" + str(magnitude)
                    elif magnitude < 0:
                        magnitude = "-" + str(magnitude)
                    pre_type = EMOTIONAL_LINK_TYPES[precondition["type"]]
                    file.write(
                        f"E {precondition['from']} {precondition['to']} {magnitude} {pre_type}\n"
                    )
                # Write tensions
                # Type, from, to
                for tension in tensions:
                    pre_type = TENSION_TYPES[tension["type"]]
                    file.write(f"T {tension['from']} {tension['to']} {pre_type}\n")
            # Postconditions
            emotional_postconditions = action["postconditions"]["emotional_links"]
            tensions = action["postconditions"]["tensions"]
            file.write("POS\n")
            # Write emotional postconditions
            # Type, magnitude, from, to
            for postcondition in emotional_postconditions:
                magnitude = postcondition["magnitude"]
                if magnitude > 0:
                    magnitude = "+" + str(magnitude)
                elif magnitude < 0:
                    magnitude = "-" + str(magnitude)
                post_type = EMOTIONAL_LINK_TYPES[postcondition["type"]]
                file.write(
                    f"E {postcondition['from']} {postcondition['to']} {magnitude} {post_type}\n"
                )
            # Write tensions
            # Type, from, to
            for tension in tensions:
                post_type = TENSION_TYPES[tension["type"]]
                file.write(f"T {tension['from']} {tension['to']} {post_type}\n")

    print(f"PAD file created at {file_path}")
    return file_path


if __name__ == "__main__":
    # Example usage
    json_dir = "artifacts/jaguar_knight/test/"
    # Load json file
    with open(json_dir + "story_actions.json", "r") as file:
        story_json = json.load(file)
        print(story_json)
    create_dps(story_json, json_dir)
