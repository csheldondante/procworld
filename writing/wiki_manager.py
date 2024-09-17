import os
import random
from pathlib import Path
from typing import List, Dict, Optional

from writing.article import Article


class WikiManager:
    def __init__(self, wiki_name: str, wiki_path: Path):
        self.wiki_name: str = wiki_name
        self.wiki_path: Path = wiki_path

        # Load all articles
        self.articles: List[Article] = []
        for article_file in os.listdir(self.wiki_path):
            if article_file.endswith(".md") and article_file != "index.md":
                with open(f"{self.wiki_path}/{article_file}", 'r') as f:
                    article_content = f.read()
                article = Article(article_file.replace(".md", ""), content_markdown=article_content)
                self.articles.append(article)
        

    def get_article_by_title(self, title: str) -> Article:
        for article in self.articles:
            if article.title == title:
                return article
        raise Exception(f"Article with title {title} not found.")

    def get_all_links(self) -> Dict[str, int]:
        links: Dict[str, int] = {}
        for article in self.articles:
            for link in article.get_all_links():
                if link in links:
                    links[link] += 1
                else:
                    links[link] = 1
        return links

    def get_snippets_that_mention(self, article_name: str) -> Dict[str, List[str]]:
        """
        Returns a dictionary of snippets that mention the given article name, with the key being the article name and the value being a list of paragraphs that mention the article name.
        """
        snippets: Dict[str, List[str]] = {}
        for article in self.articles:
            if article_name in article.get_all_links():
                snippets_for_article = article.get_snippets_that_mention(article_name)
                if snippets_for_article:
                    snippets[article.title] = snippets_for_article
        return snippets

    def get_existing_links(self, max_num_links: Optional[int] = None, alphabetize: bool = True) -> List[str]:
        article_names = [article.get_all_links() for article in self.articles]
        article_names = [item for sublist in article_names for item in sublist]

        # Remove duplicates
        article_names = list(set(article_names))

        if max_num_links is not None:
            random.shuffle(article_names)
            article_names = article_names[:max_num_links]
        if alphabetize:
            article_names.sort()
        return article_names

    def get_article_by_name(self, article_name: str) -> Article:
        for article in self.articles:
            if article.title == article_name:
                return article
        raise Exception(f"Article with name {article_name} not found.")
