from zvukovod.tasteri import ime_tastera


class Rezim:
    naziv = ""

    def __init__(self, aplikacija):
        self.aplikacija = aplikacija

    def aktiviraj(self):
        pass

    def taster_pritisnut(self, dogadjaj):
        pass

    def taster_otpusten(self, dogadjaj):
        pass


class UcenjeTastera(Rezim):
    naziv = "Režim učenja tastera"

    # Zvuk se pušta tek na otpuštanje, da prečice poput Alt+F4 ne bi
    # puštale zvuk tastera koji je samo deo kombinacije.
    def taster_otpusten(self, dogadjaj):
        self.aplikacija.zvukovi.pusti(ime_tastera(dogadjaj.key))
