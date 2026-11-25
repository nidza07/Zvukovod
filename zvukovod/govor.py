import UniversalSpeech


def izgovori(tekst, prekini=True):
    """Šalje tekst aktivnom čitaču ekrana (NVDA, JAWS, ZDSR...) ili SAPI-ju kao rezervi."""
    UniversalSpeech.say(tekst, prekini)
