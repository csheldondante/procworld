import os
import re
from typing import List


# Formatting notes:
# - Names cannot have square brackets in them, because of the '[^\]]' regex pattern


def sanitize_article_name(article_name: str) -> str:
    # In standard URLs, a comma is typically encoded as %2C. Use regex to do this replacement
    article_name = re.sub(r",", "%2C", article_name)
    article_name = re.sub(r" ", "%20", article_name)
    return article_name


def reverse_sanitize_article_name(article_name: str) -> str:
    # This needs to be kept in sync with the function above
    article_name = re.sub(r"%2C", ",", article_name)
    article_name = re.sub(r"%20", " ", article_name)
    return article_name


def convert_markdown_to_wikitext_links(markdown_text: str) -> str:
    # Use regular expressions to find all [text](link) patterns, and replace them with [[link|text]] or just [[link]] if text==link
    t = markdown_text
    t = re.sub(r"\[([^\]]*?)\]\(([^\]]*?)\.md\)", r"[[\2|\1]]", t)

    # reverse_sanitize_article_name text with in [[brackets]]
    t = re.sub(r"\[\[(.*?)\]\]", lambda m: f"[[{reverse_sanitize_article_name(m.group(1))}]]", t)

    # Find all links like [[\1|\1]] and replace them with just [[\1]], but only in cases where the text before and after the '|' are the same
    pipe_links = re.findall(r"\[\[([^\]]*?)\|([^\]]*?)\]\]", t)
    for pl in pipe_links:
        if custom_title_case(pl[0]) == pl[1]:
            t = t.replace(f"[[{pl[0]}|{pl[1]}]]", f"[[{reverse_sanitize_article_name(pl[0])}]]")

    return t


def convert_wikitext_to_markdown_links(wikitext: str) -> str:
    t = wikitext

    # Use regular expressions to convert [[link|text]] to [text](link)
    t = re.sub(r"\[\[([^\]]*?)\|([^\]]*?)\]\]", r"[\2](\1.md)", t)

    # Use regular expressions to convert [[link]] to [link](link)
    t = re.sub(r"\[\[(.*?)\]\]", r"[\1](\1.md)", t)

    # Find all article names and sanitize them, replacing them with the sanitized version
    article_names = re.findall(r"\[(.*?)\]\(.*?\)", t)
    for article_name in article_names:
        # if "," in article_name:
        #     print("Comma!")
        sanitized_name = sanitize_article_name(article_name)
        t = t.replace(f"[{article_name}]({article_name}.md)", f"[{article_name}]({sanitized_name}.md)")

    # Upper case the link portion of the Markdown link
    t = re.sub(r"\[(.*?)\]\((.*?)\)", lambda m: f"[{m.group(1)}]({custom_title_case(m.group(2))})", t)

    return t


def custom_title_case(s: str) -> str:
    #### WARNING!!!! ####

    # NOTE THAT IF YOU CHANGE THIS FUNCTION, IT MAY BREAK BACKWARDS COMPATIBILITY WITH EXISTING ARTICLES

    # This function is a custom title case function that is used to title case article names.
    # It is a modified version of the title() function, which is not sufficient for our purposes.
    # The title() function capitalizes the first letter of every word, but it also capitalizes
    # the first letter after every space, which we don't want. For example, "the" should not be
    # capitalized in the middle of a title, but it should be capitalized if it is the first word
    # of the title. This function does that.
    # https://en.wikipedia.org/wiki/Title_case

    put_funny_spaces_back = "%20" in s
    if put_funny_spaces_back:
        s = s.replace("%20", " ")

    s = s.title()
    non_title_words: List[str] = ["a", "an", "the", "and", "but", "or", "for", "nor", "on", "at", "to", "from", "by", "of", "in", "with", "as"]
    for word in non_title_words:
        s = s.replace(f" {word.title()} ", f" {word.lower()} ")
    # Make sure the first character is capitalized
    if len(s) > 0:
        s = s[0].upper() + s[1:]

    if put_funny_spaces_back:
        s = s.replace(" ", "%20")

    if s.endswith(".Md"):
        s = s[:-3] + ".md"

    return s


def fix_link_cases():
    # I had to write this because I accidentally generated a bunch of articles without title case names
    # Change the file name of all `.md` files in the current directory to be title case
    path = "../../multiverse/world1/wiki/docs"
    # for filename in os.listdir(path):
    #     if filename.endswith(".md"):
    #         new_filename = custom_title_case(filename)
    #         new_filename = new_filename[:-3] + ".md"
    #
    #         if filename == new_filename:
    #             # print(f"Skipping {filename} because it is already title case")
    #             continue
    #
    #         # Check if the renamed file already exists
    #         if os.path.exists(path + "/" + new_filename):
    #             # print(f"WARNING: {new_filename} already exists! Skipping...")
    #             continue
    #
    #         # os.rename(path + "/" + filename, path + "/" + new_filename)
    #         print(f"{filename} -> {new_filename}")
    for file_name in os.listdir(path):
        if file_name.endswith(".md"):
            with open(path + "/" + file_name, "r") as f:
                contents = f.read()
                contents_orig = contents
            # Find all links like [\1](\2.md) and uppercase the \2 portion using the custom_title_case function
            links = re.findall(r"\[(.*?)\]\((.*?)\.md\)", contents)
            for link in links:
                new_link = (link[0], custom_title_case(link[1]))
                contents = contents.replace(f"[{link[0]}]({link[1]}.md)", f"[{new_link[0]}]({new_link[1]}.md)")
            if contents_orig != contents:
                print(f"Writing {file_name}")
                with open(path + "/" + file_name, "w") as f:
                    f.write(contents)


if __name__ == "__main__":
    # test_titles = ["John the cow", "Will-o'-the-wisp", "wizards", "the wizards", "the wizards of oz", "the wizards of oz and the cow", "back of the house"]
    # for title in test_titles:
    #     print(f"{title} -> {custom_title_case(title)}")

    fix_link_cases()
