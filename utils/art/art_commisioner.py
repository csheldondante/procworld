import time
from pathlib import Path
from threading import Thread
from typing import List, Optional

from utils.art.process_response import process_art_response
from config.globals import LLM_MODEL
from utils.text_utils.formatting import sanitize_article_name
from utils.writing.next_article_selection import rank_articles
from utils.art.dalle import get_picture_and_download
from utils.llms.gpt import prompt_completion_chat
from utils.writing.article import Article
from utils.writing.wiki_manager import WikiManager

import concurrent.futures
import os
import datetime
import glob


def description_file_exists(wiki_name: str, article_title: str) -> bool:
    return os.path.isfile(f"multiverse/{wiki_name}/art_descriptions/{article_title}.txt")


def image_file_exists(wiki_name: str, article_title: str, section_name: Optional[str] = None) -> bool:
    if section_name is None:
        # return os.path.isfile(f"multiverse/{wiki_name}/images/{article_title}.png") or os.path.isfile(f"multiverse/{wiki_name}/images/{article_title}_S_top.png")
        return len(glob.glob(f"multiverse/{wiki_name}/images/{article_title}*.png")) > 0
    else:
        return os.path.isfile(f"multiverse/{wiki_name}/images/{article_title}_S_{section_name}.png")


def get_description(article: Article) -> str:
    with open("prompts/get_art_description.txt", 'r') as f:
        prompt = f.read()

    prompt = prompt.format(article_wikitext=article.content_wikitext)

    print(f"Getting description for {article.title}...")

    response = prompt_completion_chat(prompt, max_tokens=2048, model=LLM_MODEL)

    return response


def use_description(wiki_name: str, article_file_name: str, description: str) -> str:
    suggestions = process_art_response(description)
    if len(suggestions) == 0:
        raise Exception("No suggestions found")
    section = suggestions[0].section
    prompt = suggestions[0].prompt
    orientation = suggestions[0].orientation
    caption = suggestions[0].caption

    save_loc = f"multiverse/{wiki_name}/images/{article_file_name}_S_{section}.png"
    get_picture_and_download(save_loc, prompt, size=orientation)

    # Add the image to the article
    article_file_path = f"multiverse/{wiki_name}/wiki/docs/{article_file_name}.md"
    with open(article_file_path, 'r') as file:
        lines = file.readlines()
    for i, line in enumerate(lines):
        if section.lower() in line.lower():
            # Insert new_text right after the line containing search_text
            lines.insert(i + 1, f"\n![{section}](../../images/{sanitize_article_name(article_file_name)}_S_{sanitize_article_name(section)}.png)\n{caption}\n")
            break
    # Write the updated lines back to the file
    with open(article_file_path, 'w') as file:
        file.writelines(lines)
    print(f"Added image to {article_file_name} in section {section}!")

    return save_loc


def fetch_and_save_description(wiki: WikiManager, article: Article) -> Optional[str]:
    try:
        description = get_description(article)
        filename = f"multiverse/{wiki.wiki_name}/art_descriptions/{article.title}.txt"
        with open(filename, 'w') as file:
            file.write(description)
            file.write(f"\n\nRetrieved at: {datetime.datetime.now()}")
            file.write("\nUsed: False")
        return filename
    except Exception as e:
        with open("logs/art_errors.txt", 'a') as error_file:
            error_file.write(f"Error fetching description for {article.title}: {e}\n")
        return None


def process_description(wiki: WikiManager, filename: str) -> None:
    article_title = os.path.basename(filename).split('.txt')[0]
    with open(filename, 'r') as file:
        description = file.read()
    try:
        print(f"Generating art for {article_title}...")
        use_description(wiki.wiki_name, article_title, description)
        # Update the status in the file
        with open(filename, 'a') as file:
            file.write("\nUsed: True")
    except Exception as e:
        with open("logs/art_errors.txt", 'a') as error_file:
            error_file.write(f"Error processing description for {article_title}: {e}\n")


def fetch_descriptions(wiki: WikiManager, articles: List[Article], executor: concurrent.futures.Executor) -> List[str]:
    filenames = []
    for article in articles:
        if not description_file_exists(wiki.wiki_name, article.title):
            future = executor.submit(fetch_and_save_description, wiki, article)
            filename = future.result()
            if filename:
                filenames.append(filename)
    return filenames


def process_images(wiki: WikiManager, executor: concurrent.futures.Executor, polling_interval: int = 1) -> None:
    processed_articles = set()

    while True:
        description_files = [f for f in os.listdir(f"multiverse/{wiki.wiki_name}/art_descriptions") if f.endswith(".txt")]
        for filename in description_files:
            article_title = filename.split('.txt')[0]
            if article_title not in processed_articles and not image_file_exists(wiki.wiki_name, article_title):
                executor.submit(process_description, wiki, f"multiverse/{wiki.wiki_name}/art_descriptions/{filename}")
                processed_articles.add(article_title)

        time.sleep(polling_interval)  # Wait for a second before checking again


def create_art_for_articles(wiki: WikiManager, articles: List[Article], max_num_fetch_parallel: int = 1, max_num_process_parallel: int = 1) -> None:
    os.makedirs("descriptions", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    # Start processing images in a separate thread
    process_thread = Thread(target=process_images, args=(wiki, concurrent.futures.ThreadPoolExecutor(max_workers=max_num_process_parallel)))
    process_thread.start()

    # Fetch descriptions in the main thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_num_fetch_parallel) as fetch_executor:
        fetch_descriptions(wiki, articles, fetch_executor)

    process_thread.join()  # Wait for the processing thread to finish


if __name__ == "__main__":
    wiki_name = "world1"
    wiki_path = Path(f"multiverse/{wiki_name}/wiki/docs")

    # Load all articles
    wiki = WikiManager(wiki_name, wiki_path)

    articles = wiki.articles
    articles_by_score = rank_articles(wiki, remove_existing=False, only_include_existing=True)
    ranked_articles: List[Article] = [wiki.get_article_by_name(a[0]) for a in sorted(articles_by_score.items(), key=lambda x: x[1], reverse=True)]
    # print("\n".join([article.title for article in ranked_articles[:10]]))

    create_art_for_articles(wiki, ranked_articles, max_num_fetch_parallel=4, max_num_process_parallel=6)
