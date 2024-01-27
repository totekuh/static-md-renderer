import sys
import re
from datetime import datetime
import os

def escape_markdown(text):
    markdown_chars = "\\`*_{}[]()#+-.!|"
    for char in markdown_chars:
        text = text.replace(char, "\\" + char)
    return text

def parse_existing_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    existing_entries = re.findall(r'\*\*(.*?)\*\* - \[(.*?)\]\((.*?)\)', content)
    return {title: {'url': url} for title, _, url in existing_entries}

def parse_new_entries(input_content):
    entry_pattern = re.compile(
        r'%DATE_PUBLISHED%(.*?)%DATE_PUBLISHED%'
        r'%AGENT_NAME%(.*?)%AGENT_NAME%'
        r'%TITLE%(.*?)%TITLE%'
        r'%URL%(.*?)%URL%'
    )

    new_entries = {}
    for match in entry_pattern.finditer(input_content):
        date_published_str, agent, title, url = match.groups()
        try:
            datetime.strptime(date_published_str.strip(), '%Y-%m-%d %H:%M:%S %z')
        except ValueError:
            print(f"Invalid date format: {date_published_str}")
            continue

        title = escape_markdown(title.strip())
        new_entries[title] = {'url': url.strip()}
    return new_entries

def combine_and_dedupe(existing_entries, new_entries):
    for title, data in new_entries.items():
        if title not in existing_entries:
            existing_entries[title] = data
    return existing_entries

def store_to_markdown(combined_data, output_dir, date_str):
    filename = os.path.join(output_dir, f"{date_str}.md")

    markdown_content = ""
    for title, data in combined_data.items():
        markdown_content += f"**{title}** - [{data['url']}]({data['url']})\n\n"

    with open(filename, 'w') as f:
        header = f"""---
layout: post
title: "{date_str} Huginn RSS Report"
categories: huginn update
---""" + """
* auto-gen TOC:
{:toc}
        """
        f.write(header)
        f.write(markdown_content)
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} input_file output_dir".format(sys.argv[0]))
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        print("Input file does not exist")
        sys.exit(1)

    if not os.path.isdir(output_dir):
        print("Output directory does not exist")
        sys.exit(1)

    with open(input_file, 'r') as f:
        input_content = f.read()

    new_entries = parse_new_entries(input_content)
    existing_file = os.path.join(output_dir, f"{datetime.now().strftime('%Y-%m-%d')}.md")

    if os.path.exists(existing_file):
        existing_entries = parse_existing_file(existing_file)
    else:
        existing_entries = {}

    combined_data = combine_and_dedupe(existing_entries, new_entries)
    store_to_markdown(combined_data, output_dir, datetime.now().strftime('%Y-%m-%d'))
