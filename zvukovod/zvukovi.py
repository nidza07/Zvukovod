import os

import pygame

FOLDER_ZVUKOVA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "zvukovi")


class Zvukovi:
    """Učitava .ogg fajlove na zahtev i čuva ih u kešu."""

    def __init__(self):
        self._kes = {}

    def pusti(self, ime):
        if ime not in self._kes:
            putanja = os.path.join(FOLDER_ZVUKOVA, f"{ime}.ogg")
            # None se kešira da se ne bi pri svakom pritisku ponovo proveravao disk.
            self._kes[ime] = pygame.mixer.Sound(putanja) if os.path.isfile(putanja) else None
        zvuk = self._kes[ime]
        if zvuk is not None:
            zvuk.play()
