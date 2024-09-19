from pathlib import Path
from writing.wiki_manager import WikiManager
from writing.write_articles import get_or_build_index
from utils.gpt import prompt_completion_chat
from writing.article import Article
from config.globals import LLM_MODEL

class NarrativeContext():
    scenes = []#already elapsed scenes
    potential_plots = []#potential ideas of where the story could go.  Possibly mention fan theories in prompt to get speculation.
    mc = None#main character
    characters = []#already introduced characters
    locations = []#already introduced locations
    story_board = []#a list of ideas for scenes to come based on the current favorite potential plot
    summary= ""#description of what's happened so far
    def __init__(self):
        pass

class Scene():
    characters=[]
    locations=[]
    events=[]
    summary=""
    important_details=[]#keys to bring up later to make things better connected
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
        user_input = input(f"{characters} \n Would you like to create a character or choose from characters created for you? \n1. create \n2. choose \n")
        if user_input.lower() == 'create' or user_input.lower() == '1':
            return self.create_character()
        else:
            user_input = input("Which character would you like to choose? ")
            #TODO parse user input as number
            #return that character
            return None
        #try parse user input as number
        #return that character number
        return None

    def start_game(self):
        while True:
            player_contribution = input("What do you want to do? ")
            if player_contribution == None or player_contribution.lower() == 'continue' or player_contribution.lower() == 'next' or player_contribution.lower() == '':
                #TODO advance the story without the user input
                pass
            if player_contribution.lower() == 'quit' or player_contribution.lower() == 'exit' or player_contribution.lower() == 'q' or player_contribution.lower() == 'x':
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




        
