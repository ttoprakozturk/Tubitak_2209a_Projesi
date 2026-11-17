# -*- coding: utf-8 -*-
"""
ALAN – ÇEVRE OYUNU  (Python + Pygame, internet gerektirmez)
TÜBİTAK 2209-A projesi | 5. sınıf Matematik | MAT.5.4.3

Üç görev türü (proje önerisindeki gibi):
  1) Aynı alan – farklı çevre      : Alanı verilen farklı dikdörtgenleri çiz, çevrelerini bul.
  2) Aynı çevre – farklı alan      : Çevresi verilen farklı dikdörtgenleri çiz, alanlarını bul.
  3) İddia sınama                  : Verilen bir iddiayı KARŞI ÖRNEK çizerek sına.

Öğrencinin yaptığı her deneme "oyun_kayitlari.csv" dosyasına otomatik kaydedilir
(Excel'de açmak için ayraç olarak ';' kullanılır).

KURULUM VE ÇALIŞTIRMA:
    pip install pygame
    python alan_cevre_oyunu.py

NASIL OYNANIR:
    Izgaraya tıkla ya da basılı tutup sürükle -> sol üst köşeden başlayan bir
    dikdörtgen oluşur. Her kare 1 birimkaredir, her kare kenarı 1 birimdir.
"""
import csv
import math
import os
import sys
import time
from datetime import datetime

import pygame

# ════════════════════════ AYARLAR (istediğini değiştirebilirsin) ════════════════════════
AREA_ROUNDS = [12, 20, 24]        # Görev 1'deki sabit alanlar (en fazla 36 birimkare olmalı)
PERIMETER_ROUNDS = [12, 16, 20]   # Görev 2'deki sabit çevreler (çift sayı olmalı)
LOGGING = True                    # False yaparsan hiçbir kayıt tutulmaz
LOG_FILE = "oyun_kayitlari.csv"
WIDTH, HEIGHT = 1000, 640
FPS = 30

# ════════════════════════ RENKLER ════════════════════════
BG = (251, 247, 236)
INK = (40, 44, 60)
WHITE = (255, 255, 255)
DARK = (30, 50, 90)
BLUE = (120, 178, 240)
BLUE_D = (40, 90, 160)
ORANGE = (245, 170, 90)
ORANGE_D = (200, 110, 20)
GREEN = (40, 150, 80)
RED = (200, 50, 50)
GREY = (200, 200, 208)
GRID = (150, 160, 180)
HOVER = (222, 236, 252)
BTN = (60, 120, 200)
BTN_OFF = (170, 175, 185)

TASK_NAMES = {
    "alan": "Görev 1: Aynı alan – farklı çevre",
    "cevre": "Görev 2: Aynı çevre – farklı alan",
    "iddia": "Görev 3: İddia sınama",
}

# ════════════════════════ MATEMATİK YARDIMCILARI ════════════════════════
def area(w, h):
    return w * h


def perimeter(w, h):
    return 2 * (w + h)


def norm(r):
    """4×5 ile 5×4 aynı dikdörtgendir; hep (küçük, büyük) biçiminde tutulur."""
    return (min(r), max(r))


def rects_with_area(a):
    """Alanı a olan tüm farklı dikdörtgenler (doğal sayı kenarlı)."""
    return [(k, a // k) for k in range(1, math.isqrt(a) + 1) if a % k == 0]


def rects_with_perimeter(p):
    """Çevresi p olan tüm farklı dikdörtgenler (doğal sayı kenarlı)."""
    s = p // 2
    return [(k, s - k) for k in range(1, s // 2 + 1)]


def check_config():
    for a in AREA_ROUNDS:
        if a > 36 or len(rects_with_area(a)) < 2:
            raise ValueError("AREA_ROUNDS: %d geçersiz (en fazla 36 olmalı ve en az 2 dikdörtgen çıkmalı)" % a)
    for p in PERIMETER_ROUNDS:
        if p % 2 or len(rects_with_perimeter(p)) < 2:
            raise ValueError("PERIMETER_ROUNDS: %d geçersiz (çift sayı olmalı ve en az 2 dikdörtgen çıkmalı)" % p)


# ════════════════════════ İDDİALAR (Görev 3) ════════════════════════
CLAIMS = [
    {
        "id": "I1",
        "text": "İddia: Alanı aynı olan dikdörtgenlerin çevreleri de her zaman aynıdır.",
        "hint": "Önce bir dikdörtgen çiz ve kaç birimkare olduğunu bul. Sonra aynı sayıda "
                "birimkaresi olan ama farklı görünen başka bir dikdörtgen çiz.",
    },
    {
        "id": "I2",
        "text": "İddia: Çevreleri aynı olan dikdörtgenlerin alanları da her zaman aynıdır.",
        "hint": "Önce bir dikdörtgen çiz ve çevresini bul. Sonra çevresi aynı olan ama "
                "kenarları farklı başka bir dikdörtgen çiz.",
    },
    {
        "id": "I3",
        "text": "İddia: Alanı daha büyük olan dikdörtgenin çevresi de her zaman daha büyüktür.",
        "hint": "Çok uzun ve ince bir dikdörtgenle, kareye yakın bir dikdörtgeni karşılaştır. "
                "Hangisinin alanı büyük? Hangisinin çevresi büyük?",
    },
]


def check_claim(cid, r1, r2):
    """İki dikdörtgenin iddiayı çürütüp çürütmediğine bakar. (başarılı_mı, mesaj) döndürür."""
    a1, p1 = area(*r1), perimeter(*r1)
    a2, p2 = area(*r2), perimeter(*r2)
    if cid == "I1":
        if a1 != a2:
            return False, ("Bu dikdörtgenlerin alanları farklı (%d ve %d). İddia, alanı aynı olan "
                           "dikdörtgenler için. Alanları aynı olan iki dikdörtgen çiz." % (a1, a2))
        if p1 == p2:
            return False, ("İkisinin de alanı %d, çevresi %d. Bu örnek iddiayı çürütmüyor. "
                           "Alanı aynı olan başka bir dikdörtgen dene." % (a1, p1))
        return True, ("Karşı örnek buldun! İkisinin de alanı %d birimkare ama çevreleri farklı "
                      "(%d ve %d). İddia yanlış." % (a1, p1, p2))
    if cid == "I2":
        if p1 != p2:
            return False, ("Bu dikdörtgenlerin çevreleri farklı (%d ve %d). İddia, çevresi aynı olan "
                           "dikdörtgenler için. Çevreleri aynı olan iki dikdörtgen çiz." % (p1, p2))
        if a1 == a2:
            return False, ("İkisinin de çevresi %d, alanı %d. Bu örnek iddiayı çürütmüyor. "
                           "Çevresi aynı olan başka bir dikdörtgen dene." % (p1, a1))
        return True, ("Karşı örnek buldun! İkisinin de çevresi %d birim ama alanları farklı "
                      "(%d ve %d). İddia yanlış." % (p1, a1, a2))
    if cid == "I3":
        if a1 == a2:
            return False, ("İki dikdörtgenin alanı aynı (%d). Birinin alanı diğerinden büyük olmalı." % a1)
        (ab, pb), (asm, ps) = ((a1, p1), (a2, p2)) if a1 > a2 else ((a2, p2), (a1, p1))
        if pb > ps:
            return False, ("Alanı büyük olan dikdörtgenin (%d) çevresi de büyük çıktı (%d > %d). Bu örnek "
                           "iddiayı çürütmüyor. Alanı büyük ama çevresi büyük olmayan bir çift dene."
                           % (ab, pb, ps))
        return True, ("Karşı örnek buldun! Alanı %d olan dikdörtgenin çevresi %d; alanı %d olan "
                      "dikdörtgenin çevresi %d. Alanı büyük olanın çevresi daha büyük çıkmadı. İddia yanlış."
                      % (ab, pb, asm, ps))
    return False, ""


# ════════════════════════ KAYIT (CSV) ════════════════════════
class Logger:
    FIELDS = ["zaman", "ogrenci", "gorev", "olay", "hedef", "w1", "h1", "alan1", "cevre1",
              "w2", "h2", "alan2", "cevre2", "cevap", "dogru", "deneme_no", "sure_sn", "ek"]

    def __init__(self):
        self.enabled = LOGGING
        self.path = None
        if self.enabled:
            self._prepare()

    def _prepare(self):
        folders = [os.path.dirname(os.path.abspath(sys.argv[0])), os.path.expanduser("~")]
        for folder in folders:
            path = os.path.join(folder, LOG_FILE)
            try:
                new = (not os.path.exists(path)) or os.path.getsize(path) == 0
                with open(path, "a", newline="", encoding="utf-8-sig") as f:
                    if new:
                        csv.writer(f, delimiter=";").writerow(self.FIELDS)
                self.path = path
                return
            except OSError:
                continue
        self.enabled = False  # yazılamıyorsa oyun yine de çalışsın

    def write(self, student, task, event, **kw):
        if not self.enabled:
            return
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), student, task, event]
        row += [kw.get(k, "") for k in self.FIELDS[4:]]
        try:
            with open(self.path, "a", newline="", encoding="utf-8-sig") as f:
                csv.writer(f, delimiter=";").writerow(row)
        except OSError:
            self.enabled = False


def rf(r, n="1"):
    """Bir dikdörtgenin bilgilerini kayıt alanlarına çevirir."""
    return {"w" + n: r[0], "h" + n: r[1], "alan" + n: area(*r), "cevre" + n: perimeter(*r)}


# ════════════════════════ ARAYÜZ PARÇALARI ════════════════════════
def make_font(size, bold=False):
    names = "arial,calibri,segoeui,dejavusans,liberationsans,verdana,tahoma"
    try:
        return pygame.font.SysFont(names, size, bold=bold)
    except Exception:
        return pygame.font.Font(None, int(size * 1.3))


def wrap(font, text, width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if font.size(trial)[0] <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


class Button:
    def __init__(self, x, y, w, h, text, color=BTN):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, font, enabled=True, sub=None, subfont=None, text=None, color=None):
        col = (color or self.color) if enabled else BTN_OFF
        if enabled and self.rect.collidepoint(pygame.mouse.get_pos()):
            col = tuple(min(255, c + 25) for c in col)
        pygame.draw.rect(surf, col, self.rect)
        pygame.draw.rect(surf, DARK, self.rect, 2)
        img = font.render(text if text is not None else self.text, True, WHITE)
        if sub:
            surf.blit(img, (self.rect.x + 16, self.rect.y + 10))
            surf.blit(subfont.render(sub, True, WHITE), (self.rect.x + 16, self.rect.y + 14 + img.get_height()))
        else:
            surf.blit(img, (self.rect.centerx - img.get_width() // 2,
                            self.rect.centery - img.get_height() // 2))


class GridPicker:
    """Birim karelerden oluşan ızgara. Tıkla/sürükle: sol üst köşeden dikdörtgen seçilir."""

    def __init__(self, x, y, cols, rows, cell, color):
        self.x, self.y, self.cols, self.rows, self.cell = x, y, cols, rows, cell
        self.color = color
        self.sel = None      # (genişlik, yükseklik)
        self.hover = None
        self.dragging = False

    def _cell_at(self, pos, clamp=False):
        c = (pos[0] - self.x) // self.cell
        r = (pos[1] - self.y) // self.cell
        if clamp:
            c = min(max(c, 0), self.cols - 1)
            r = min(max(r, 0), self.rows - 1)
        elif not (0 <= c < self.cols and 0 <= r < self.rows):
            return None
        return (c + 1, r + 1)

    def handle(self, ev):
        """Seçim değiştiyse True döndürür."""
        if ev.type == pygame.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 1:
            cell = self._cell_at(ev.pos)
            if cell:
                self.dragging = True
                changed = cell != self.sel
                self.sel = cell
                return changed
        elif ev.type == pygame.MOUSEMOTION:
            if self.dragging:
                cell = self._cell_at(ev.pos, clamp=True)
                if cell != self.sel:
                    self.sel = cell
                    return True
            else:
                self.hover = self._cell_at(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONUP and getattr(ev, "button", 1) == 1:
            self.dragging = False
        return False

    def freeze(self):
        self.dragging = False
        self.hover = None

    def draw(self, s, interactive=True, border=False):
        cell = self.cell
        pygame.draw.rect(s, WHITE, (self.x, self.y, self.cols * cell, self.rows * cell))
        if interactive and self.hover and not self.dragging:
            pygame.draw.rect(s, HOVER, (self.x, self.y, self.hover[0] * cell, self.hover[1] * cell))
        if self.sel:
            pygame.draw.rect(s, self.color, (self.x, self.y, self.sel[0] * cell, self.sel[1] * cell))
        for c in range(self.cols + 1):
            xx = self.x + c * cell
            pygame.draw.line(s, GRID, (xx, self.y), (xx, self.y + self.rows * cell))
        for r in range(self.rows + 1):
            yy = self.y + r * cell
            pygame.draw.line(s, GRID, (self.x, yy), (self.x + self.cols * cell, yy))
        if self.sel:
            pygame.draw.rect(s, RED if border else DARK,
                             (self.x, self.y, self.sel[0] * cell, self.sel[1] * cell), 5 if border else 3)
        pygame.draw.rect(s, DARK, (self.x, self.y, self.cols * cell, self.rows * cell), 2)


def is_digit_key(ev):
    return len(ev.unicode) == 1 and ev.unicode in "0123456789"


def is_enter(ev):
    return ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER)


def is_click(ev):
    return ev.type == pygame.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 1


# ════════════════════════ OYUN ════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        flags = pygame.RESIZABLE | getattr(pygame, "SCALED", 0)
        try:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except Exception:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Alan – Çevre Oyunu")
        self.clock = pygame.time.Clock()
        self.f_s, self.f_n = make_font(20), make_font(22)
        self.f_m, self.f_l, self.f_xl = make_font(26, True), make_font(36, True), make_font(46, True)

        self.logger = Logger()
        self.student = ""
        self.task = None
        self.task_t0 = time.time()
        self.done = set()
        self.menu_msg = ""
        self.input_text = ""
        self.msg, self.msg_color = "", INK
        self.scr = "name"
        self.running = True

        self.B = {
            "start": Button(380, 330, 240, 50, "Başla"),
            "m1": Button(200, 140, 600, 84, ""),
            "m2": Button(200, 240, 600, 84, ""),
            "m3": Button(200, 340, 600, 84, ""),
            "change": Button(30, 592, 220, 40, "Öğrenci değiştir", (110, 120, 140)),
            "quit": Button(880, 592, 90, 40, "Çıkış", RED),
            "menu": Button(880, 8, 100, 40, "Menü", (110, 120, 140)),
            "check": Button(30, 592, 180, 40, "Kontrol Et", GREEN),
            "finish": Button(225, 592, 260, 40, "Bitir ve Karşılaştır", ORANGE_D),
            "send": Button(365, 466, 120, 40, "Gönder", GREEN),
            "next": Button(30, 592, 230, 40, "Devam", GREEN),
            "try": Button(30, 592, 210, 40, "Karşı örneği dene", GREEN),
            "hint": Button(255, 592, 110, 40, "İpucu", ORANGE_D),
            "skip": Button(380, 592, 160, 40, "İddiayı geç", (110, 120, 140)),
        }

    # ─────────────── genel yardımcılar ───────────────
    def log(self, event, **kw):
        if "sure_sn" not in kw:
            kw["sure_sn"] = round(time.time() - self.task_t0, 1) if self.task else ""
        self.logger.write(self.student, self.task or "", event, **kw)

    def say(self, text, color=INK):
        self.msg, self.msg_color = text, color

    def text(self, s, font, txt, x, y, color=INK, width=None):
        for para in str(txt).split("\n"):
            for line in (wrap(font, para, width) if width else [para]):
                if line:
                    s.blit(font.render(line, True, color), (x, y))
                y += font.get_height() + 4
        return y

    def feedback_panel(self, s):
        pygame.draw.rect(s, WHITE, (30, 508, 630, 80))
        pygame.draw.rect(s, GREY, (30, 508, 630, 80), 2)
        if self.msg:
            self.text(s, self.f_s, self.msg, 40, 514, self.msg_color, width=610)

    def header(self, s, title, with_menu=True):
        pygame.draw.rect(s, BLUE_D, (0, 0, WIDTH, 56))
        self.text(s, self.f_m, title, 20, 12, WHITE)
        if with_menu:
            self.text(s, self.f_s, "Öğrenci: " + self.student, 620, 16, WHITE)
            self.B["menu"].draw(s, self.f_s)

    # ─────────────── ana döngü ───────────────
    def run(self):
        while self.running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle(ev)
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        self.log("oyun_kapandi")
        pygame.quit()

    def handle(self, ev):
        if (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE
                and self.scr in ("build", "answer", "compare", "claim")):
            self.back_to_menu("esc")
            return
        getattr(self, "on_" + self.scr)(ev)

    def draw(self):
        self.screen.fill(BG)
        getattr(self, "draw_" + self.scr)(self.screen)

    # ─────────────── ad girişi ───────────────
    def on_name(self, ev):
        if is_enter(ev) or (is_click(ev) and self.B["start"].hit(ev.pos)):
            self.student = self.input_text.strip() or "ogrenci"
            self.input_text = ""
            self.scr = "menu"
            self.log("oyun_basladi")
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif ev.unicode and ev.unicode.isprintable() and len(self.input_text) < 20:
                self.input_text += ev.unicode

    def draw_name(self, s):
        self.header(s, "Alan – Çevre Oyunu", with_menu=False)
        self.text(s, self.f_l, "Merhaba!", 380, 120)
        self.text(s, self.f_n, "Adını ya da öğrenci kodunu yaz, sonra Enter'a bas.", 250, 200)
        pygame.draw.rect(s, WHITE, (300, 250, 400, 52))
        pygame.draw.rect(s, DARK, (300, 250, 400, 52), 2)
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        self.text(s, self.f_m, self.input_text + cursor, 312, 260)
        self.B["start"].draw(s, self.f_m)

    # ─────────────── menü ───────────────
    def on_menu(self, ev):
        if not is_click(ev):
            return
        for key, task in (("m1", "alan"), ("m2", "cevre"), ("m3", "iddia")):
            if self.B[key].hit(ev.pos):
                self.start_task(task)
                return
        if self.B["change"].hit(ev.pos):
            self.input_text = ""
            self.scr = "name"
        elif self.B["quit"].hit(ev.pos):
            self.running = False

    def draw_menu(self, s):
        self.header(s, "Alan – Çevre Oyunu", with_menu=False)
        self.text(s, self.f_n, "Öğrenci: " + self.student, 30, 70)
        self.text(s, self.f_m, "Bir görev seç:", 200, 100)
        info = (("m1", "alan", "1. Aynı alan – farklı çevre", "Alanı verilen dikdörtgenleri çiz, çevrelerini bul."),
                ("m2", "cevre", "2. Aynı çevre – farklı alan", "Çevresi verilen dikdörtgenleri çiz, alanlarını bul."),
                ("m3", "iddia", "3. İddia sınama", "Bir iddiayı karşı örnek çizerek sına."))
        for key, task, label, sub in info:
            title = label + ("   [Tamamlandı]" if task in self.done else "")
            self.B[key].draw(s, self.f_m, sub=sub, subfont=self.f_s, text=title)
        if self.menu_msg:
            self.text(s, self.f_n, self.menu_msg, 200, 440, GREEN, width=600)
        pygame.draw.rect(s, WHITE, (30, 480, 940, 90))
        pygame.draw.rect(s, GREY, (30, 480, 940, 90), 2)
        self.text(s, self.f_s, "Nasıl oynanır? Izgaraya tıkla ya da basılı tutup sürükle: sol üst köşeden başlayan "
                               "bir dikdörtgen çizilir. Her kare 1 birimkaredir, bir karenin kenarı 1 birimdir. "
                               "Görevden çıkmak için Esc tuşuna veya Menü düğmesine bas.", 42, 490, INK, width=916)
        self.B["change"].draw(s, self.f_s)
        self.B["quit"].draw(s, self.f_s)

    def start_task(self, task):
        self.task = task
        self.task_t0 = time.time()
        self.menu_msg = ""
        self.log("gorev_basladi")
        if task == "iddia":
            self.start_claim(0)
        else:
            self.start_round(0)

    def back_to_menu(self, why=""):
        self.log("gorevden_cikis", ek=why + ":" + self.scr)
        self.task = None
        self.scr = "menu"

    def finish_task(self):
        self.log("gorev_bitti")
        self.done.add(self.task)
        self.menu_msg = TASK_NAMES[self.task] + " tamamlandı. Aferin!"
        self.task = None
        self.scr = "menu"

    # ═════════════ GÖREV 1 ve 2: dikdörtgen bul, ölçüyü yaz, karşılaştır ═════════════
    def rounds(self):
        return AREA_ROUNDS if self.task == "alan" else PERIMETER_ROUNDS

    def asked(self):
        """Öğrenciden istenen ölçü: (ad, birim)."""
        return ("çevre", "birim") if self.task == "alan" else ("alan", "birimkare")

    def start_round(self, i):
        self.round = i
        self.target = self.rounds()[i]
        if self.task == "alan":
            self.all_rects = rects_with_area(self.target)
            longest = self.target
        else:
            self.all_rects = rects_with_perimeter(self.target)
            longest = self.target // 2 - 1
        cols = max(12, longest)
        cell = min(30, 630 // cols, 27)
        self.grid = GridPicker(30, 135, cols, 12, cell, BLUE)
        self.found = {}          # norm(dikdörtgen) -> {"revealed": bool}
        self.cur = None
        self.tries = 0
        self.hint_border = False
        self.input_text = ""
        self.scr = "build"
        self.say("")
        self.log("tur_basladi", hedef=self.target)

    # ---------- dikdörtgen çizme ----------
    def on_build(self, ev):
        self.grid.handle(ev)
        if is_enter(ev):
            self.check_build()
        elif is_click(ev):
            if self.B["menu"].hit(ev.pos):
                self.back_to_menu("menu")
            elif self.B["check"].hit(ev.pos):
                self.check_build()
            elif self.B["finish"].hit(ev.pos) and len(self.found) >= 2:
                self.start_compare("Şimdi bulduğun dikdörtgenleri karşılaştıralım.")

    def check_build(self):
        if not self.grid.sel:
            return
        r = self.grid.sel
        w, h = r
        a, p = area(w, h), perimeter(w, h)
        measure = a if self.task == "alan" else p
        ok = measure == self.target
        dup = ok and norm(r) in self.found
        self.log("deneme", hedef=self.target, dogru=int(ok and not dup),
                 ek="tekrar" if dup else "", **rf(r))
        if not ok:
            if self.task == "alan":
                self.say("%d × %d dikdörtgeninde %d birimkare var. Hedef: %d birimkare. "
                         "Kareleri say ve tekrar dene." % (w, h, a, self.target), RED)
            else:
                self.say("%d × %d dikdörtgeninin çevresi %d birim. Hedef: %d birim. "
                         "Tekrar dene." % (w, h, p, self.target), RED)
        elif dup:
            self.say("Bu dikdörtgeni zaten buldun (%d × %d ile %d × %d aynı dikdörtgendir). "
                     "Farklı bir tane dene." % (w, h, h, w), ORANGE_D)
        else:
            self.cur = r
            self.tries = 0
            self.input_text = ""
            self.hint_border = False
            self.grid.freeze()
            self.scr = "answer"
            if self.task == "alan":
                self.say("Süper! %d × %d dikdörtgeninin alanı %d birimkare. Şimdi bu dikdörtgenin "
                         "ÇEVRESİNİ yaz." % (w, h, self.target), GREEN)
            else:
                self.say("Süper! %d × %d dikdörtgeninin çevresi %d birim. Şimdi bu dikdörtgenin "
                         "ALANINI yaz." % (w, h, self.target), GREEN)

    # ---------- cevap yazma ----------
    def on_answer(self, ev):
        if is_enter(ev):
            self.submit_answer()
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif is_digit_key(ev) and len(self.input_text) < 3:
                self.input_text += ev.unicode
        elif is_click(ev):
            if self.B["menu"].hit(ev.pos):
                self.back_to_menu("menu")
            elif self.B["send"].hit(ev.pos):
                self.submit_answer()

    def submit_answer(self):
        if not self.input_text:
            self.say("Önce bir sayı yaz.", ORANGE_D)
            return
        w, h = self.cur
        name, unit = self.asked()
        correct = perimeter(w, h) if self.task == "alan" else area(w, h)
        value = int(self.input_text)
        self.tries += 1
        ok = value == correct
        self.log("cevap", hedef=self.target, cevap=value, dogru=int(ok), deneme_no=self.tries, **rf(self.cur))
        self.input_text = ""
        if ok:
            self.found[norm(self.cur)] = {"revealed": False}
            self.after_answer("Doğru! %d × %d dikdörtgeninin %s %d %s." % (w, h, name, correct, unit), GREEN)
        elif self.tries >= 3:
            self.found[norm(self.cur)] = {"revealed": True}
            self.after_answer("Doğrusu %d %s. Tabloya yazdım, bir sonrakinde dikkatli say!" % (correct, unit),
                              ORANGE_D)
        elif self.tries == 1:
            if self.task == "alan":
                self.hint_border = True
                self.say("Tam olmadı. Çevre, şeklin dış çizgisinin (kırmızı) uzunluğudur. "
                         "Kenarları say ve tekrar dene.", RED)
            else:
                self.say("Tam olmadı. Alan, içindeki birimkarelerin sayısıdır. Kareleri say "
                         "(ya da satır × sütun yap) ve tekrar dene.", RED)
        else:
            if self.task == "alan":
                self.say("Bir köşeden başla, dört kenarı da say: %d + %d + %d + %d. Tekrar dene."
                         % (w, h, w, h), RED)
            else:
                self.say("Her satırda %d kare var, %d satır var. Hepsini say ya da çarp. Tekrar dene."
                         % (w, h), RED)

    def after_answer(self, text, color):
        self.cur = None
        self.hint_border = False
        self.grid.sel = None
        self.say(text, color)
        if len(self.found) == len(self.all_rects):
            self.start_compare(text + " Hepsini buldun! Şimdi karşılaştıralım.", color)
        else:
            self.scr = "build"

    # ---------- karşılaştırma soruları ----------
    def start_compare(self, text, color=INK):
        self.scr = "compare"
        self.cq = 0
        self.cq_done = False
        self.cq_choice = None
        self.say(text, color)
        self.make_compare_buttons()

    def make_compare_buttons(self):
        if self.cq == 0:
            self.cbtns = [(Button(30, 210, 320, 46, "Evet, hepsi aynı"), "evet"),
                          (Button(30, 266, 320, 46, "Hayır, farklı"), "hayir")]
        else:
            self.cbtns = [(Button(30, 190 + i * 56, 320, 46, "%d × %d" % r), r)
                          for i, r in enumerate(sorted(self.found))]

    def best_rect(self):
        if self.task == "alan":
            return min(self.found, key=lambda r: perimeter(*r))   # en küçük çevre
        return max(self.found, key=lambda r: area(*r))            # en büyük alan

    def compare_correct(self):
        return "hayir" if self.cq == 0 else self.best_rect()

    def compare_question(self):
        if self.cq == 0:
            if self.task == "alan":
                return ("Bulduğun dikdörtgenlerin hepsinin alanı %d birimkare. "
                        "Çevreleri de hepsi aynı mı?" % self.target)
            return ("Bulduğun dikdörtgenlerin hepsinin çevresi %d birim. "
                    "Alanları da hepsi aynı mı?" % self.target)
        if self.task == "alan":
            return "Hangi dikdörtgenin çevresi en küçük?"
        return "Hangi dikdörtgenin alanı en büyük?"

    def values_text(self):
        name, _ = self.asked()
        if self.task == "alan":
            vals = [perimeter(*r) for r in sorted(self.found)]
        else:
            vals = [area(*r) for r in sorted(self.found)]
        return name, ", ".join(str(v) for v in vals)

    def on_compare(self, ev):
        if not is_click(ev):
            return
        if self.B["menu"].hit(ev.pos):
            self.back_to_menu("menu")
        elif not self.cq_done:
            for btn, val in self.cbtns:
                if btn.hit(ev.pos):
                    self.answer_compare(val)
                    break
        elif self.B["next"].hit(ev.pos):
            self.compare_next()

    def answer_compare(self, val):
        self.cq_done = True
        self.cq_choice = val
        ok = val == self.compare_correct()
        name, vals = self.values_text()
        cevap = val if self.cq == 0 else "%dx%d" % val
        self.log("karsilastirma_%d" % (self.cq + 1), hedef=self.target, cevap=cevap, dogru=int(ok))
        if self.cq == 0:
            if ok:
                self.say("Doğru! Tablodaki %s sütununa bak: %s. Hepsi farklı." % (name, vals), GREEN)
            else:
                self.say("Tabloya bir daha bak: %s değerleri %s. Hepsi aynı değil." % (name, vals), RED)
        else:
            best = self.best_rect()
            if self.task == "alan":
                rule = "Alan aynıyken dikdörtgen kareye yaklaştıkça çevre küçülür."
                what = "çevre en küçük"
            else:
                rule = "Çevre aynıyken dikdörtgen kareye yaklaştıkça alan büyür."
                what = "alan en büyük"
            if ok:
                self.say("Doğru! %d × %d dikdörtgeninde %s. %s" % (best[0], best[1], what, rule), GREEN)
            else:
                self.say("Olmadı. Tabloya bak: %s %d × %d dikdörtgeninde. %s" % (what, best[0], best[1], rule), RED)

    def compare_next(self):
        if self.cq == 0:
            self.cq = 1
            self.cq_done = False
            self.cq_choice = None
            self.say("")
            self.make_compare_buttons()
        elif self.round + 1 >= len(self.rounds()):
            self.finish_task()
        else:
            self.start_round(self.round + 1)

    # ---------- GÖREV 1/2 çizimleri ----------
    def draw_table(self, s):
        x, y, w = 690, 70, 280
        pygame.draw.rect(s, WHITE, (x, y, w, 400))
        pygame.draw.rect(s, GREY, (x, y, w, 400), 2)
        self.text(s, self.f_n, "Bulduklarım: %d / %d" % (len(self.found), len(self.all_rects)), x + 12, y + 10, DARK)
        for label, dx in (("Şekil", 12), ("Alan", 130), ("Çevre", 200)):
            self.text(s, self.f_s, label, x + dx, y + 50, DARK)
        pygame.draw.line(s, GREY, (x + 8, y + 76), (x + w - 8, y + 76), 2)
        yy = y + 86
        for r in sorted(self.found):
            col = ORANGE_D if self.found[r]["revealed"] else INK
            self.text(s, self.f_n, "%d × %d" % r, x + 12, yy, col)
            self.text(s, self.f_n, str(area(*r)), x + 130, yy, col)
            self.text(s, self.f_n, str(perimeter(*r)), x + 200, yy, col)
            yy += 34
        if self.cur and self.scr == "answer":
            a, p = area(*self.cur), perimeter(*self.cur)
            self.text(s, self.f_n, "%d × %d" % self.cur, x + 12, yy, BLUE_D)
            self.text(s, self.f_n, str(a) if self.task == "alan" else "?", x + 130, yy, BLUE_D)
            self.text(s, self.f_n, "?" if self.task == "alan" else str(p), x + 200, yy, BLUE_D)

    def goal_text(self):
        n = "%d/%d  " % (self.round + 1, len(self.rounds()))
        if self.task == "alan":
            return n + "Alanı %d birimkare olan FARKLI dikdörtgenleri bul ve çevrelerini yaz." % self.target
        return n + "Çevresi %d birim olan FARKLI dikdörtgenleri bul ve alanlarını yaz." % self.target

    def draw_build(self, s):
        self.header(s, TASK_NAMES[self.task])
        self.text(s, self.f_n, self.goal_text(), 30, 68, INK, width=640)
        self.grid.draw(s, interactive=True)
        if self.grid.sel:
            self.text(s, self.f_n, "Seçtiğin: %d × %d" % self.grid.sel, 30, 474)
        else:
            self.text(s, self.f_n, "Izgaradan bir dikdörtgen seç.", 30, 474, GREY)
        self.feedback_panel(s)
        self.B["check"].draw(s, self.f_n, enabled=bool(self.grid.sel))
        self.B["finish"].draw(s, self.f_n, enabled=len(self.found) >= 2)
        self.draw_table(s)

    def draw_answer(self, s):
        self.header(s, TASK_NAMES[self.task])
        self.text(s, self.f_n, self.goal_text(), 30, 68, INK, width=640)
        self.grid.draw(s, interactive=False, border=self.hint_border)
        name, unit = self.asked()
        self.text(s, self.f_n, "%s (%s):" % (name.capitalize(), unit), 30, 474)
        pygame.draw.rect(s, WHITE, (240, 466, 110, 40))
        pygame.draw.rect(s, DARK, (240, 466, 110, 40), 2)
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        self.text(s, self.f_m, self.input_text + cursor, 250, 470)
        self.B["send"].draw(s, self.f_n)
        self.feedback_panel(s)
        self.draw_table(s)

    def draw_compare(self, s):
        self.header(s, TASK_NAMES[self.task])
        self.text(s, self.f_m, self.compare_question(), 30, 70, INK, width=630)
        correct = self.compare_correct()
        for btn, val in self.cbtns:
            if not self.cq_done:
                btn.draw(s, self.f_n)
            elif val == correct:
                btn.draw(s, self.f_n, color=GREEN)
            elif val == self.cq_choice:
                btn.draw(s, self.f_n, color=RED)
            else:
                btn.draw(s, self.f_n, enabled=False)
        self.feedback_panel(s)
        if self.cq_done:
            last = self.cq == 1
            more = self.round + 1 < len(self.rounds())
            label = "Devam" if not last else ("Sonraki soru" if more else "Görevi bitir")
            self.B["next"].draw(s, self.f_n, text=label)
        self.draw_table(s)

    # ═════════════ GÖREV 3: İddia sınama ═════════════
    def start_claim(self, i):
        self.round = i
        self.claim = CLAIMS[i]
        self.g1 = GridPicker(30, 160, 12, 12, 24, BLUE)
        self.g2 = GridPicker(350, 160, 12, 12, 24, ORANGE)
        self.claim_tries = 0
        self.claim_solved = False
        self.last_try = None
        self.scr = "claim"
        self.say("İki dikdörtgen çizip iddiayı çürütmeye çalış. Sonra \"Karşı örneği dene\"ye bas.")
        self.log("iddia_basladi", ek=self.claim["id"])

    def on_claim(self, ev):
        if self.claim_solved:
            if is_click(ev):
                if self.B["menu"].hit(ev.pos):
                    self.back_to_menu("menu")
                elif self.B["next"].hit(ev.pos):
                    self.claim_next()
            return
        self.g1.handle(ev)
        self.g2.handle(ev)
        if is_enter(ev):
            self.try_claim()
        elif is_click(ev):
            if self.B["menu"].hit(ev.pos):
                self.back_to_menu("menu")
            elif self.B["try"].hit(ev.pos):
                self.try_claim()
            elif self.B["hint"].hit(ev.pos):
                self.log("ipucu", ek=self.claim["id"])
                self.say("İpucu: " + self.claim["hint"], ORANGE_D)
            elif self.B["skip"].hit(ev.pos):
                self.log("iddia_bitti", ek=self.claim["id"] + ":gecildi", deneme_no=self.claim_tries)
                self.claim_next()

    def try_claim(self):
        if not (self.g1.sel and self.g2.sel):
            self.say("Önce iki dikdörtgeni de çiz (Dikdörtgen 1 ve Dikdörtgen 2).", ORANGE_D)
            return
        r1, r2 = self.g1.sel, self.g2.sel
        ok, msg = check_claim(self.claim["id"], r1, r2)
        self.claim_tries += 1
        self.last_try = (r1, r2)
        self.log("iddia_deneme", dogru=int(ok), deneme_no=self.claim_tries,
                 ek=self.claim["id"], **dict(rf(r1, "1"), **rf(r2, "2")))
        self.say(msg, GREEN if ok else RED)
        if ok:
            self.claim_solved = True
            self.g1.freeze()
            self.g2.freeze()
            self.log("iddia_bitti", ek=self.claim["id"] + ":karsi_ornek_bulundu", deneme_no=self.claim_tries)

    def claim_next(self):
        if self.round + 1 >= len(CLAIMS):
            self.finish_task()
        else:
            self.start_claim(self.round + 1)

    def draw_claim(self, s):
        self.header(s, TASK_NAMES[self.task])
        self.text(s, self.f_m, "%d/%d  %s" % (self.round + 1, len(CLAIMS), self.claim["text"]), 30, 64, INK, width=940)
        live = not self.claim_solved
        for g, label in ((self.g1, "Dikdörtgen 1"), (self.g2, "Dikdörtgen 2")):
            self.text(s, self.f_n, label, g.x, 134, DARK)
            g.draw(s, interactive=live)
            sel = "%d × %d" % g.sel if g.sel else "—"
            self.text(s, self.f_n, "Seçtiğin: " + sel, g.x, 454)
        # sağ panel: son deneme
        pygame.draw.rect(s, WHITE, (690, 134, 280, 330))
        pygame.draw.rect(s, GREY, (690, 134, 280, 330), 2)
        self.text(s, self.f_n, "Son denemen", 702, 144, DARK)
        if self.last_try:
            yy = 184
            for i, r in enumerate(self.last_try):
                self.text(s, self.f_n, "Dikdörtgen %d: %d × %d" % ((i + 1,) + r), 702, yy, INK)
                self.text(s, self.f_s, "alan = %d, çevre = %d" % (area(*r), perimeter(*r)), 702, yy + 28, INK)
                yy += 70
            self.text(s, self.f_s, "Deneme sayısı: %d" % self.claim_tries, 702, yy + 10, INK)
        self.feedback_panel(s)
        if self.claim_solved:
            more = self.round + 1 < len(CLAIMS)
            self.B["next"].draw(s, self.f_n, text="Sonraki iddia" if more else "Görevi bitir")
        else:
            ready = bool(self.g1.sel and self.g2.sel)
            self.B["try"].draw(s, self.f_n, enabled=ready)
            self.B["hint"].draw(s, self.f_n)
            self.B["skip"].draw(s, self.f_n)


def main():
    check_config()
    Game().run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        input("Bir hata oluştu. Kapatmak için Enter'a bas...")
