import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from zvukovod.govor import izgovori
from zvukovod.rezimi import UcenjeTastera
from zvukovod.zvukovi import Zvukovi

NASLOV = "Zvukovod"
# Čitač ekrana prvo izgovara naslov novog prozora; bez ovog odlaganja
# taj izgovor bi prekinuo (ili bio izgovoren umesto) naše poruke.
ODLAGANJE_POZDRAVA_MS = 50
DOGADJAJ_POZDRAV = pygame.USEREVENT + 1
ALT_TASTERI = (pygame.K_LALT, pygame.K_RALT)


class Aplikacija:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.mixer.set_num_channels(32)
        pygame.display.set_caption(NASLOV)
        self.ekran = pygame.display.set_mode((640, 480))
        self.sat = pygame.time.Clock()
        self.zvukovi = Zvukovi()
        self.rezimi = [UcenjeTastera(self)]
        self.indeks_rezima = 0
        self.radi = True
        # Tasteri za koje smo primili KEYDOWN, a još nisu otpušteni.
        self.drzani = set()
        # Tasteri iskorišćeni za globalnu prečicu: njihovo otpuštanje se ne prosleđuje režimu.
        self.potroseni = set()

    @property
    def rezim(self):
        return self.rezimi[self.indeks_rezima]

    def promeni_rezim(self, pomeraj):
        if len(self.rezimi) < 2:
            izgovori("Drugi režimi trenutno nisu dostupni")
            return
        self.indeks_rezima = (self.indeks_rezima + pomeraj) % len(self.rezimi)
        izgovori(self.rezim.naziv)
        self.rezim.aktiviraj()

    def obradi_pritisak(self, dogadjaj):
        self.drzani.add(dogadjaj.key)
        if dogadjaj.mod & pygame.KMOD_ALT and dogadjaj.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.potroseni.add(dogadjaj.key)
            self.potroseni.update(self.drzani.intersection(ALT_TASTERI))
            self.promeni_rezim(1 if dogadjaj.key == pygame.K_RIGHT else -1)
        else:
            self.rezim.taster_pritisnut(dogadjaj)

    def obradi_otpustanje(self, dogadjaj):
        # KEYUP bez prethodnog KEYDOWN-a (npr. taster pritisnut pre nego što je
        # prozor dobio fokus) se ignoriše.
        if dogadjaj.key not in self.drzani:
            return
        self.drzani.discard(dogadjaj.key)
        if dogadjaj.key in self.potroseni:
            self.potroseni.discard(dogadjaj.key)
            return
        self.rezim.taster_otpusten(dogadjaj)

    def pokreni(self):
        pygame.time.set_timer(DOGADJAJ_POZDRAV, ODLAGANJE_POZDRAVA_MS, loops=1)
        while self.radi:
            for dogadjaj in pygame.event.get():
                if dogadjaj.type == pygame.QUIT:
                    self.radi = False
                    break
                elif dogadjaj.type == DOGADJAJ_POZDRAV:
                    izgovori(f"Dobro došli u Zvukovod! {self.rezim.naziv} je aktivan")
                    self.rezim.aktiviraj()
                elif dogadjaj.type == pygame.KEYDOWN:
                    self.obradi_pritisak(dogadjaj)
                elif dogadjaj.type == pygame.KEYUP:
                    self.obradi_otpustanje(dogadjaj)
            self.sat.tick(60)
        pygame.quit()


if __name__ == "__main__":
    Aplikacija().pokreni()
