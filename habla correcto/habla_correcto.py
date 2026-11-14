"""
🦜 HABLA CORRECTO — versión para NIÑOS (interfaz gráfica, todo en un archivo)

Solo ejecuta:   python habla_correcto_ninos.py
La primera vez instala solo las librerías que falten (necesita internet).
"""
import importlib
import subprocess
import sys


def _instalar():
    for modulo, paquete in {"sounddevice": "sounddevice", "scipy": "scipy",
                            "speech_recognition": "SpeechRecognition"}.items():
        try:
            importlib.import_module(modulo)
        except ImportError:
            print(f"📦 Instalando {paquete}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
    try:
        importlib.import_module("googletrans")
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "googletrans==4.0.0rc1"])
        except Exception:
            print("⚠️ googletrans no se instaló: se usará el diccionario de respaldo.")


_instalar()

import asyncio, difflib, inspect, json, os, queue, random, re, tempfile, threading, time
import tkinter as tk

import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write

try:
    import winsound
except ImportError:
    winsound = None

FREC = 44100
AUDIO = os.path.join(tempfile.gettempdir(), "habla_ninos.wav")
RECORD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "record_habla_ninos.json")

# palabra en inglés: (español de respaldo, dibujo)
NIVELES = {
    "1": {"nombre": "🐣 Fácil", "color": "#5ed38a", "rondas": 6, "vidas": 5, "intentos": 3, "seg": 3, "mult": 1,
          "palabras": {"apple": ("manzana", "🍎"), "house": ("casa", "🏠"), "water": ("agua", "💧"),
                       "dog": ("perro", "🐶"), "cat": ("gato", "🐱"), "book": ("libro", "📖"),
                       "red": ("rojo", "🔴"), "milk": ("leche", "🥛"), "friend": ("amigo", "🤝"),
                       "sun": ("sol", "☀️")}},
    "2": {"nombre": "🐥 Medio", "color": "#ffb02e", "rondas": 8, "vidas": 4, "intentos": 2, "seg": 4, "mult": 2,
          "palabras": {"window": ("ventana", "🪟"), "butterfly": ("mariposa", "🦋"),
                       "breakfast": ("desayuno", "🥞"), "library": ("biblioteca", "📚"),
                       "neighbor": ("vecino", "🏘️"), "umbrella": ("paraguas", "☂️"),
                       "kitchen": ("cocina", "🍳"), "mountain": ("montaña", "⛰️"),
                       "chicken": ("pollo", "🐔"), "island": ("isla", "🏝️")}},
    "3": {"nombre": "🦅 Difícil", "color": "#ff7eb6", "rondas": 10, "vidas": 3, "intentos": 1, "seg": 4, "mult": 3,
          "palabras": {"thought": ("pensamiento", "💭"), "through": ("a través", "🚇"),
                       "comfortable": ("cómodo", "🛋️"), "vegetable": ("verdura", "🥕"),
                       "schedule": ("horario", "📅"), "enough": ("suficiente", "✋"),
                       "throughout": ("a lo largo de", "🌍"), "development": ("desarrollo", "🌱"),
                       "entrepreneur": ("emprendedor", "💼"), "Wednesday": ("miércoles", "📆")}},
}

BG, BLANCO, OSCURO = "#bfe9ff", "#ffffff", "#3b2f6b"
MORADO, VERDE, ROJO, AMARILLO, AZUL, ROSA, NARANJA = "#8e6bff", "#5ed38a", "#ff6b6b", "#ffd23f", "#4dabf7", "#ff7eb6", "#ff9f43"
FUENTE = "Comic Sans MS"


# ---------------------------- lógica ----------------------------
def traducir(en, respaldo):
    try:
        from googletrans import Translator
        r = Translator().translate(en, src="en", dest="es")
        if inspect.isawaitable(r):
            r = asyncio.run(r)
        return r.text
    except Exception:
        return respaldo


def grabar_y_reconocer(seg, aviso):
    try:
        audio = sd.rec(int(seg * FREC), samplerate=FREC, channels=1, dtype="int16")
        for resto in range(seg, 0, -1):
            aviso(f"🔴 ¡Habla ahora! {resto}")
            time.sleep(1)
        sd.wait()
        write(AUDIO, FREC, audio)
    except Exception as e:
        return None, f"No pude usar el micrófono: {e}"
    aviso("🧠 Estoy pensando...")
    rec = sr.Recognizer()
    try:
        with sr.AudioFile(AUDIO) as f:
            datos = rec.record(f)
        return rec.recognize_google(datos, language="en-US"), None
    except sr.UnknownValueError:
        return None, None
    except sr.RequestError:
        return None, "No hay internet para entender tu voz."
    except Exception as e:
        return None, f"Error de audio: {e}"


def limpiar(t):
    return re.sub(r"[^a-z\s]", "", t.lower()).strip()


def comparar(esperado, oido):
    e, o = limpiar(esperado), limpiar(oido)
    if e == o or e in o.split():
        return "ok", 1.0
    s = difflib.SequenceMatcher(None, e, o).ratio()
    return ("casi" if s >= 0.8 else "mal"), s


def cargar_record():
    try:
        with open(RECORD, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"puntos": 0, "jugador": "-"}


def guardar_record(nombre, puntos):
    try:
        with open(RECORD, "w", encoding="utf-8") as f:
            json.dump({"puntos": puntos, "jugador": nombre}, f, ensure_ascii=False)
    except Exception:
        pass


def sonido(bien):
    if not winsound:
        return
    notas = [(660, 120), (880, 120), (1100, 200)] if bien else [(300, 200), (220, 300)]
    def tocar():
        try:
            for f, d in notas:
                winsound.Beep(f, d)
        except Exception:
            pass
    threading.Thread(target=tocar, daemon=True).start()


# ---------------------------- widgets ----------------------------
class Boton(tk.Canvas):
    """Botón grande y redondeado, fácil de tocar."""
    def __init__(self, padre, texto, comando, color, ancho=260, alto=64, tam=18, fg="white"):
        super().__init__(padre, width=ancho, height=alto, bg=padre["bg"], highlightthickness=0, cursor="hand2")
        r, (w, h) = alto // 2, (ancho, alto)
        pts = [r+3, 3, w-r, 3, w-3, 3, w-3, r, w-3, h-r, w-3, h-3, w-r, h-3, r+3, h-3, 3, h-3, 3, h-r, 3, r, 3, 3]
        self.color, self.comando, self.activo = color, comando, True
        self.forma = self.create_polygon(pts, smooth=True, fill=color, outline=color, width=4)
        self.texto = self.create_text(w / 2, h / 2, text=texto, font=(FUENTE, tam, "bold"), fill=fg)
        self.bind("<Button-1>", lambda e: self.activo and self.comando and self.comando())

    def habilitar(self, si):
        self.activo = si
        self.itemconfig(self.forma, fill=self.color if si else "#cfd8e3", outline=self.color if si else "#cfd8e3")
        self.config(cursor="hand2" if si else "arrow")

    def marcar(self, si):
        self.itemconfig(self.forma, outline=OSCURO if si else self.color)


class App:
    def __init__(self, root):
        self.root = root
        root.title("🦜 Habla Correcto")
        root.geometry("840x760")
        root.minsize(760, 700)
        root.configure(bg=BG)
        self.cola = queue.Queue()
        self.cont = tk.Frame(root, bg=BG)
        self.cont.pack(fill="both", expand=True, padx=20, pady=10)
        self.nombre, self.clave = "", "1"
        self.estado = self.bubble = self.cara = None
        self.botones, self.ocupado = [], False
        self.poll()
        self.inicio()

    # --- ayudas ---
    def L(self, padre, texto, tam=14, color=OSCURO, **kw):
        return tk.Label(padre, text=texto, bg=padre["bg"], fg=color, font=(FUENTE, tam, "bold"), **kw)

    def limpiar_pantalla(self):
        for w in self.cont.winfo_children():
            w.destroy()
        self.estado = self.bubble = self.cara = None
        self.botones = []

    def habilitar(self, si):
        for b in self.botones:
            b.habilitar(si)
        self.ocupado = not si

    def di(self, texto, cara="🦜"):
        """Lora (la mascota) habla."""
        try:
            if self.bubble: self.bubble.config(text=texto)
            if self.cara: self.cara.config(text=cara)
        except tk.TclError:
            pass

    def mascota(self, padre, texto):
        fila = tk.Frame(padre, bg=padre["bg"])
        self.cara = self.L(fila, "🦜", 54)
        self.cara.pack(side="left", padx=8)
        marco = tk.Frame(fila, bg=BLANCO, padx=16, pady=10, highlightbackground=MORADO, highlightthickness=3)
        marco.pack(side="left", fill="x", expand=True)
        self.bubble = self.L(marco, texto, 15, wraplength=520, justify="left")
        self.bubble.pack()
        return fila

    # --- cola hilos → pantalla ---
    def poll(self):
        try:
            while True:
                tipo, datos = self.cola.get_nowait()
                getattr(self, "on_" + tipo)(datos)
        except queue.Empty:
            pass
        self.root.after(100, self.poll)

    def aviso(self, texto):
        self.cola.put(("aviso", texto))

    def on_aviso(self, texto):
        self.di(texto, "👂" if "Habla" in texto else "🤔")

    def on_pares(self, pares):
        self.pares = pares
        self.juego()

    def on_mic(self, datos):
        texto, error = datos
        if error:
            self.di("⚠️ " + error, "😟")
        elif texto:
            self.di(f"¡Te escuché! Dijiste “{texto}”. ¡Todo funciona! 🎉", "🤩")
        else:
            self.di("No te oí bien. ¡Habla más fuerte! 📢", "🥺")
        self.habilitar(True)

    def on_resultado(self, datos):
        self.procesar(*datos)

    # ---------------------------- INICIO ----------------------------
    def inicio(self):
        self.limpiar_pantalla()
        c = self.cont
        titulo = tk.Frame(c, bg=BG)
        titulo.pack(pady=(4, 0))
        colores = [ROJO, NARANJA, "#e6b800", VERDE, AZUL, MORADO, ROSA, ROJO]
        for i, ch in enumerate("HABLA"):
            self.L(titulo, ch, 44, colores[i]).pack(side="left")
        titulo2 = tk.Frame(c, bg=BG)
        titulo2.pack()
        for i, ch in enumerate("CORRECTO"):
            self.L(titulo2, ch, 36, colores[i]).pack(side="left")

        self.mascota(c, "¡Hola! Soy Lora, el loro. ¡Aprende inglés conmigo! Te diré una palabra en español y tú me la dices en inglés 🇬🇧").pack(fill="x", pady=12)

        self.L(c, "✏️ ¿Cómo te llamas?", 16).pack()
        self.entrada = tk.Entry(c, font=(FUENTE, 18, "bold"), justify="center", width=16,
                                relief="flat", highlightthickness=3, highlightbackground=MORADO)
        self.entrada.insert(0, self.nombre)
        self.entrada.pack(pady=6, ipady=6)

        self.L(c, "🎚️ ¿Qué nivel quieres?", 16).pack(pady=(10, 4))
        fila = tk.Frame(c, bg=BG)
        fila.pack()
        self.b_niveles = {}
        for k, n in NIVELES.items():
            b = Boton(fila, n["nombre"], lambda k=k: self.elegir(k), n["color"], 220, 62, 17)
            b.pack(side="left", padx=6)
            self.b_niveles[k] = b
        self.elegir(self.clave)

        fila2 = tk.Frame(c, bg=BG)
        fila2.pack(pady=18)
        b_mic = Boton(fila2, "🎙️ Probar mi micrófono", self.probar_mic, AZUL, 300, 58, 14)
        b_mic.pack(side="left", padx=8)
        b_play = Boton(fila2, "🚀 ¡A JUGAR!", self.empezar, VERDE, 300, 58, 17)
        b_play.pack(side="left", padx=8)
        self.botones = [b_mic, b_play]

        r = cargar_record()
        self.L(c, f"🏆 Récord: {r['puntos']} estrellas ({r['jugador']})", 14, "#b07d00").pack()

    def elegir(self, clave):
        self.clave = clave
        for k, b in self.b_niveles.items():
            b.marcar(k == clave)

    def probar_mic(self):
        if self.ocupado:
            return
        self.habilitar(False)
        self.di("¡Di “hello” cuando veas el aviso rojo! 🎙️", "👂")
        def tarea():
            self.cola.put(("mic", grabar_y_reconocer(2, self.aviso)))
        threading.Thread(target=tarea, daemon=True).start()

    def empezar(self):
        if self.ocupado:
            return
        self.nombre = self.entrada.get().strip() or "Amigo"
        self.nivel = NIVELES[self.clave]
        self.habilitar(False)
        self.di("¡Preparando las palabras mágicas! ✨", "🤗")
        def tarea():
            elegidas = random.sample(list(self.nivel["palabras"].items()),
                                     min(self.nivel["rondas"], len(self.nivel["palabras"])))
            pares = [(en, traducir(en, es), dib) for en, (es, dib) in elegidas]
            self.cola.put(("pares", pares))
        threading.Thread(target=tarea, daemon=True).start()

    # ---------------------------- JUEGO ----------------------------
    def juego(self):
        self.limpiar_pantalla()
        c = self.cont
        self.e = {"est": 0, "vidas": self.nivel["vidas"], "racha": 0, "mejor": 0}
        self.i, self.aciertos, self.jugadas = -1, 0, 0

        top = tk.Frame(c, bg=BLANCO, padx=14, pady=6, highlightbackground=MORADO, highlightthickness=3)
        top.pack(fill="x")
        self.l_ronda = self.L(top, "", 14)
        self.l_ronda.pack(side="left")
        self.l_est = self.L(top, "", 16, "#b07d00")
        self.l_est.pack(side="right")
        self.l_vidas = self.L(top, "", 16)
        self.l_vidas.pack(side="right", padx=18)

        self.barra = tk.Canvas(c, height=22, bg=BG, highlightthickness=0)
        self.barra.pack(fill="x", pady=6)

        tarjeta = tk.Frame(c, bg=BLANCO, highlightbackground=NARANJA, highlightthickness=5)
        tarjeta.pack(fill="x", pady=4)
        self.confeti = tk.Canvas(tarjeta, height=48, bg=BLANCO, highlightthickness=0)
        self.confeti.pack(fill="x")
        self.l_dibujo = self.L(tarjeta, "", 78, BLANCO)
        self.l_dibujo.pack()
        self.L(tarjeta, "¿Cómo se dice en inglés? 🇬🇧", 14, "#7b6fb0").pack()
        self.l_palabra = self.L(tarjeta, "", 40, MORADO)
        self.l_palabra.pack()
        self.l_pista = self.L(tarjeta, " ", 14, AZUL)
        self.l_pista.pack(pady=(0, 8))

        self.mascota(c, "").pack(fill="x", pady=8)

        self.b_hablar = Boton(c, "🎤  ¡HABLA!", self.hablar, VERDE, 340, 78, 24)
        self.b_hablar.pack(pady=4)
        fila = tk.Frame(c, bg=BG)
        fila.pack(pady=6)
        self.b_pista = Boton(fila, "💡 Pista", self.pista, AZUL, 190, 52, 14)
        self.b_pista.pack(side="left", padx=8)
        self.b_saltar = Boton(fila, "⏭️ Saltar", self.saltar, NARANJA, 190, 52, 14)
        self.b_saltar.pack(side="left", padx=8)
        self.botones = [self.b_hablar, self.b_pista, self.b_saltar]
        self.siguiente()

    def encabezado(self):
        n, e = len(self.pares), self.e
        self.l_ronda.config(text=f"📍 {min(self.i + 1, n)} de {n}")
        self.l_est.config(text=f"⭐ {e['est']}" + (f"   🔥 x{e['racha']}" if e["racha"] >= 2 else ""))
        self.l_vidas.config(text="❤️" * e["vidas"] + "🖤" * (self.nivel["vidas"] - e["vidas"]))
        self.barra.update_idletasks()
        w = max(self.barra.winfo_width(), 100)
        self.barra.delete("all")
        self.barra.create_rectangle(2, 3, w - 2, 19, fill=BLANCO, outline=MORADO, width=2)
        self.barra.create_rectangle(4, 5, 4 + (w - 8) * self.i / n, 17, fill=VERDE, outline=VERDE)

    def siguiente(self):
        self.i += 1
        if self.i >= len(self.pares):
            bonus = self.e["vidas"] * 10
            self.e["est"] += bonus
            return self.fin(True, bonus)
        self.jugadas += 1
        self.intento, self.pista_usada = 0, False
        en, es, dib = self.pares[self.i]
        self.l_dibujo.config(text=dib)
        self.l_palabra.config(text=es.upper())
        self.l_pista.config(text=" ")
        self.di("Pulsa el botón verde y dime la palabra en inglés 🎤", "🦜")
        self.encabezado()
        self.habilitar(True)

    def hablar(self):
        if self.ocupado:
            return
        self.habilitar(False)
        def tarea():
            self.cola.put(("resultado", grabar_y_reconocer(self.nivel["seg"], self.aviso)))
        threading.Thread(target=tarea, daemon=True).start()

    def procesar(self, texto, error):
        en = self.pares[self.i][0]
        if error:
            self.di("⚠️ " + error, "😟")
            self.habilitar(True)
            return
        self.intento += 1
        quedan = self.nivel["intentos"] - self.intento
        if texto is None:
            msg, cara = "No te entendí 🙉 ¡Habla más fuerte y claro!", "🥺"
        else:
            res, sim = comparar(en, texto)
            if res == "ok":
                return self.acierto(texto)
            if res == "casi":
                msg, cara = f"¡Casi, casi! 😮 Escuché “{texto}”. ¡Tú puedes!", "😮"
            else:
                msg, cara = f"Escuché “{texto}”. ¡Inténtalo otra vez! 💪", "🤔"
        if quedan > 0:
            self.di(f"{msg}\nTe quedan {quedan} intento(s) ❤️", cara)
            self.habilitar(True)
        else:
            self.di(f"{msg}\nLa respuesta era: {en.upper()} 💛", "🥺")
            self.fallo()

    def acierto(self, texto):
        e, n = self.e, self.nivel
        ganadas = 10 * n["mult"] + (n["intentos"] - self.intento) * 3 + e["racha"] * 2 + (0 if self.pista_usada else 5)
        e["est"] += ganadas
        e["racha"] += 1
        e["mejor"] = max(e["mejor"], e["racha"])
        self.aciertos += 1
        extra = f"\n🔥 ¡Racha de {e['racha']}!" if e["racha"] >= 3 else ""
        self.di(f"¡¡MUY BIEN!! Dijiste “{texto}” 🎉\n¡Ganaste {ganadas} estrellas! ⭐{extra}", "🤩")
        self.encabezado()
        sonido(True)
        self.lluvia()
        self.root.after(2200, self.siguiente)

    def fallo(self):
        self.e["vidas"] -= 1
        self.e["racha"] = 0
        self.encabezado()
        sonido(False)
        if self.e["vidas"] <= 0:
            self.root.after(2600, lambda: self.fin(False, 0))
        else:
            self.root.after(2600, self.siguiente)

    def pista(self):
        if self.ocupado or self.pista_usada:
            return
        en = self.pares[self.i][0]
        self.pista_usada = True
        self.e["est"] = max(0, self.e["est"] - 5)
        self.l_pista.config(text=f"💡 Empieza con la letra “{en[0].upper()}” y tiene {len(en)} letras")
        self.encabezado()

    def saltar(self):
        if self.ocupado:
            return
        self.habilitar(False)
        self.di(f"Saltamos esta. Era: {self.pares[self.i][0].upper()} 💛", "😌")
        self.fallo()

    def lluvia(self):
        """Confeti de estrellas."""
        cv = self.confeti
        w = max(cv.winfo_width(), 300)
        bolas = [[cv.create_text(random.randint(10, w - 10), -10, text=random.choice("⭐🎉✨🎈💖"),
                                 font=(FUENTE, random.randint(14, 24))), random.randint(3, 8)] for _ in range(26)]
        def paso(n=0):
            try:
                for b, v in bolas:
                    cv.move(b, random.randint(-2, 2), v)
                if n < 16:
                    self.root.after(45, lambda: paso(n + 1))
                else:
                    cv.delete("all")
            except tk.TclError:
                pass
        paso()

    # ---------------------------- FIN ----------------------------
    def fin(self, gano, bonus):
        self.limpiar_pantalla()
        c = self.cont
        pct = int(self.aciertos / self.jugadas * 100) if self.jugadas else 0
        medallas = 3 if pct >= 70 else 2 if pct >= 40 else 1
        self.L(c, "🏆" if gano else "🫶", 70).pack(pady=(10, 0))
        self.L(c, "¡LO LOGRASTE!" if gano else "¡Buen intento!", 34, VERDE if gano else NARANJA).pack()
        self.L(c, "⭐" * medallas + "☆" * (3 - medallas), 40, "#e6b800").pack()
        self.mascota(c, (f"¡Felicidades, {self.nombre}! Terminaste todas las palabras. 🎁 Bonus: +{bonus}" if gano else
                         f"¡Ay, {self.nombre}! Se acabaron las vidas, pero aprendiste mucho. ¡Practica otra vez!")).pack(fill="x", pady=10)
        self.cara.config(text="🤩" if gano else "🤗")

        card = tk.Frame(c, bg=BLANCO, padx=30, pady=14, highlightbackground=MORADO, highlightthickness=4)
        card.pack(pady=6)
        for t in (f"✅ Palabras bien:  {self.aciertos} de {self.jugadas}",
                  f"🔥 Mejor racha:  {self.e['mejor']}",
                  f"⭐ Estrellas:  {self.e['est']}",
                  f"🎖️ Título:  {['🌱 Semillita', '📚 Buen estudiante', '🎤 Súper hablador', '🏅 ¡Campeón del inglés!'][min(3, pct // 30)]}"):
            self.L(card, t, 16, anchor="w").pack(fill="x", pady=2)

        r = cargar_record()
        if self.e["est"] > r["puntos"]:
            self.L(c, "🎉 ¡NUEVO RÉCORD! ¡Eres el mejor! 🎉", 18, ROSA).pack(pady=6)
            guardar_record(self.nombre, self.e["est"])
        else:
            self.L(c, f"🏆 Récord: {r['puntos']} estrellas ({r['jugador']})", 14, "#b07d00").pack(pady=6)
        fila = tk.Frame(c, bg=BG)
        fila.pack(pady=10)
        Boton(fila, "🔁 Jugar otra vez", self.inicio, VERDE, 270, 62, 16).pack(side="left", padx=8)
        Boton(fila, "👋 Salir", self.root.destroy, ROJO, 200, 62, 16).pack(side="left", padx=8)
        sonido(gano)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
    try:
        os.remove(AUDIO)
    except OSError:
        pass


if __name__ == "__main__":
    main()