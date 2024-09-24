from pathlib import Path
from typing import List

from utils.writing.article import Article


def update_articles_wikitext_to_markdown(wiki_path: Path, article_names: List[str]):
    for article_name in article_names:
        with open(f"{wiki_path}/{article_name}.md", 'r+') as f:
            article_content = f.read()
            article = Article(article_name, content_wikitext=article_content)
            f.seek(0)
            f.write(article.content_markdown)


if __name__ == "__main__":
    update_articles_wikitext_to_markdown(Path("../../multiverse/testing/wiki/docs"), ["Aesheron"])