from pathlib import Path
from writing.wiki_manager import WikiManager
from writing.write_articles import get_or_build_index
from utils.gpt import prompt_completion_chat
from writing.article import Article
from config.globals import LLM_MODEL

class NarrativeContext():
    potential_plots = []
    fan_theories = []
    mc = None
    characters = []
    story_board = []
    story_summary_so_far = ""
    def __init__(self):
        pass


class GameMaster():
    def __init__(self, wiki: WikiManager=None):
        self.wiki = wiki
        self.article_index = get_or_build_index(wiki)
        self.narrative_context = NarrativeContext()

    def create_character(self):
        user_input = input("Tell me about your idea for a character or ask for suggestions if you are unsure")
        user_input = input("What faction does your character belong to?")
        user_input = input("What is their role within the faction?")
        user_input = input("Tell me about their motivations, abilities and quirks")
        print("Creating character...")
        #get factions from the setting
        #get possible roles within the factions
        #choose some motivations, abilities and quirks
        #get potential story lines for the character and give their hooks
        character_name = "<Character Name>"
        while True:
            user_input = input(f"Do you want to continue with {character_name}?")
            if user_input.lower() == 'yes' or user_input.lower() == 'y' or user_input.lower() == 'continue' or user_input.lower() == 'true':
                print("Character created!")
                return None
        #return the character
        return None

    def character_selection(self):
        #propose a list of characters or an option to create characters
        characters = []
        user_input = input(f"{characters} \n Which character do you want to play? ")
        if user_input.lower() == 'create':
            return self.create_character()
        #try parse user input as number
        #return that character number
        return None

    def start_game(self):
        while True:
            user_input = input("What do you want to do? ")
            if user_input == None or user_input.lower() == 'continue' or user_input.lower() == 'next' or user_input.lower() == '':
                #TODO advance the story without the user input
                pass
            if user_input.lower() == 'quit' or user_input.lower() == 'exit' or user_input.lower() == 'stop' or user_input.lower() == 'end' or user_input.lower() == 'save' or user_input.lower() == 'save and quit' or user_input.lower() == 'x':
                print("Goodbye!")
                #TODO save
                break
            #TODO process the user input
            #if the input is plausible and established in the setting, incorpoerate it as is
            #if the input is plausible but not established, add it to the setting and incorporate it as long as it doesn't interfere with the narrative
            #if the input is implausible, provide feedback and ask for a different input or request a skill check and proceed


    def new_run(self):
        main_article=self.wiki.get_article_by_name("Aesheron")#TODO make some method to get the main article so this isn't horribly hardcoded
        print("Staring a new run in the world of Aesheron")
        print(main_article)
        self.mc=self.character_selection()
        self.start_game()
        pass

    def setup_new_run(main_article_name: str, wiki: WikiManager) -> str:
        snippets = wiki.get_snippets_that_mention(main_article_name)
        snippets_text = ""
        for article_name, article_snippets in snippets.items():
            for snippet in article_snippets:
                snippets_text += f"The \"{article_name}\" article says: "
                snippets_text += f"{snippet}\n\n"

        # TODO: Somehow get the most relevant links here
        other_article_titles = wiki.get_existing_links(max_num_links=40, alphabetize=True)

        with open("prompts/write_new_article.txt", 'r') as f:
            prompt = f.read()

        prompt = prompt.format(topic=main_article_name, snippets=snippets_text.strip(), other_articles="\n".join([f"* [[{article_title}]]" for article_title in other_article_titles]))

        response = prompt_completion_chat(prompt, max_tokens=2048, model=LLM_MODEL)

        return response




        
