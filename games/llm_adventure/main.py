from utils.llms.gpt import prompt_completion_chat

def main_loop():
    print("Welcome to the LLM Adventure Game!")
    print("Type 'quit' to exit the game.")
    
    context = "You are in a text-based adventure game. Describe the player's surroundings and ask what they want to do."
    
    while True:
        response = prompt_completion_chat(
            question=context,
            model="gpt-3.5-turbo",
            max_tokens=150
        )
        
        print("\n" + response + "\n")
        
        user_input = input("What do you want to do? ")
        
        if user_input.lower() == 'quit':
            print("Thanks for playing!")
            break
        
        context = f"{context}\nPlayer: {user_input}\nGame:"

def main_start():
    main_loop()

if __name__ == "__main__":
    main_start()
