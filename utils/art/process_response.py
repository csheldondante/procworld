from typing import List, Tuple


class ArtResponseData:
    def __init__(self):
        self.section = ""
        self.prompt = ""
        self.num_artsy = 0
        self.num_good = 0
        self.num_bad = 0
        self.orientation = "square"
        self.caption = ""


def process_art_response(response: str) -> List[ArtResponseData]:
    """
    Process a response from ChatGPT to the prompt at `get_art_description`
    """
    art_suggestions = []

    cur_response = None
    for line in response.split("\n"):
        if line.startswith("#"):
            if cur_response is not None:
                art_suggestions.append(cur_response)
            cur_response = ArtResponseData()
            cur_response.section = line.lstrip("#").strip()
        elif "art_prompt_detailed" in line:
            cur_response.prompt = line.split("art_prompt_detailed")[1].lstrip(":").strip("\"").strip()
        # TODO: This could be more robust
        elif "artistic_value" in line:
            cur_response.num_artsy = 0 if "none" in line else int(len(line.split(",")))
        elif "descriptive_value" in line:
            cur_response.num_good = 0 if "none" in line else int(len(line.split(",")))
        elif "difficulties" in line:
            cur_response.num_bad = 0 if "none" in line else int(len(line.split(",")))
        elif "caption:" in line:
            cur_response.caption = line.split("caption:")[1].strip("\"").strip()
            # print("Got caption", cur_response.caption)
        elif "orientation" in line:
            if "landscape" in line:
                cur_response.orientation = "1792x1024"
            elif "portrait" in line:
                cur_response.orientation = "1024x1792"
            else:
                cur_response.orientation = "1024x1024"

    # TODO: Sometimes suggest more than one
    best_suggestion = max(art_suggestions, key=lambda x: x.num_artsy + x.num_good - x.num_bad)

    return [best_suggestion]