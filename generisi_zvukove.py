"""Generiše privremeni beep (modul tones) i kopira ga kao zvuk za svaki taster.

Postojeći fajlovi se ne diraju, tako da ručno zamenjeni zvukovi ostaju sačuvani.
Pokretanje: python generisi_zvukove.py   (zahteva ffmpeg u PATH-u)
"""
import os
import shutil
import subprocess
import tempfile

from tones import SINE_WAVE
from tones.mixer import Mixer

from zvukovod.tasteri import sva_imena
from zvukovod.zvukovi import FOLDER_ZVUKOVA


def napravi_beep(putanja_ogg):
    mikser = Mixer(44100, 0.5)
    mikser.create_track(0, SINE_WAVE, attack=0.005, decay=0.02)
    mikser.add_tone(0, frequency=880, duration=0.12)
    with tempfile.TemporaryDirectory() as privremeni:
        wav = os.path.join(privremeni, "beep.wav")
        mikser.write_wav(wav)
        # tones pravi samo WAV, a aplikacija očekuje OGG, pa konverziju radi ffmpeg.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "4", putanja_ogg],
            check=True,
        )


def main():
    os.makedirs(FOLDER_ZVUKOVA, exist_ok=True)
    with tempfile.TemporaryDirectory() as privremeni:
        beep = os.path.join(privremeni, "beep.ogg")
        napravi_beep(beep)
        napravljeno = 0
        for ime in sva_imena():
            odrediste = os.path.join(FOLDER_ZVUKOVA, f"{ime}.ogg")
            if not os.path.exists(odrediste):
                shutil.copyfile(beep, odrediste)
                napravljeno += 1
    print(f"Napravljeno {napravljeno} novih zvukova u {FOLDER_ZVUKOVA}")


if __name__ == "__main__":
    main()
