"""Pretvaranje pygame kodova tastera u imena fajlova zvukova.

Ime tastera je ime pygame konstante bez prefiksa "K_", malim slovima
(K_a -> "a", K_LSHIFT -> "lshift", K_KP_ENTER -> "kp_enter").
Na taj način su sva imena bezbedna za fajl sistem, za razliku od
pygame.key.name() koji vraća npr. "/" ili "left shift".
"""
import pygame

# Pygame ima više konstanti za isti taster; ovde biramo jedno, kanonsko ime.
_ALIJASI = {
    pygame.K_PAUSE: "pause",
    pygame.K_EURO: "euro",
    pygame.K_LGUI: "lwin",
    pygame.K_RGUI: "rwin",
    pygame.K_NUMLOCK: "numlock",
    pygame.K_PRINTSCREEN: "printscreen",
    pygame.K_SCROLLLOCK: "scrolllock",
    **{getattr(pygame, f"K_KP{i}"): f"kp{i}" for i in range(10)},
}

# Slova srpske latinice nemaju pygame konstante; SDL ih prijavljuje
# preko njihovog Unicode koda kada je aktivan srpski raspored tastature.
SRPSKA_SLOVA = "čćžšđ"


def _napravi_mapu():
    mapa = {}
    for ime in dir(pygame):
        if ime.startswith("K_") and ime != "K_UNKNOWN":
            mapa.setdefault(getattr(pygame, ime), ime[2:].lower())
    mapa.update(_ALIJASI)
    mapa.update({ord(slovo): slovo for slovo in SRPSKA_SLOVA})
    return mapa


IMENA_TASTERA = _napravi_mapu()


def ime_tastera(kod):
    if kod in IMENA_TASTERA:
        return IMENA_TASTERA[kod]
    ime = pygame.key.name(kod).lower()
    return ime if ime.isalnum() else f"kod_{kod}"


def sva_imena():
    return sorted(set(IMENA_TASTERA.values()))
