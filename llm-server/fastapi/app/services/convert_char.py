from unidecode import unidecode

def convert_to_english(name: str) -> str:    
    return unidecode(name)