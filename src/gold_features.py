from src.scoring import detect_language, english_score, contract_type, is_target

def compute_gold(title: str, contract: str, description: str) -> dict:
    lang = detect_language(description)
    score = english_score(description)
    ctype = contract_type(title, contract, description)
    target = is_target(ctype)
    return {
        "language": lang,
        "english_score": score,
        "contract_type": ctype,
        "is_target": target
    }
