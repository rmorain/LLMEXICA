import json
import os

EMOTIONAL_LINK_TYPES = {"non-romantic": 1, "romantic": 2}

TENSION_TYPES = {
    "character_dead": "Ad",
    "life_at_risk": "Lr",
    "life_normal": "Ln",
    "health_at_risk": "Hr",
    "health_normal": "Hn",
    "prisoner": "Pr",
    "prisoner_freed": "Pf",
    "clashing_emotions": "Ce",
    "love_competition": "Lc",
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
            # If there are no postconditions, skip the action
            if (
                len(action["postconditions"]["emotional_links"]) == 0
                and len(action["postconditions"]["tensions"]) == 0
            ):
                continue
            # Get action name, subject, and object
            action_name = action["action"]
            subject = action["subject"] if action["subject"] != "-" else ""
            object = action["object"] if action["object"] != "-" else ""
            # Replace spaces with underscores
            subject = subject.replace(" ", "_")
            object = object.replace(" ", "_")
            # Remove characters that are not alpha or underscore
            subject = "".join(c for c in subject if c.isalnum() or c == "_")
            object = "".join(c for c in object if c.isalnum() or c == "_")
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
            # If there are no postconditions, skip the action
            if (
                len(action["postconditions"]["emotional_links"]) == 0
                and len(action["postconditions"]["tensions"]) == 0
            ):
                continue
            # Action name, num characters
            action_name = action["action"]
            num_characters = action["n_characters"]
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
                    pre_type = EMOTIONAL_LINK_TYPES[precondition["type"]]
                    file.write(
                        f"E {precondition['from']} {precondition['to']} {magnitude} {pre_type}\n"
                    )
                # Write tensions
                # Type, from, to
                for tension in tensions:
                    pre_type = TENSION_TYPES[tension["type"]]
                    file.write(f"T {pre_type} {tension['from']} {tension['to']}\n")
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
                post_type = EMOTIONAL_LINK_TYPES[postcondition["type"]]
                file.write(
                    f"E {postcondition['from']} {postcondition['to']} {magnitude} {post_type}\n"
                )
            # Write tensions
            # Type, from, to
            for tension in tensions:
                post_type = TENSION_TYPES[tension["type"]]
                file.write(f"T {post_type} {tension['from']} {tension['to']}\n")
            file.write("\n")

    print(f"PAD file created at {file_path}")
    return file_path


def emotion_helper(emotion_type, magnitude, source, target, subject, object):
    if target == "a":
        target = subject
    elif target == "b":
        target = object
    elif target == "-":
        target = "nobody"
    elif target == "*":
        target = "anybody"
    if source == "a":
        source = subject
    elif source == "b":
        source = object
    elif source == "-":
        source = "nobody"
    elif source == "*":
        source = "anybody"
    s = f"it is likely that {source} "
    if emotion_type == "non-romantic":
        if magnitude <= -3:
            s += "hates"
        elif magnitude == -2:
            s += "dislikes"
        elif magnitude == -1:
            s += "somewhat dislikes"
        elif magnitude == 1:
            s += "somewhat likes"
        elif magnitude == 2:
            s += "likes"
        elif magnitude >= 3:
            s += "really likes"
    elif emotion_type == "romantic":
        if magnitude <= -3:
            s += "is completely not in love with"
        elif magnitude == -2:
            s += "is not in love with"
        elif magnitude == -1:
            s += "is somewhat not in love with"
        elif magnitude == 1:
            s += "is somewhat in love with"
        elif magnitude == 2:
            s += "is in love with"
        elif magnitude >= 3:
            s += "is deeply in love with"
    s += f" {target}."
    return s


def tension_helper(tension_type, source, target, subject, object):
    if target == "a":
        target = subject
    elif target == "b":
        target = object
    elif target == "-":
        target = "nobody"
    elif target == "*":
        target = "anybody"
    if source == "a":
        source = subject
    elif source == "b":
        source = object
    elif source == "-":
        source = "nobody"
    elif source == "*":
        source = "anybody"
    s = f" {source} has caused "
    if tension_type == "character_dead":
        s += f"{target} to die."
    elif tension_type == "life_at_risk":
        s += f"{target}'s life to be at risk."
    elif tension_type == "life_normal":
        s += f"{target}'s life to no longer be at risk."
    elif tension_type == "health_at_risk":
        s += f"{target}'s health to be at risk."
    elif tension_type == "health_normal":
        s += f"{target}'s health to no longer be at risk."
    elif tension_type == "prisoner":
        s += f"{target} to be a prisoner."
    elif tension_type == "prisoner_freed":
        s += f"{target} to no longer be a prisoner."
    return s


def create_survey_questions(story_action_json, write_dir):
    with open(os.path.join(write_dir, "survey_questions.txt"), "w") as file:
        for action in story_action_json:
            # If there are no postconditions, skip the action
            if (
                len(action["postconditions"]["emotional_links"]) == 0
                and len(action["postconditions"]["tensions"]) == 0
            ):
                continue
            # Action name, num characters
            action_name = action["action"]
            subject = action["subject"].replace("_", " ")
            object = action["object"].replace("_", " ")
            # For each precondition, write a question
            if "preconditions" in action:
                emotional_preconditions = action["preconditions"]["emotional_links"]
                tensions = action["preconditions"]["tensions"]
                if len(emotional_preconditions) > 0 or len(tensions) > 0:
                    for precondition in emotional_preconditions:
                        source = precondition["from"]
                        target = precondition["to"]
                        magnitude = precondition["magnitude"]
                        pre_type = precondition["type"]
                        precondition = emotion_helper(
                            pre_type, magnitude, source, target, subject, object
                        )
                        file.write(
                            f"Before {subject} {action_name} {object}, {precondition}\n"
                        )
                    # Write tensions
                    # Type, from, to
                    for tension in tensions:
                        source = tension["from"]
                        target = tension["to"]
                        tension_type = tension["type"]
                        tension = tension_helper(
                            tension_type, source, target, subject, object
                        )
                        file.write(
                            f"Before {subject} {action_name} {object}, {tension}\n"
                        )
            # Postconditions
            emotional_postconditions = action["postconditions"]["emotional_links"]
            tensions = action["postconditions"]["tensions"]
            # Write emotional postconditions
            # Type, magnitude, from, to
            for postcondition in emotional_postconditions:
                source = postcondition["from"]
                target = postcondition["to"]
                magnitude = postcondition["magnitude"]
                post_type = postcondition["type"]
                postcondition = emotion_helper(
                    post_type, magnitude, source, target, subject, object
                )
                file.write(f"After {subject} {action_name} {object}, {postcondition}\n")
            # Write tensions
            # Type, from, to
            for tension in tensions:
                if "from" not in tension:
                    tension["from"] = "-"
                if "to" not in tension:
                    tension["to"] = "-"
                source = tension["from"]
                target = tension["to"]
                tension_type = tension["type"]
                tension = tension_helper(tension_type, source, target, subject, object)
                file.write(f"After {subject} {action_name} {object}, {tension}\n")
            file.write("\n")


if __name__ == "__main__":
    # Example usage
    # json_dir = "artifacts/jaguar_knight/test/"
    # # Load json file
    # with open(json_dir + "story_actions.json", "r") as file:
    #     story_json = json.load(file)
    #     print(story_json)
    # create_dps(story_json, json_dir)

    # create_pad(story_json, json_dir)

    # Get dirs of latest artifacts in the artifacts folder for each story
    stories = os.listdir("artifacts")
    for story in stories:
        story_dir = os.path.join("artifacts", story)
        if not os.path.isdir(story_dir):
            continue
        # Get the latest dir
        latest_dir = max(
            [
                os.path.join(story_dir, d)
                for d in os.listdir(story_dir)
                if os.path.isdir(os.path.join(story_dir, d))
            ],
            key=os.path.getmtime,
        )
        print(latest_dir)
        # Load json file
        with open(os.path.join(latest_dir, "story_actions.json"), "r") as file:
            story_json = json.load(file)
            print(story_json)
        create_survey_questions(story_json, latest_dir)
