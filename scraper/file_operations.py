def save_txt_as_file(text_list, filename):
    """Save the list of text lines to a .txt file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for line in text_list:
            file.write(line + '\n')
