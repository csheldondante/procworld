from pathlib import Path

from writing.wiki_manager import WikiManager
from writing.write_articles import add_articles_to_wiki

def load_wiki(wiki_name: str = "testing") -> WikiManager:
    wiki_path = Path(f"multiverse/{wiki_name}/wiki/docs")

    # Load all articles
    wiki = WikiManager(wiki_name, wiki_path)

    # Get all links
    links = wiki.get_all_links()

    # Sort links by count
    links = {k: v for k, v in sorted(links.items(), key=lambda item: item[1], reverse=False)}

    # Print all links
    for link, count in links.items():
        print(f"{link} ({count})")

    return wiki


if __name__ == "__main__":
    add_articles_to_wiki("world2", num_new_articles=1000)
