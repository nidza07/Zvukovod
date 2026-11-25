# Zvukovod — plan i dokumentacija

Zvukovod je aplikacija koja slepim korisnicima pomaže u učenju tastature kroz
interaktivne mini igre i tutorijale. Pisana je u Pythonu uz Pygame, a sa čitačem
ekrana komunicira preko biblioteke Universal Speech.

## Pokretanje

```
pip install -r requirements.txt
python generisi_zvukove.py   # samo prvi put, ili kad se doda novi taster
python main.py
```

Izlaz iz aplikacije: **Alt+F4**.

## Struktura projekta

| Fajl / folder | Namena |
|---|---|
| `main.py` | Ulazna tačka. Klasa `Aplikacija`: prozor, glavna petlja, pozdravna poruka, prebacivanje režima. |
| `zvukovod/govor.py` | `izgovori(tekst)` — tanak omotač oko `UniversalSpeech.say`. |
| `zvukovod/zvukovi.py` | Klasa `Zvukovi` — učitava `zvukovi/<ime>.ogg` na zahtev i kešira ga. |
| `zvukovod/tasteri.py` | Pretvaranje pygame koda tastera u ime fajla zvuka. |
| `zvukovod/rezimi.py` | Osnovna klasa `Rezim` i prvi režim `UcenjeTastera`. |
| `generisi_zvukove.py` | Pomoćna skripta: generiše privremeni beep i kopira ga za svaki taster. |
| `zvukovi/` | Zvukovi tastera (`.ogg`). |
| `UniversalSpeech.py`, `*.dll` | Universal Speech i DLL-ovi za NVDA i ZDSR. |

## Implementirano

### Pozdravna poruka

Po pokretanju aplikacija izgovara: *„Dobro došli u Zvukovod! Režim učenja tastera je aktivan“*.

Kada se otvori novi prozor, čitač ekrana izgovara njegov naslov. Da taj izgovor ne
bi pregazio našu poruku, poruka se šalje 50 ms kasnije. Odlaganje nije urađeno
blokirajućim `sleep`-om, već jednokratnim pygame tajmerom
(`pygame.time.set_timer(DOGADJAJ_POZDRAV, 50, loops=1)`), pa glavna petlja i obrada
događaja rade normalno i tokom čekanja. Vrednost je u konstanti
`ODLAGANJE_POZDRAVA_MS` u `main.py`, ako bude potrebno podešavanje.

Naziv režima u poruci se uzima iz `rezim.naziv`, tako da će poruka biti tačna i ako
se početni režim jednom promeni.

### Režimi

Svaki režim nasleđuje `Rezim` (`zvukovod/rezimi.py`) i ima:

- `naziv` — tekst koji se izgovara pri prelasku na režim,
- `aktiviraj()` — poziva se kada režim postane aktivan,
- `taster_pritisnut(dogadjaj)` — dobija svaki `KEYDOWN` događaj koji nije globalna prečica,
- `taster_otpusten(dogadjaj)` — dobija `KEYUP` događaj, osim za tastere koji su bili deo
  globalne prečice (vidi ispod).

`Aplikacija` drži listu `self.rezimi` i indeks aktivnog režima. Novi režim se dodaje
tako što se napiše nova klasa i doda u tu listu.

### Prečice za promenu režima

- **Alt+Strelica desno** — naredni režim
- **Alt+Strelica levo** — prethodni režim

Prečice se proveravaju u `Aplikacija.obradi_pritisak` pre nego što se događaj prosledi
režimu, pa režim nikada ne vidi ove kombinacije. Radi i levi i desni Alt
(`KMOD_ALT`). Kretanje kroz režime je kružno. Dok postoji samo jedan režim,
izgovara se *„Drugi režimi trenutno nisu dostupni“*.

#### Praćenje tastera i „potrošeni“ tasteri

`Aplikacija` vodi dva skupa:

- `drzani` — tasteri za koje je stigao `KEYDOWN`, a još nije `KEYUP`.
- `potroseni` — tasteri koji su iskorišćeni za globalnu prečicu.

Kada se aktivira Alt+Strelica, u `potroseni` se dodaju ta strelica i svi Alt tasteri
koji su u tom trenutku držani. Pri otpuštanju (`obradi_otpustanje`) potrošen taster se
samo skida sa spiska i **ne prosleđuje se režimu**. Rezultat:

- Alt+Strelica ne pušta nikakav zvuk, ni za strelicu ni za Alt kad se otpusti,
  bez obzira na redosled otpuštanja i na to koliko puta je strelica pritisnuta dok je Alt držan.
- Alt pritisnut i otpušten sam pušta zvuk normalno; isto važi i za strelicu bez Alta.

`KEYUP` za taster koji nije u `drzani` se ignoriše. To se dešava kada je taster pritisnut
pre nego što je prozor dobio fokus (npr. pri povratku u aplikaciju sa Alt+Tab), pa takvo
otpuštanje ne pušta zvuk.

Na `QUIT` (Alt+F4) obrada preostalih događaja u tom krugu se odmah prekida, kako
eventualni `KEYUP` koji je stigao u istom paketu ne bi pustio zvuk pri zatvaranju.

### Režim učenja tastera

Svaki taster ne radi ništa osim što pušta zvuk `zvukovi/<ime_tastera>.ogg`.
Zvuk se pušta tek **kada se taster otpusti**, a ne pri pritisku. Tako prečice kao
Alt+F4 ne puštaju bespotrebne zvukove: aplikacija se zatvori pre nego što se ijedan
taster otpusti. Ovo je i osnova za budući režim učenja prečica (npr. Ctrl+F), gde će
se kombinacija prepoznavati dok su tasteri držani.
Ako zvuk za taster ne postoji, ništa se ne dešava (aplikacija ne puca).

Zvukovi se učitavaju pri prvom pritisku i čuvaju u kešu. Mikser ima 32 kanala, pa se
brzo uzastopni pritisci preklapaju umesto da se prekidaju.

### Imena tastera

Ime tastera je ime pygame konstante bez prefiksa `K_`, malim slovima:

| Taster | Konstanta | Fajl |
|---|---|---|
| A | `K_a` | `a.ogg` |
| 1 | `K_1` | `1.ogg` |
| Levi Shift | `K_LSHIFT` | `lshift.ogg` |
| Enter | `K_RETURN` | `return.ogg` |
| Razmak | `K_SPACE` | `space.ogg` |
| Strelica levo | `K_LEFT` | `left.ogg` |
| / | `K_SLASH` | `slash.ogg` |
| Enter na numeričkoj | `K_KP_ENTER` | `kp_enter.ogg` |
| 5 na numeričkoj | `K_KP5` | `kp5.ogg` |
| Levi Windows | `K_LGUI` | `lwin.ogg` |

Zašto ne `pygame.key.name()`: ona vraća imena poput `"/"`, `"\"`, `":"` ili
`"left shift"`, a neki od tih znakova nisu dozvoljeni u imenima fajlova na Windowsu.

Pygame ima više konstanti za isti taster (npr. `K_KP1` i `K_KP_1`, `K_LGUI`/`K_LMETA`/`K_LSUPER`).
Za njih je kanonsko ime određeno ručno u rečniku `_ALIJASI` u `zvukovod/tasteri.py`.

Slova srpske latinice (č, ć, ž, š, đ) nemaju pygame konstante. Kada je aktivan srpski
raspored tastature, SDL ih prijavljuje preko njihovog Unicode koda, pa su dodata u
mapu sa imenima `č.ogg`, `ć.ogg`, `ž.ogg`, `š.ogg`, `đ.ogg`. Za bilo koji drugi
nepoznat taster koristi se `pygame.key.name()` ako je ime alfanumeričko, a inače
`kod_<broj>`.

Kompletan spisak imena je spisak fajlova u folderu `zvukovi/`.

### Privremeni zvukovi

`generisi_zvukove.py` pomoću modula `tones` pravi kratak beep (sinus, 880 Hz, 120 ms,
sa kratkim attack/decay da ne bi pucketao), i kopira ga kao zvuk za svaki taster
(trenutno 138 fajlova).

- `tones` ume da napravi samo WAV, pa se konverzija u OGG radi pomoću **ffmpeg**
  (mora biti u PATH-u).
- Skripta **ne prepisuje** postojeće fajlove: kada se neki zvuk ručno zameni, ponovno
  pokretanje skripte ga neće pregaziti, već će samo dopuniti tastere koji nedostaju.

### Universal Speech

`UniversalSpeech.py` traži `UniversalSpeech.dll` u folderu skripte koja je pokrenuta
(`sys.argv[0]`), zato se aplikacija pokreće preko `main.py` iz korena projekta.
DLL sam bira aktivni čitač ekrana (NVDA, JAWS, ZDSR...), a ako nijedan nije pokrenut,
koristi SAPI. Svaka poruka prekida prethodni govor.

## Poznata ograničenja

- Neke kombinacije presreće Windows pre aplikacije (Alt+Tab, Windows taster,
  Ctrl+Alt+Del), pa za njih zvuk neće uvek biti pušten.
- Alt+F4 zatvara aplikaciju; ne postoji drugi način izlaza za sada.
- Pri odlasku iz prozora (npr. Alt+Tab) SDL može sam da pošalje `KEYUP` za držani Alt,
  pa se tada može čuti zvuk Alta. Nije testirano uživo.

## Sledeći koraci

- Zameniti privremene beep zvukove pravim snimcima imena tastera.
- Dodati nove režime (mini igre, tutorijale) u listu `Aplikacija.rezimi`.
- Režim učenja prečica: dok je modifikator (Ctrl, Alt, Shift) držan, pritisak na drugi
  taster pušta zvuk kombinacije (npr. `ctrl+f`) sa kratkim opisom šta prečica obično radi.
