def remove_html_tags(soup, tag, class_name):
    """Remove specified tags with the given class from the BeautifulSoup object."""
    for element in soup.find_all(tag, class_=class_name):
        element.decompose()
    return soup


def filter_html(soup, tag, class_name, limit=None):
    """Filter the HTML content based on the specified tag and class."""
    specific_elements = soup.find_all(tag, class_=class_name)

    if limit is not None:
        specific_elements = specific_elements[:limit]

    return specific_elements


def clean_html(soup):
    """Extract text from specific HTML elements and return each piece as a separate line in a list."""
    cleaned_lines = []

    # Define the relevant tags and classes you expect in the content
    relevant_tags = [
        ('h1', None),
        ('h2', None),
        ('p', None),
        ('li', None),
    ]

    for tag, class_name in relevant_tags:
        elements = soup.find_all(tag, class_=class_name) if class_name else soup.find_all(tag)
        for element in elements:
            # Replace non-breaking space with a normal space
            text = element.get_text(strip=True).replace('\xa0', ' ')

            # Handle superscripts: add space after each <sup>
            for sup in element.find_all('sup'):
                sup.insert_after(' ')  # Adding a space after the superscript

            # Clean up extra spaces created by the above replacement
            text = ' '.join(text.split())  # This removes any extra whitespace

            if text:  # Only append non-empty lines
                cleaned_lines.append(text)
                # print(text)  # Print each appended line

    return cleaned_lines


def file_name_from_url(url):
    url_elements = url.split("/")
    count = len(url_elements)

    return url_elements[count - 1] + ".txt"


@DeprecationWarning
def save_txt_as_file(text_list, filename):
    """Save the list of text lines to a .txt file."""
    with open(filename, 'w', encoding='utf-8') as file:
        for line in text_list:
            file.write(line + '\n')


def read_file_as_txt(filename):
    """Read a .txt file and return its contents as a list of text lines."""
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]
