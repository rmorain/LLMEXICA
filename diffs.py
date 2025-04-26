import difflib
import glob
import os
from collections import defaultdict
from difflib import SequenceMatcher


def count_changed_lines(original_file_path: str, corrected_file_path: str) -> int:
    """
    Computes the number of lines changed between two text files.

    Args:
        original_file_path: Path to the original file.
        corrected_file_path: Path to the corrected file.

    Returns:
        The total number of added and deleted lines.
    """
    try:
        with open(original_file_path, "r") as f1, open(corrected_file_path, "r") as f2:
            original_lines = f1.readlines()
            corrected_lines = f2.readlines()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return -1  # Indicate an error

    diff = difflib.unified_diff(
        original_lines,
        corrected_lines,
        fromfile=original_file_path,
        tofile=corrected_file_path,
        lineterm="",  # Avoid extra newlines in diff output
        n=0,  # Context lines - set to 0 if only interested in changes
    )

    changed_lines_count = 0
    for line in diff:
        # Skip header lines
        if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
            continue
        # Count added or deleted lines
        if line.startswith("+") or line.startswith("-"):
            changed_lines_count += 1

    return changed_lines_count


def smart_diff_analysis(original_lines, corrected_lines):
    sm = SequenceMatcher(None, original_lines, corrected_lines)
    opcodes = sm.get_opcodes()

    stats = {
        "unchanged": 0,
        "inserted": 0,
        "deleted": 0,
        "moved": 0,
        "modified": 0,
    }

    # Track lines that are inserted or deleted (we'll use them to detect moves)
    inserted_lines = defaultdict(list)
    deleted_lines = defaultdict(list)

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            stats["unchanged"] += i2 - i1
        elif tag == "replace":
            for i in range(i1, i2):
                stats["deleted"] += 1
                deleted_lines[original_lines[i].strip()].append(i)
            for j in range(j1, j2):
                stats["inserted"] += 1
                inserted_lines[corrected_lines[j].strip()].append(j)
        elif tag == "delete":
            for i in range(i1, i2):
                stats["deleted"] += 1
                deleted_lines[original_lines[i].strip()].append(i)
        elif tag == "insert":
            for j in range(j1, j2):
                stats["inserted"] += 1
                inserted_lines[corrected_lines[j].strip()].append(j)

    # Detect moves: a line both deleted and inserted
    moved_lines = set(inserted_lines.keys()) & set(deleted_lines.keys())
    for line in moved_lines:
        move_count = min(len(inserted_lines[line]), len(deleted_lines[line]))
        stats["moved"] += move_count
        stats["deleted"] -= move_count
        stats["inserted"] -= move_count

    return stats


# Example usage (optional):
if __name__ == "__main__":
    # Get the paths to all original and corrected files in the diffs directory
    original_files = glob.glob("diffs/*/original.txt")
    corrected_files = glob.glob("diffs/*/corrected.txt")
    dps_total_lines = 0
    pad_total_lines = 0
    dps_unchanged = 0
    pad_unchanged = 0
    for original_file, corrected_file in zip(original_files, corrected_files):
        with open(original_file) as f1, open(corrected_file) as f2:
            original_lines = [line.strip() for line in f1]
            corrected_lines = [line.strip() for line in f2]

        stats = smart_diff_analysis(original_lines, corrected_lines)
        if "dps" in original_file:
            dps_total_lines += len(original_lines)
            dps_unchanged += stats["unchanged"]
        elif "pad" in original_file:
            pad_total_lines += len(original_lines)
            pad_unchanged += stats["unchanged"]
        print(f"File: {original_file}")
        print(f"Unchanged lines: {stats['unchanged']}")
        print(
            f"Unchanged lines percentage: {stats['unchanged'] / len(original_lines) * 100:.2f}%"
        )
        print(f"Stats: {stats}")

    print(f"Total lines in dps files: {dps_total_lines}")
    print(f"Total unchanged lines in dps files: {dps_unchanged}")
    print(
        f"Unchanged percentage in dps files: {dps_unchanged / dps_total_lines * 100:.2f}%"
    )
    print(f"Total lines in pad files: {pad_total_lines}")
    print(f"Total unchanged lines in pad files: {pad_unchanged}")
    print(
        f"Unchanged percentage in pad files: {pad_unchanged / pad_total_lines * 100:.2f}%"
    )
