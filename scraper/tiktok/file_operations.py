import pandas as pd
import json


def save_to_txt(text_list, filename):
    """Save the list of text lines to a .txt file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for line in text_list:
            file.write(line + '\n')


def save_to_csv(data, filename):
    # Create a DataFrame
    df = pd.DataFrame(data, columns=["Description"])

    # Remove duplicate descriptions
    df = df.drop_duplicates(subset=["Description"], keep="first")

    # Save to CSV
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Data saved to {filename}")


def save_to_json(data, filename):
    """Save data to a JSON file with the specified structure."""
    # Remove duplicate entries based on the text content
    unique_data = []
    seen_texts = set()

    for text in data:
        if text not in seen_texts:
            unique_data.append({"text": text})
            seen_texts.add(text)

    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(unique_data, file, ensure_ascii=False, indent=4)

    print(f"Data saved to {filename}")