import tkinter as tk
import math
import random
import time
import re


class ECGGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("ECG Text Generator")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        self.root.configure(bg="#030603")

        self.running = True
        self.last_time = time.perf_counter()

        self.phase = 0.0
        self.bpm = 72.0
        self.amplitude = 1.0
        self.noise = 0.0
        self.language = "EN"
        self.translations = {
            "EN": {
                "sequence": "ECG SEQUENCE:",
                "symbols_title": "SYMBOLS — press COPY to copy:",
                "copy": "COPY",
                "bpm": "BPM",
                "amplitude": "AMPLITUDE",
                "noise": "NOISE",
                "space": "SPACE = PAUSE",
                "footer": "P Q R S T = waves    W = delay    U = small wave    | = pause    _ = line    ~ = noise",
                "toggle": "RU / EN",
                "symbol_descriptions": {
                    "P": "P — wave",
                    "Q": "Q — Q",
                    "R": "R — R",
                    "S": "S — S",
                    "T": "T — T",
                    "U": "U — small wave",
                    "W": "W — delay",
                    "|": "| — pause",
                    "_": "_ — line",
                    "~": "~ — noise"
                }
            },
            "RU": {
                "sequence": "ПОСЛЕДОВАТЕЛЬНОСТЬ ЭКГ:",
                "symbols_title": "СИМВОЛЫ — нажми COPY, чтобы скопировать:",
                "copy": "КОПИРОВАТЬ",
                "bpm": "ЧСС",
                "amplitude": "АМПЛИТУДА",
                "noise": "ШУМ",
                "space": "ПРОБЕЛ = ПАУЗА",
                "footer": "P Q R S T = волны    W = задержка    U = малая волна    | = пауза    _ = линия    ~ = шум",
                "toggle": "EN / RU",
                "symbol_descriptions": {
                    "P": "P — волна",
                    "Q": "Q — Q",
                    "R": "R — R",
                    "S": "S — S",
                    "T": "T — T",
                    "U": "U — малая волна",
                    "W": "W — задержка",
                    "|": "| — пауза",
                    "_": "_ — линия",
                    "~": "~ — шум"
                }
            }
        }

        self.sequence = "P Q R S T"
        self.tokens = []
        self.pattern_duration = 1.0

        self.last_width = 0
        self.last_height = 0
        self.grid_dirty = True

        self.durations = {
            "P": 0.14,
            "Q": 0.035,
            "R": 0.045,
            "S": 0.055,
            "T": 0.20,
            "U": 0.10,
            "W": 0.12,
            "|": 0.30,
            "_": 0.15,
            "~": 0.15
        }

        self.build_interface()
        self.parse_sequence()

        self.root.bind("<space>", self.toggle)
        self.canvas.bind("<Configure>", self.on_resize)

        self.update()

    def build_interface(self):

        header = tk.Frame(
            self.root,
            bg="#061006",
            height=60
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="ECG TEXT GENERATOR",
            bg="#061006",
            fg="#00ff66",
            font=("Consolas", 18, "bold")
        ).pack(
            side="left",
            padx=20
        )

        controls_right = tk.Frame(
            header,
            bg="#061006"
        )
        controls_right.pack(
            side="right",
            padx=20
        )

        self.status = tk.Label(
            controls_right,
            text="● LIVE",
            bg="#061006",
            fg="#00ff66",
            font=("Consolas", 12, "bold")
        )
        self.status.pack(
            side="left",
            padx=(0, 10)
        )

        self.lang_button = tk.Button(
            controls_right,
            text="RU / EN",
            command=self.toggle_language,
            bg="#0b220b",
            fg="#00ff66",
            activebackground="#153815",
            activeforeground="#ffffff",
            relief="flat",
            font=("Consolas", 9, "bold"),
            padx=10,
            pady=3
        )
        self.lang_button.pack(
            side="left"
        )

        self.canvas = tk.Canvas(
            self.root,
            bg="#020702",
            highlightthickness=1,
            highlightbackground="#123312"
        )

        self.canvas.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(15, 8)
        )

        controls = tk.Frame(
            self.root,
            bg="#030603"
        )
        controls.pack(
            fill="x",
            padx=15,
            pady=5
        )

        sequence_frame = tk.Frame(
            controls,
            bg="#030603"
        )
        sequence_frame.pack(
            fill="x",
            pady=(0, 8)
        )

        self.sequence_label = tk.Label(
            sequence_frame,
            text="ECG SEQUENCE:",
            bg="#030603",
            fg="#00ff66",
            font=("Consolas", 10, "bold")
        )
        self.sequence_label.pack(
            side="left",
            padx=(0, 8)
        )

        self.entry = tk.Entry(
            sequence_frame,
            bg="#071007",
            fg="#00ff66",
            insertbackground="#00ff66",
            relief="flat",
            font=("Consolas", 12)
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6
        )

        self.entry.insert(
            0,
            self.sequence
        )

        self.entry.bind(
            "<KeyRelease>",
            self.live_sequence_update
        )

        sliders = tk.Frame(
            controls,
            bg="#030603"
        )
        sliders.pack(
            fill="x"
        )

        # BPM
        bpm_frame = tk.Frame(
            sliders,
            bg="#030603"
        )
        bpm_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.bpm_label = tk.Label(
            bpm_frame,
            text="BPM: 72",
            bg="#030603",
            fg="#00ff66",
            font=("Consolas", 10)
        )

        self.bpm_label.pack(
            anchor="w"
        )

        self.bpm_scale = tk.Scale(
            bpm_frame,
            from_=30,
            to=220,
            orient="horizontal",
            bg="#030603",
            fg="#00ff66",
            troughcolor="#102010",
            highlightthickness=0,
            showvalue=False,
            command=self.change_bpm
        )

        self.bpm_scale.set(72)

        self.bpm_scale.pack(
            fill="x"
        )

        # AMPLITUDE
        amp_frame = tk.Frame(
            sliders,
            bg="#030603"
        )
        amp_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10
        )

        self.amp_label = tk.Label(
            amp_frame,
            text="AMPLITUDE: 1.00",
            bg="#030603",
            fg="#00ff66",
            font=("Consolas", 10)
        )

        self.amp_label.pack(
            anchor="w"
        )

        self.amp_scale = tk.Scale(
            amp_frame,
            from_=0.2,
            to=2.0,
            resolution=0.05,
            orient="horizontal",
            bg="#030603",
            fg="#00ff66",
            troughcolor="#102010",
            highlightthickness=0,
            showvalue=False,
            command=self.change_amplitude
        )

        self.amp_scale.set(1.0)

        self.amp_scale.pack(
            fill="x"
        )

        # NOISE
        noise_frame = tk.Frame(
            sliders,
            bg="#030603"
        )
        noise_frame.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 0)
        )

        self.noise_label = tk.Label(
            noise_frame,
            text="NOISE: 0%",
            bg="#030603",
            fg="#00ff66",
            font=("Consolas", 10)
        )

        self.noise_label.pack(
            anchor="w"
        )

        self.noise_scale = tk.Scale(
            noise_frame,
            from_=0,
            to=100,
            orient="horizontal",
            bg="#030603",
            fg="#00ff66",
            troughcolor="#102010",
            highlightthickness=0,
            showvalue=False,
            command=self.change_noise
        )

        self.noise_scale.set(0)

        self.noise_scale.pack(
            fill="x"
        )

        symbols_outer = tk.Frame(
            self.root,
            bg="#030603"
        )

        symbols_outer.pack(
            fill="x",
            padx=15,
            pady=(8, 4)
        )

        self.symbols_label = tk.Label(
            symbols_outer,
            text="SYMBOLS — press COPY to copy:",
            bg="#030603",
            fg="#00ff66",
            font=("Consolas", 9, "bold")
        )
        self.symbols_label.pack(
            anchor="w"
        )

        symbols_frame = tk.Frame(
            symbols_outer,
            bg="#030603"
        )

        symbols_frame.pack(
            fill="x",
            pady=(4, 0)
        )

        self.symbol_description_labels = {}
        self.copy_buttons = {}

        symbols = [
            ("P", "P — wave"),
            ("Q", "Q — Q"),
            ("R", "R — R"),
            ("S", "S — S"),
            ("T", "T — T"),
            ("U", "U — small wave"),
            ("W", "W — delay"),
            ("|", "| — pause"),
            ("_", "_ — line"),
            ("~", "~ — noise")
        ]

        for symbol, description in symbols:

            item = tk.Frame(
                symbols_frame,
                bg="#061006",
                highlightthickness=1,
                highlightbackground="#123312"
            )

            item.pack(
                side="left",
                padx=(0, 5)
            )

            tk.Label(
                item,
                text=symbol,
                bg="#061006",
                fg="#00ff66",
                font=("Consolas", 12, "bold"),
                width=2
            ).pack(
                side="left",
                padx=(4, 0)
            )

            desc_label = tk.Label(
                item,
                text=description,
                bg="#061006",
                fg="#88aa88",
                font=("Consolas", 8)
            )
            desc_label.pack(
                side="left",
                padx=3
            )
            self.symbol_description_labels[symbol] = desc_label

            button = tk.Button(
                item,
                text="COPY",
                command=lambda s=symbol: self.copy_symbol(s),
                bg="#0b220b",
                fg="#00ff66",
                activebackground="#153815",
                activeforeground="#ffffff",
                relief="flat",
                font=("Consolas", 8, "bold"),
                padx=4,
                pady=1
            )
            button.pack(
                side="left",
                padx=(0, 3),
                pady=2
            )
            self.copy_buttons[symbol] = button

        footer = tk.Frame(
            self.root,
            bg="#030603"
        )

        footer.pack(
            fill="x",
            padx=15,
            pady=(3, 8)
        )

        self.footer_label = tk.Label(
            footer,
            text="P Q R S T = waves    W = delay    U = small wave    | = pause    _ = line    ~ = noise",
            bg="#030603",
            fg="#446644",
            font=("Consolas", 8)
        )
        self.footer_label.pack(
            side="left"
        )

        self.footer_space_label = tk.Label(
            footer,
            text="SPACE = PAUSE",
            bg="#030603",
            fg="#446644",
            font=("Consolas", 8)
        )
        self.footer_space_label.pack(
            side="right"
        )

        self.apply_language()

    def copy_symbol(self, symbol):

        self.root.clipboard_clear()
        self.root.clipboard_append(symbol)
        self.root.update()

    def live_sequence_update(self, event=None):

        self.parse_sequence()

    def change_bpm(self, value):

        self.bpm = float(value)
        self.bpm_label.config(
            text=f"{self.translations[self.language]['bpm']}: {int(self.bpm)}"
        )

    def change_amplitude(self, value):

        self.amplitude = float(value)
        self.amp_label.config(
            text=f"{self.translations[self.language]['amplitude']}: {self.amplitude:.2f}"
        )

    def change_noise(self, value):

        self.noise = float(value) / 100.0
        self.noise_label.config(
            text=f"{self.translations[self.language]['noise']}: {int(float(value))}%"
        )

    def apply_language(self):

        texts = self.translations[self.language]

        self.sequence_label.config(text=texts["sequence"])
        self.symbols_label.config(text=texts["symbols_title"])
        self.footer_label.config(text=texts["footer"])
        self.footer_space_label.config(text=texts["space"])
        self.lang_button.config(text=texts["toggle"])

        for symbol, label in self.symbol_description_labels.items():
            label.config(text=texts["symbol_descriptions"][symbol])

        for symbol, button in self.copy_buttons.items():
            button.config(text=texts["copy"])

        self.bpm_label.config(
            text=f"{texts['bpm']}: {int(self.bpm)}"
        )
        self.amp_label.config(
            text=f"{texts['amplitude']}: {self.amplitude:.2f}"
        )
        self.noise_label.config(
            text=f"{texts['noise']}: {int(self.noise * 100)}%"
        )

    def toggle_language(self, event=None):

        self.language = "RU" if self.language == "EN" else "EN"
        self.apply_language()

    def toggle(self, event=None):

        self.running = not self.running

        self.last_time = time.perf_counter()

        if self.running:

            self.status.config(
                text="● LIVE",
                fg="#00ff66"
            )

        else:

            self.status.config(
                text="■ PAUSED",
                fg="#888888"
            )

    def parse_sequence(self):

        text = self.entry.get().upper().strip()

        if not text:
            text = "_"

        text = text.replace(
            "QRS",
            " Q R S "
        )

        raw = re.findall(
            r"[PQRSTUW|_~]",
            text
        )

        if not raw:
            raw = ["_"]

        self.tokens = raw

        self.pattern_duration = sum(
            self.durations.get(
                token,
                0.1
            )
            for token in self.tokens
        )

        if self.pattern_duration <= 0:
            self.pattern_duration = 1.0

        self.sequence = text

    def gaussian(self, x, center, width):

        return math.exp(
            -0.5 *
            ((x - center) / width) ** 2
        )

    def realistic_p(self, x):

        return (
            self.gaussian(
                x,
                0.40,
                0.18
            ) * 0.18
            -
            self.gaussian(
                x,
                0.64,
                0.12
            ) * 0.025
        )

    def realistic_q(self, x):

        return (
            self.gaussian(
                x,
                0.46,
                0.14
            ) * -0.22
        )

    def realistic_r(self, x):

        return (
            self.gaussian(
                x,
                0.39,
                0.075
            ) * 1.05
            -
            self.gaussian(
                x,
                0.60,
                0.11
            ) * 0.18
        )

    def realistic_s(self, x):

        return (
            self.gaussian(
                x,
                0.48,
                0.12
            ) * -0.42
        )

    def realistic_t(self, x):

        return (
            self.gaussian(
                x,
                0.38,
                0.22
            ) * 0.34
            +
            self.gaussian(
                x,
                0.66,
                0.29
            ) * 0.20
        )

    def realistic_u(self, x):

        return (
            self.gaussian(
                x,
                0.48,
                0.20
            ) * 0.10
        )

    def wave_value(self, token, x):

        if token == "P":
            return self.realistic_p(x)

        if token == "Q":
            return self.realistic_q(x)

        if token == "R":
            return self.realistic_r(x)

        if token == "S":
            return self.realistic_s(x)

        if token == "T":
            return self.realistic_t(x)

        if token == "U":
            return self.realistic_u(x)

        if token == "~":

            return (
                math.sin(
                    x * math.pi * 22
                ) * 0.035
                +
                math.sin(
                    x * math.pi * 47
                ) * 0.018
            )

        if token == "W":

            return (
                math.sin(
                    x * math.pi
                ) * 0.008
            )

        return 0.0

    def value_at(self, phase):

        if not self.tokens:
            return 0.0

        phase %= self.pattern_duration

        elapsed = 0.0

        for token in self.tokens:

            duration = self.durations.get(
                token,
                0.1
            )

            if phase < elapsed + duration:

                local = (
                    phase - elapsed
                ) / duration

                return self.wave_value(
                    token,
                    local
                )

            elapsed += duration

        return 0.0

    def on_resize(self, event=None):

        self.grid_dirty = True

    def draw_grid(self, width, height):

        self.canvas.delete("grid")

        minor_x = 25
        minor_y = 20

        major_x = 125
        major_y = 100

        for x in range(
            0,
            width,
            minor_x
        ):

            self.canvas.create_line(
                x,
                0,
                x,
                height,
                fill="#082008",
                tags="grid"
            )

        for y in range(
            0,
            height,
            minor_y
        ):

            self.canvas.create_line(
                0,
                y,
                width,
                y,
                fill="#082008",
                tags="grid"
            )

        for x in range(
            0,
            width,
            major_x
        ):

            self.canvas.create_line(
                x,
                0,
                x,
                height,
                fill="#103510",
                tags="grid"
            )

        for y in range(
            0,
            height,
            major_y
        ):

            self.canvas.create_line(
                0,
                y,
                width,
                y,
                fill="#103510",
                tags="grid"
            )

        self.canvas.tag_lower("grid")

    def update(self):

        now = time.perf_counter()

        dt = now - self.last_time
        self.last_time = now

        if dt > 0.1:
            dt = 0.1

        # Всегда вычисляем BPM-период.
        # Это нужно даже во время PAUSE.
        beat_period = 60.0 / self.bpm

        # Двигаем сигнал только в LIVE.
        if self.running:

            self.phase += (
                dt /
                beat_period
            ) * self.pattern_duration

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width > 10 and height > 10:

            if (
                self.grid_dirty
                or
                width != self.last_width
                or
                height != self.last_height
            ):

                self.draw_grid(
                    width,
                    height
                )

                self.last_width = width
                self.last_height = height
                self.grid_dirty = False

            visible_time = 7.0

            count = min(
                900,
                max(
                    500,
                    int(width * 0.75)
                )
            )

            points = []

            baseline = (
                height * 0.50
            )

            for i in range(count):

                age = (
                    1.0 -
                    i / (count - 1)
                ) * visible_time

                phase = (
                    self.phase
                    -
                    age *
                    self.pattern_duration
                    /
                    beat_period
                )

                value = self.value_at(
                    phase
                )

                if self.noise > 0:

                    value += (
                        random.uniform(
                            -1.0,
                            1.0
                        )
                        *
                        0.035
                        *
                        self.noise
                    )

                baseline_phase = (
                    phase *
                    math.pi *
                    2
                )

                value += (
                    math.sin(
                        baseline_phase
                        +
                        age * 0.35
                    )
                    *
                    0.004
                )

                # i = 0 -> ЛЕВО
                # i = count-1 -> ПРАВО
                x = (
                    i *
                    width /
                    (count - 1)
                )

                y = (
                    baseline
                    -
                    value
                    *
                    self.amplitude
                    *
                    height
                    *
                    0.28
                )

                points.append(
                    (x, y)
                )

            flat_points = []

            for x, y in points:

                flat_points.extend(
                    [x, y]
                )

            self.canvas.delete("ecg")

            self.canvas.create_line(
                *flat_points,
                fill="#00ff66",
                width=2,
                tags="ecg"
            )

            self.canvas.tag_raise(
                "ecg"
            )

        self.root.after(
            33,
            self.update
        )


if __name__ == "__main__":

    root = tk.Tk()

    app = ECGGenerator(root)

    root.mainloop()