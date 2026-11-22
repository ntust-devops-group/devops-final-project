import json
from pathlib import Path

FLAGS_PATH = Path(__file__).with_name("flags.json")


def load_flags():
    with FLAGS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def is_enabled(feature):
    flags = load_flags()
    return flags.get(feature, {}).get("enabled", False)


if __name__ == "__main__":
    print("=== Feature Toggle Status ===")

    print("Quick Submit:",
          "ON" if is_enabled("quick_submit") else "OFF")

    print("CSV Export:",
          "ON" if is_enabled("csv_export") else "OFF")
