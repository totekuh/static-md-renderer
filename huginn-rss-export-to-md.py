#!/usr/bin/env python3
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

    # Find sections that start with '## Agent:'
    agent_sections = re.findall(r'## Agent: (.*?) \(\d+ entries\)\n(.*?)\n(?=## Agent:|$)', content, re.DOTALL)

    parsed_entries = {}
    for agent, entries_block in agent_sections:
        # Remove the number of entries from the agent line
        agent = agent.strip()

        # Find all titles within this agent's section
        titles_urls = re.findall(r'\*\*(.*?)\*\* - \[(.*?)\]\((.*?)\)', entries_block)

        for title, _, url in titles_urls:
            domain = url.split("://")[1].split("/")[0]
            if agent not in parsed_entries:
                parsed_entries[agent] = {}
            if domain not in parsed_entries[agent]:
                parsed_entries[agent][domain] = []
            parsed_entries[agent][domain].append({'title': title, 'url': url})

    return parsed_entries


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
        domain = url.split("://")[1].split("/")[0]
        agent = agent.strip()
        if agent not in new_entries:
            new_entries[agent] = {}
        if domain not in new_entries[agent]:
            new_entries[agent][domain] = []
        new_entries[agent][domain].append({'title': title, 'url': url.strip()})
    return new_entries


def combine_and_dedupe(existing_entries, new_entries):
    for agent, domains in new_entries.items():
        if agent not in existing_entries:
            existing_entries[agent] = domains
        else:
            for domain, entries in domains.items():
                if domain not in existing_entries[agent]:
                    existing_entries[agent][domain] = entries
                else:
                    existing_titles = {entry['title'] for entry in existing_entries[agent][domain]}
                    for entry in entries:
                        if entry['title'] not in existing_titles:
                            existing_entries[agent][domain].append(entry)
    return existing_entries


def store_to_markdown(combined_data, output_dir, date_str):
    filename = os.path.join(output_dir, f"{date_str}-Huginn-Data-Feed.md")

    markdown_content = f"""---
layout: post
title: Huginn RSS Report
categories: huginn update
date: {date_str} 
---
""" + """
* auto-gen TOC:
{:toc}

"""

    # Sort the combined data by agent and then domain
    for agent in sorted(combined_data.keys()):
        entries_per_agent = sum(len(entries) for entries in combined_data[agent].values())
        markdown_content += f"## Agent: {agent} ({entries_per_agent} entries)\n"
        for domain in sorted(combined_data[agent].keys()):
            markdown_content += f"### Domain: {domain}\n"
            for entry in sorted(combined_data[agent][domain], key=lambda x: x['title']):
                entry_str = f"**{entry['title']}** - [{entry['url']}]({entry['url']})\n\n"
                if entry_str in markdown_content:
                    print(f"Duplicate detected: {entry_str}")
                    continue
                else:
                    markdown_content += entry_str

    with open(filename, 'w') as f:
        f.write(markdown_content)
        print(f"Data saved to {filename}")


def get_arguments():
    from argparse import ArgumentParser

    parser = ArgumentParser("Convert Hugin RSS Feads to Markdown")
    parser.add_argument("-i",
                        '--input',
                        dest='input',
                        required=True,
                        type=str,
                        help='Specify the input file produced by Huginn')
    parser.add_argument("-od",
                        '--output-dir',
                        dest='output_dir',
                        required=True,
                        type=str,
                        help='Specify the output directory to write converted files to')
    return parser.parse_args()


def main():
    options = get_arguments()

    input_file = options.input
    output_dir = options.output_dir

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


if __name__ == "__main__":
    main()
