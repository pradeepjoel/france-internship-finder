from langdetect import detect, LangDetectException
import re

# Internship / alternance signals (EN+FR)
INTERNSHIP_PATTERNS = [
    r"\bintern(ship)?\b",
    r"\bstage\b",
    r"\bstagiaire\b",
]
ALTERNANCE_PATTERNS = [
    r"\balternance\b",
    r"\bapprentissage\b",
    r"\bcontrat d['’]apprentissage\b",
    r"\bcontrat pro\b",
    r"\bprofessionnalisation\b",
]

# Non-target strong signals
NOT_TARGET_PATTERNS = [
    r"\bcdi\b",
    r"\bcdd\b",
    r"\bfull[\s-]?time\b",
    r"\bpermanent\b",
]

# English-friendly signals
POSITIVE_EN = [
    "working language: english", "english speaking", "english required",
    "fluent english", "native english", "professional english",
    "international environment", "global team", "multicultural",
    "communication in english", "meetings in english"
]

POSITIVE_FR = [
    "anglais requis", "anglais indispensable", "anglais obligatoire",
    "maîtrise de l'anglais", "maitrise de l'anglais", "bon niveau d'anglais",
    "niveau b2", "niveau c1", "toeic", "ielts", "toefl",
    "environnement international", "contexte international",
    "équipe internationale", "equipe internationale",
    "clients internationaux", "collaboration internationale",
    "communication en anglais", "réunions en anglais", "reunions en anglais",
    "documents en anglais", "reporting en anglais"
]

NEGATIVE_FR = [
    "français indispensable", "francais indispensable",
    "français obligatoire", "francais obligatoire",
    "maîtrise du français", "maitrise du francais",
    "bilingue français", "bilingue francais",
    "français courant", "francais courant",
    "équipe francophone", "equipe francophone",
    "uniquement en français", "uniquement en francais"
]

def detect_language(text: str) -> str:
    if not text or len(text) < 60:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def english_score(text: str) -> int:
    if not text:
        return 0
    t = text.lower()
    score = 0

    lang = detect_language(text)
    if lang == "en":
        score += 55
    elif lang == "fr":
        score += 10
    else:
        score += 5

    for k in POSITIVE_EN:
        if k in t:
            score += 12
    for k in POSITIVE_FR:
        if k in t:
            score += 12
    for k in NEGATIVE_FR:
        if k in t:
            score -= 22

    tech_boost = ["sql", "python", "spark", "databricks", "aws", "gcp", "azure", "docker", "kubernetes", "power bi"]
    for k in tech_boost:
        if k in t:
            score += 2

    return max(0, min(100, score))

def _match_any(patterns, text: str) -> bool:
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            return True
    return False

def contract_type(title: str, contract: str, desc: str) -> str:
    # Use title+desc as primary (more reliable than "contract" field)
    blob = " ".join([title or "", desc or "", contract or ""]).strip()
    if not blob:
        return "OTHER"

    # If explicitly CDI/CDD/full-time only, not a target
    if _match_any(NOT_TARGET_PATTERNS, blob):
        # BUT: allow if it also clearly says stage/alternance (some postings mention CDI after internship)
        if not (_match_any(INTERNSHIP_PATTERNS, blob) or _match_any(ALTERNANCE_PATTERNS, blob)):
            return "OTHER"

    if _match_any(ALTERNANCE_PATTERNS, blob):
        return "ALTERNANCE"
    if _match_any(INTERNSHIP_PATTERNS, blob):
        return "INTERNSHIP"

    return "OTHER"

def is_target(ct: str) -> int:
    return 1 if ct in ("INTERNSHIP", "ALTERNANCE") else 0
