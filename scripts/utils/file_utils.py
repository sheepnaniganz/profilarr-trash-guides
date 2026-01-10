import json
import os


def iterate_json_files(input_dir):
    """
    Generator that yields (file_path, file_stem, data) tuples for all JSON files
    in the input directory and its subdirectories.

    Args:
        input_dir: Directory to search for JSON files

    Yields:
        Tuple of (file_path, file_stem, data) where:
        - file_path: Full path to the JSON file
        - file_stem: Filename without extension
        - data: Parsed JSON data
    """
    for root, _, files in os.walk(input_dir):
        for filename in sorted(files):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(root, filename)
            file_stem = os.path.splitext(filename)[0]
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            yield file_path, file_stem, data
