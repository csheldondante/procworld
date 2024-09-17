from pathlib import Path

from config.globals import LLM_MODEL
from strategy.next_article_selection import select_next_article
from utils.gpt import prompt_completion_chat
from writing.article import Article
from writing.wiki_manager import WikiManager
import json
import os


def get_article_text(next_article_name: str, wiki: WikiManager) -> str:
    snippets = wiki.get_snippets_that_mention(next_article_name)
    snippets_text = ""
    for article_name, article_snippets in snippets.items():
        for snippet in article_snippets:
            snippets_text += f"The \"{article_name}\" article says: "
            snippets_text += f"{snippet}\n\n"

    # TODO: Somehow get the most relevant links here
    other_article_titles = wiki.get_existing_links(max_num_links=40, alphabetize=True)

    with open("prompts/write_new_article.txt", 'r') as f:
        prompt = f.read()

    prompt = prompt.format(topic=next_article_name, snippets=snippets_text.strip(), other_articles="\n".join([f"* [[{article_title}]]" for article_title in other_article_titles]))

    response = prompt_completion_chat(prompt, max_tokens=2048, model=LLM_MODEL)

    return response

def get_or_build_index(wiki: WikiManager):
    index_filename=f"{wiki.wiki_path}/article_index.index"
    if os.path.exists(index_filename) and os.path.getsize(index_filename) > 0:
        with open(index_filename, 'r') as i:
            categorized_articles=json.load(i)
            categorized_articles = {key: set(value) for key, value in categorized_articles.items()}
    else:
        categorized_articles = {}
        
    for article in wiki.articles:
        for key, value in categorized_articles.items():
            if article.title in value:
                break
        labels=categorize_article(article)
        for label in labels:
            if label not in categorized_articles:
                categorized_articles[label] = set()
            categorized_articles[label].add(article.title)
    
    with open(f"{wiki.wiki_path}/article_index.index", 'w+') as f:
            f.write(json.dumps(categorized_articles))

    return categorized_articles

def open_or_create_file(filename, mode='r+'):
    try:
        return open(filename, mode)
    except FileNotFoundError:
        return open(filename, 'w+')
    except IOError as e:
        print(f"Error opening or creating the file: {e}")
        return None

def categorize_article(article: Article):
    with open("prompts/article_categories.txt", 'r') as f:
        categories = f.read()
    with open("prompts/categorize_article.txt", 'r') as f:
        prompt = f.read()
    prompt = prompt.format(topic=article.title, categories=categories, article=article.content_markdown)
    response = prompt_completion_chat(prompt, max_tokens=2048, model=LLM_MODEL)
    labels = json.loads(response)
    return labels

def add_articles_to_wiki(wiki_name: str = "testing", num_new_articles: int = 1):
    wiki_path = Path(f"multiverse/{wiki_name}/wiki/docs")

    for i in range(num_new_articles):
        # Load all articles
        wiki = WikiManager(wiki_name, wiki_path)

        # Select next article
        next_article = select_next_article(wiki)
        print(f"Next article: {next_article}")

        # Get article text
        article_text = get_article_text(next_article, wiki)
        article = Article(next_article, content_wikitext=article_text)

        # Write article file
        with open(f"{wiki_path}/{next_article}.md", 'w') as f:
            f.write(article.content_markdown)
        print(f"Wrote article {next_article}!")

