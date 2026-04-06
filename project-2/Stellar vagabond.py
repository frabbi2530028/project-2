"""
Stellar Vagabond: Nuclear Age Space Trader
==========================================
Requires:  pip install arcade   (Arcade 3.x)
Run:       python stellar_vagabond.py
"""

import arcade
import random
import math

# ── SCREEN ─────────────────────────────────────────────────────────────────────
SCREEN_W = 1200
SCREEN_H = 800
TITLE    = "Stellar Vagabond: Nuclear Age Space Trader"

# ── COLOURS ────────────────────────────────────────────────────────────────────
DARK_BG  = (8,   12,  30)
PANEL_BG = (15,  25,  55)
WHITE    = (255, 255, 255)
GRAY     = (100, 100, 120)
YELLOW   = (255, 220,  50)
ORANGE   = (255, 140,   0)
CYAN     = ( 50, 220, 220)
GREEN    = ( 50, 220, 100)
RED      = (220,  50,  50)

# ── TRAVEL COSTS  (fuel_rods, reactor_drain) ───────────────────────────────────
TRAVEL = {
    "galaxy": (15, 20),
    "star":   ( 8, 10),
    "planet": ( 3,  5),
}

# ── UNIVERSE DATA ──────────────────────────────────────────────────────────────
UNIVERSE_DATA = [
    {
        "name": "Solaris Prime", "color": (255, 200, 50), "pos": (280, 500),
        "systems": [
            {
                "name": "Alpha Centauri", "star_color": (255, 230, 120),
                "planets": [
                    {"name": "Dustara",  "danger": 1, "market": {"fuel_rods": 45, "minerals": 30, "tech": 80}},
                    {"name": "Verdis",   "danger": 2, "market": {"fuel_rods": 40, "minerals": 60, "tech": 70}},
                    {"name": "Ironhold", "danger": 1, "market": {"fuel_rods": 60, "minerals": 20, "tech": 90}},
                ],
            },
            {
                "name": "Tau Ceti", "star_color": (255, 180, 80),
                "planets": [
                    {"name": "Glacius", "danger": 2, "market": {"fuel_rods": 45, "minerals": 70, "tech": 60}},
                    {"name": "Pyra",    "danger": 3, "market": {"fuel_rods": 35, "minerals": 80, "tech": 50}},
                ],
            },
        ],
    },
    {
        "name": "Nebula Drift", "color": (150, 60, 230), "pos": (750, 540),
        "systems": [
            {
                "name": "Krypton Veil", "star_color": (200, 120, 255),
                "planets": [
                    {"name": "Shardis", "danger": 3, "market": {"fuel_rods": 70, "minerals": 25, "tech": 100}},
                    {"name": "Umbra",   "danger": 4, "market": {"fuel_rods": 80, "minerals": 30, "tech": 110}},
                ],
            },
            {
                "name": "Void Core", "star_color": (120, 60, 200),
                "planets": [
                    {"name": "Phantom", "danger": 4, "market": {"fuel_rods": 90,  "minerals": 15, "tech": 120}},
                    {"name": "Abyss",   "danger": 5, "market": {"fuel_rods": 100, "minerals": 10, "tech": 130}},
                ],
            },
        ],
    },
    {
        "name": "Iron Expanse", "color": (210, 120, 40), "pos": (520, 230),
        "systems": [
            {
                "name": "Ferro Prime", "star_color": (255, 160, 60),
                "planets": [
                    {"name": "Rustium",  "danger": 2, "market": {"fuel_rods": 65, "minerals": 10, "tech": 75}},
                    {"name": "Cinder",   "danger": 3, "market": {"fuel_rods": 75, "minerals": 15, "tech": 85}},
                ],
            },
            {
                "name": "Slag Reach", "star_color": (230, 140, 70),
                "planets": [
                    {"name": "Moltenix", "danger": 3, "market": {"fuel_rods": 55, "minerals": 20, "tech":  95}},
                    {"name": "Scorchis", "danger": 4, "market": {"fuel_rods": 85, "minerals":  5, "tech": 115}},
                ],
            },
        ],
    },
]

# ── DATA MODEL ─────────────────────────────────────────────────────────────────

class Planet:
    def __init__(self, data):
        self.name   = data["name"]
        self.danger = data["danger"]
        self.prices = dict(data["market"])
        self.stock  = {k: random.randint(8, 25) for k in ["fuel_rods", "minerals", "tech"]}

class SolarSystem:
    def __init__(self, data):
        self.name       = data["name"]
        self.star_color = data["star_color"]
        self.planets    = [Planet(p) for p in data["planets"]]

class Galaxy:
    def __init__(self, data):
        self.name      = data["name"]
        self.color     = data["color"]
        self.x, self.y = data["pos"]
        self.systems   = [SolarSystem(s) for s in data["systems"]]

class Ship:
    def __init__(self):
        self.cargo_capacity  = 50
        self.fuel_efficiency = 1.0

class Player:
    def __init__(self):
        self.credits        = 1000
        self.reactor_energy = 100
        self.max_reactor    = 100
        self.fuel_rods      = 25
        self.cargo          = {"minerals": 0, "tech": 0}
        self.ship           = Ship()
        self.current_galaxy = None
        self.current_system = None
        self.current_planet = None

    @property
    def cargo_used(self):
        return sum(self.cargo.values())

    def travel(self, travel_type):
        rod_cost, reactor_cost = TRAVEL[travel_type]
        if self.fuel_rods < rod_cost:
            return False, "Not enough fuel rods!"
        self.fuel_rods      -= rod_cost
        self.reactor_energy  = max(0, self.reactor_energy - reactor_cost)
        return True, ""

    def recharge(self, rods_used=5):
        if self.fuel_rods < rods_used:
            return False
        self.fuel_rods      -= rods_used
        self.reactor_energy  = min(self.max_reactor, self.reactor_energy + rods_used * 4)
        return True

    def is_dead(self):
        return self.reactor_energy <= 0

# ── ARCADE 3.x DRAWING WRAPPERS ────────────────────────────────────────────────
# Arcade 3.x replaced draw_rectangle_* with draw_rect_* using XYWH/LBWH rects.

def fill_rect(cx, cy, w, h, color):
    arcade.draw_rect_filled(arcade.XYWH(cx, cy, w, h), color)

def outline_rect(cx, cy, w, h, color, border=2):
    arcade.draw_rect_outline(arcade.XYWH(cx, cy, w, h), color, border)

def fill_circle(cx, cy, r, color):
    arcade.draw_circle_filled(cx, cy, r, color)

def outline_circle(cx, cy, r, color, border=2):
    arcade.draw_circle_outline(cx, cy, r, color, border)

def dline(x1, y1, x2, y2, color, width=1):
    arcade.draw_line(x1, y1, x2, y2, color, width)

def dtext(text, x, y, color, size=12, anchor_x="left", anchor_y="baseline", bold=False):
    arcade.draw_text(text, x, y, color,
                     font_size=size, anchor_x=anchor_x, anchor_y=anchor_y, bold=bold)

# ── BUTTON ─────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, text, color, hover_color=(70, 70, 150)):
        self.x, self.y   = x, y
        self.w, self.h   = w, h
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.hovered     = False
        self.enabled     = True

    def _hit(self, mx, my):
        return abs(mx - self.x) <= self.w / 2 and abs(my - self.y) <= self.h / 2

    def update_hover(self, mx, my):
        self.hovered = self.enabled and self._hit(mx, my)

    def clicked(self, mx, my):
        return self.enabled and self._hit(mx, my)

    def draw(self):
        col = self.hover_color if self.hovered else self.color
        if not self.enabled:
            col = GRAY
        fill_rect(self.x, self.y, self.w, self.h, col)
        outline_rect(self.x, self.y, self.w, self.h, WHITE, 2)
        size = 12 if len(self.text) > 20 else 14
        dtext(self.text, self.x, self.y, WHITE,
              size=size, anchor_x="center", anchor_y="center", bold=True)

# ── SHARED HELPERS ─────────────────────────────────────────────────────────────

def make_stars(n=300):
    return [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H),
             random.uniform(0.5, 2.0), random.randint(80, 220))
            for _ in range(n)]

def draw_stars(stars):
    for sx, sy, size, b in stars:
        fill_circle(sx, sy, size, (b, b, b))

def draw_hud(player):
    fill_rect(SCREEN_W / 2, SCREEN_H - 25, SCREEN_W, 50, PANEL_BG)
    dline(0, SCREEN_H - 50, SCREEN_W, SCREEN_H - 50, CYAN, 1)

    dtext(f"CR  {player.credits}", 20, SCREEN_H - 32,
          YELLOW, size=15, anchor_y="center", bold=True)
    dtext(f"Fuel Rods  {player.fuel_rods}", 200, SCREEN_H - 32,
          ORANGE, size=15, anchor_y="center", bold=True)

    # Reactor bar
    bx, by, bw, bh = 430, SCREEN_H - 25, 200, 18
    ratio     = player.reactor_energy / player.max_reactor
    bar_color = GREEN if ratio > 0.5 else (ORANGE if ratio > 0.25 else RED)
    fill_rect(bx + bw / 2, by, bw, bh, (40, 40, 40))
    if ratio > 0:
        fill_rect(bx + (bw * ratio) / 2, by, bw * ratio, bh, bar_color)
    outline_rect(bx + bw / 2, by, bw, bh, WHITE, 1)
    dtext(f"Reactor  {player.reactor_energy}/{player.max_reactor}",
          bx + bw / 2, by, WHITE, size=11, anchor_x="center", anchor_y="center")

    dtext(f"Cargo  {player.cargo_used}/{player.ship.cargo_capacity}",
          690, SCREEN_H - 32, CYAN, size=14, anchor_y="center", bold=True)

    parts = []
    if player.current_galaxy:  parts.append(player.current_galaxy.name)
    if player.current_system:  parts.append(player.current_system.name)
    if player.current_planet:  parts.append(player.current_planet.name)
    dtext("  >  ".join(parts), SCREEN_W - 15, SCREEN_H - 32,
          GRAY, size=11, anchor_x="right", anchor_y="center")

# ── RANDOM EVENTS ──────────────────────────────────────────────────────────────
EVENTS = [
    ("Solar radiation burst!",          "reactor",   -15),
    ("Pirate ambush — cargo lost!",     "minerals",   -3),
    ("Abandoned station — found rods!", "fuel_rods",   3),
    ("Friendly trader gift!",           "credits",    50),
    ("Meteor shower!",                  "reactor",   -10),
    ("Reactor surge — gained energy!",  "reactor",    15),
]

# ── VIEWS ──────────────────────────────────────────────────────────────────────

class MainMenuView(arcade.View):
    def __init__(self, player, galaxies):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.stars    = make_stars(200)
        self.start    = Button(SCREEN_W // 2, 340, 270, 58,
                               "BEGIN JOURNEY", (30, 90, 170), (55, 130, 210))

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, DARK_BG)
        draw_stars(self.stars)

        for r in range(90, 0, -12):
            fill_circle(SCREEN_W // 2, 510, r, (r // 3, r // 6, 0))
        fill_circle(SCREEN_W // 2, 510, 32, ORANGE)
        outline_circle(SCREEN_W // 2, 510, 38, YELLOW, 2)

        dtext("STELLAR VAGABOND", SCREEN_W // 2, 610,
              YELLOW, size=50, anchor_x="center", bold=True)
        dtext("Nuclear Age Space Trader", SCREEN_W // 2, 563,
              CYAN, size=22, anchor_x="center")
        dtext("You are an autonomous robot captain powered by a nuclear core.",
              SCREEN_W // 2, 455, WHITE, size=14, anchor_x="center")
        dtext("Travel between galaxies. Trade resources. Keep your reactor alive.",
              SCREEN_W // 2, 428, GRAY, size=13, anchor_x="center")

        self.start.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.start.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.start.clicked(x, y):
            self.window.show_view(GalaxyMapView(self.player, self.galaxies))


# ───────────────────────────────────────────────────────────────────────────────

class GalaxyMapView(arcade.View):
    def __init__(self, player, galaxies):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.stars    = make_stars(280)
        self.msg      = ""
        self.msg_t    = 0.0

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, DARK_BG)
        draw_stars(self.stars)

        dtext("GALAXY MAP", SCREEN_W // 2, SCREEN_H - 70,
              CYAN, size=24, anchor_x="center", bold=True)
        dtext("Click a galaxy to travel there  |  Galaxy jump: 15 rods + 20 reactor",
              SCREEN_W // 2, SCREEN_H - 96, GRAY, size=11, anchor_x="center")

        for i in range(len(self.galaxies)):
            for j in range(i + 1, len(self.galaxies)):
                g1, g2 = self.galaxies[i], self.galaxies[j]
                dline(g1.x, g1.y, g2.x, g2.y, (30, 40, 70), 1)

        for g in self.galaxies:
            here = g is self.player.current_galaxy
            r = 55
            for rr in range(r + 22, r - 1, -6):
                fill_circle(g.x, g.y, rr, (*g.color, 18))
            fill_circle(g.x, g.y, r, WHITE if here else g.color)
            outline_circle(g.x, g.y, r, WHITE if here else g.color, 3)
            dtext(g.name, g.x, g.y - r - 20, WHITE, size=13, anchor_x="center", bold=True)
            dtext(f"{len(g.systems)} systems", g.x, g.y - r - 36, GRAY, size=10, anchor_x="center")
            if here:
                dtext("< HERE", g.x, g.y + r + 10, YELLOW, size=11, anchor_x="center", bold=True)

        if self.msg:
            dtext(self.msg, SCREEN_W // 2, 110, RED, size=14, anchor_x="center", bold=True)

        draw_hud(self.player)

    def on_update(self, dt):
        if self.msg_t > 0:
            self.msg_t -= dt
            if self.msg_t <= 0:
                self.msg = ""

    def on_mouse_press(self, x, y, button, modifiers):
        for g in self.galaxies:
            if math.dist((x, y), (g.x, g.y)) <= 55:
                if g is self.player.current_galaxy:
                    self.window.show_view(SolarSystemView(self.player, self.galaxies, g))
                else:
                    ok, err = self.player.travel("galaxy")
                    if ok:
                        self.player.current_galaxy = g
                        self.player.current_system = None
                        self.player.current_planet = None
                        if self.player.is_dead():
                            self.window.show_view(GameOverView(self.player, self.galaxies))
                            return
                        self.window.show_view(SolarSystemView(self.player, self.galaxies, g))
                    else:
                        self.msg, self.msg_t = err, 3.0
                return


# ───────────────────────────────────────────────────────────────────────────────

class SolarSystemView(arcade.View):
    def __init__(self, player, galaxies, galaxy):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.galaxy   = galaxy
        self.stars    = make_stars(280)
        self.msg      = ""
        self.msg_t    = 0.0

        n       = len(galaxy.systems)
        spacing = 700 // max(n, 1)
        self.star_btns = []
        for i, sys_ in enumerate(galaxy.systems):
            bx = 250 + i * spacing
            self.star_btns.append(
                (Button(bx, 360, 170, 48, sys_.name, (50, 25, 110), (90, 55, 170)), sys_))

        self.back = Button(80, 55, 130, 40, "< Galaxy Map", (35, 35, 75), (65, 65, 120))

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, DARK_BG)
        draw_stars(self.stars)

        dtext(f"{self.galaxy.name}  -  Solar Systems",
              SCREEN_W // 2, SCREEN_H - 70, YELLOW, size=22, anchor_x="center", bold=True)
        dtext("Click a star to travel there  |  Star jump: 8 rods + 10 reactor",
              SCREEN_W // 2, SCREEN_H - 96, GRAY, size=11, anchor_x="center")

        for btn, sys_ in self.star_btns:
            here = sys_ is self.player.current_system
            sc   = sys_.star_color
            for rr in range(55, 20, -10):
                fill_circle(btn.x, btn.y + 90, rr, sc)
            fill_circle(btn.x, btn.y + 90, 24, sc)
            if here:
                outline_circle(btn.x, btn.y + 90, 30, WHITE, 2)
                dtext("HERE", btn.x, btn.y + 128, YELLOW, size=10, anchor_x="center", bold=True)
            btn.draw()
            dtext(f"{len(sys_.planets)} planets",
                  btn.x, btn.y - 35, GRAY, size=10, anchor_x="center")

        if self.msg:
            dtext(self.msg, SCREEN_W // 2, 110, RED, size=14, anchor_x="center", bold=True)

        self.back.draw()
        draw_hud(self.player)

    def on_update(self, dt):
        if self.msg_t > 0:
            self.msg_t -= dt
            if self.msg_t <= 0:
                self.msg = ""

    def on_mouse_motion(self, x, y, dx, dy):
        self.back.update_hover(x, y)
        for btn, _ in self.star_btns:
            btn.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.back.clicked(x, y):
            self.window.show_view(GalaxyMapView(self.player, self.galaxies))
            return
        for btn, sys_ in self.star_btns:
            if btn.clicked(x, y):
                if sys_ is self.player.current_system:
                    self.window.show_view(
                        PlanetSelectView(self.player, self.galaxies, self.galaxy, sys_))
                else:
                    ok, err = self.player.travel("star")
                    if ok:
                        self.player.current_system = sys_
                        self.player.current_planet = None
                        if self.player.is_dead():
                            self.window.show_view(GameOverView(self.player, self.galaxies))
                            return
                        self.window.show_view(
                            PlanetSelectView(self.player, self.galaxies, self.galaxy, sys_))
                    else:
                        self.msg, self.msg_t = err, 3.0
                return


# ───────────────────────────────────────────────────────────────────────────────

class PlanetSelectView(arcade.View):
    PLANET_COLORS = [(100, 180, 100), (200, 120, 50), (80, 150, 220),
                     (180, 80, 180), (220, 200, 80)]
    CX, CY = SCREEN_W // 2, 380

    def __init__(self, player, galaxies, galaxy, system):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.galaxy   = galaxy
        self.system   = system
        self.stars    = make_stars(280)
        self.angle    = 0.0
        self.msg      = ""
        self.msg_t    = 0.0
        self.orbits   = [120 + i * 85 for i in range(len(system.planets))]
        self.back     = Button(80, 55, 130, 40, "< Systems", (35, 35, 75), (65, 65, 120))

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, DARK_BG)
        draw_stars(self.stars)

        dtext(f"{self.system.name}  -  Choose a planet to land",
              SCREEN_W // 2, SCREEN_H - 70, YELLOW, size=20, anchor_x="center", bold=True)
        dtext("Planet landing: 3 rods + 5 reactor",
              SCREEN_W // 2, SCREEN_H - 94, GRAY, size=11, anchor_x="center")

        for r in self.orbits:
            outline_circle(self.CX, self.CY, r, (40, 40, 80), 1)

        sc = self.system.star_color
        for rr in range(65, 18, -10):
            fill_circle(self.CX, self.CY, rr, sc)

        n = len(self.system.planets)
        for i, planet in enumerate(self.system.planets):
            ang  = self.angle + i * (360 / n)
            px   = self.CX + self.orbits[i] * math.cos(math.radians(ang))
            py   = self.CY + self.orbits[i] * math.sin(math.radians(ang))
            col  = self.PLANET_COLORS[i % len(self.PLANET_COLORS)]
            here = planet is self.player.current_planet

            fill_circle(px, py, 14, col)
            if here:
                outline_circle(px, py, 19, WHITE, 2)
            dtext(planet.name, px, py - 26, WHITE, size=10, anchor_x="center")
            dtext("!" * planet.danger, px, py + 19, RED, size=9, anchor_x="center")

        if self.msg:
            dtext(self.msg, SCREEN_W // 2, 110, RED, size=14, anchor_x="center", bold=True)

        self.back.draw()
        draw_hud(self.player)

    def on_update(self, dt):
        self.angle = (self.angle + dt * 14) % 360
        if self.msg_t > 0:
            self.msg_t -= dt
            if self.msg_t <= 0:
                self.msg = ""

    def on_mouse_motion(self, x, y, dx, dy):
        self.back.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.back.clicked(x, y):
            self.window.show_view(
                SolarSystemView(self.player, self.galaxies, self.galaxy))
            return
        n = len(self.system.planets)
        for i, planet in enumerate(self.system.planets):
            ang = self.angle + i * (360 / n)
            px  = self.CX + self.orbits[i] * math.cos(math.radians(ang))
            py  = self.CY + self.orbits[i] * math.sin(math.radians(ang))
            if math.dist((x, y), (px, py)) <= 20:
                ok, err = self.player.travel("planet")
                if ok:
                    self.player.current_planet = planet
                    if self.player.is_dead():
                        self.window.show_view(GameOverView(self.player, self.galaxies))
                        return
                    self.window.show_view(
                        PlanetView(self.player, self.galaxies,
                                   self.galaxy, self.system, planet))
                else:
                    self.msg, self.msg_t = err, 3.0
                return


# ───────────────────────────────────────────────────────────────────────────────

class PlanetView(arcade.View):

    def __init__(self, player, galaxies, galaxy, system, planet):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.galaxy   = galaxy
        self.system   = system
        self.planet   = planet
        self.msg      = ""
        self.msg_col  = GREEN
        self.msg_t    = 0.0

        self.event_msg = self._roll_event()

        bw, bh = 185, 44
        self.b_fuel   = Button(200, 460, bw, bh, "BUY Fuel Rod",      (25, 75, 155), (50, 110, 200))
        self.b_min    = Button(200, 405, bw, bh, "BUY Minerals",      (25, 75, 155), (50, 110, 200))
        self.b_tech   = Button(200, 350, bw, bh, "BUY Tech",          (25, 75, 155), (50, 110, 200))
        self.s_min    = Button(430, 405, bw, bh, "SELL Minerals",     (60, 130, 35), (90, 170, 55))
        self.s_tech   = Button(430, 350, bw, bh, "SELL Tech",         (60, 130, 35), (90, 170, 55))
        self.recharge = Button(680, 420, bw, bh, "Recharge (5 rods)", (130, 55, 15), (170, 85, 25))
        self.back     = Button(80,   55, 130, 40, "< Planets",        (35,  35, 75), (65,  65, 120))

        self.all_btns = [self.b_fuel, self.b_min, self.b_tech,
                         self.s_min,  self.s_tech, self.recharge, self.back]

    def _roll_event(self):
        if random.random() < 0.35:
            ev              = random.choice(EVENTS)
            label, key, val = ev
            if key == "reactor":
                self.player.reactor_energy = max(0, min(
                    self.player.max_reactor, self.player.reactor_energy + val))
            elif key == "minerals":
                self.player.cargo["minerals"] = max(0, self.player.cargo["minerals"] + val)
            elif key == "fuel_rods":
                self.player.fuel_rods = max(0, self.player.fuel_rods + val)
            elif key == "credits":
                self.player.credits += val
            sign = "+" if val > 0 else ""
            return f"{label}  ({sign}{val} {key.replace('_', ' ')})"
        return ""

    def _msg(self, text, color=GREEN):
        self.msg, self.msg_col, self.msg_t = text, color, 3.0

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, DARK_BG)
        fill_rect(SCREEN_W / 2, SCREEN_H / 2 - 25, SCREEN_W - 50, SCREEN_H - 120, PANEL_BG)
        outline_rect(SCREEN_W / 2, SCREEN_H / 2 - 25, SCREEN_W - 50, SCREEN_H - 120, CYAN, 2)

        dtext(self.planet.name, SCREEN_W // 2, SCREEN_H - 78,
              YELLOW, size=28, anchor_x="center", bold=True)
        dtext("Danger  " + ("! " * self.planet.danger).strip(),
              SCREEN_W // 2, SCREEN_H - 108, RED, size=13, anchor_x="center")
        if self.event_msg:
            dtext(f"EVENT: {self.event_msg}", SCREEN_W // 2, SCREEN_H - 130,
                  ORANGE, size=12, anchor_x="center", bold=True)

        # Market
        dtext("MARKET", 200, 508, CYAN, size=15, anchor_x="center", bold=True)
        p, st = self.planet.prices, self.planet.stock
        for row, ty in [
            (f"Fuel Rod  {p['fuel_rods']:>4} CR   stock {st['fuel_rods']}", 490),
            (f"Minerals  {p['minerals']:>4} CR   stock {st['minerals']}",   472),
            (f"Tech      {p['tech']:>4} CR   stock {st['tech']}",           454),
        ]:
            dtext(row, 200, ty, WHITE, size=11, anchor_x="center")

        # Cargo
        dtext("YOUR CARGO", 430, 508, CYAN, size=15, anchor_x="center", bold=True)
        dtext(f"Minerals  {self.player.cargo['minerals']}",
              430, 483, WHITE, size=12, anchor_x="center")
        dtext(f"Tech      {self.player.cargo['tech']}",
              430, 460, WHITE, size=12, anchor_x="center")
        dtext(f"Used  {self.player.cargo_used}/{self.player.ship.cargo_capacity}",
              430, 438, GRAY, size=11, anchor_x="center")

        # Reactor
        dtext("REACTOR", 680, 508, CYAN, size=15, anchor_x="center", bold=True)
        dtext("5 rods  ->  +20 energy", 680, 483, WHITE, size=11, anchor_x="center")

        for btn in self.all_btns:
            btn.draw()

        if self.msg:
            dtext(self.msg, SCREEN_W // 2, 120,
                  self.msg_col, size=14, anchor_x="center", bold=True)

        draw_hud(self.player)

    def on_update(self, dt):
        if self.msg_t > 0:
            self.msg_t -= dt
            if self.msg_t <= 0:
                self.msg = ""

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.all_btns:
            btn.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.back.clicked(x, y):
            self.window.show_view(
                PlanetSelectView(self.player, self.galaxies, self.galaxy, self.system))
            return

        p = self.planet

        if self.b_fuel.clicked(x, y):
            cost = p.prices["fuel_rods"]
            if self.player.credits >= cost and p.stock["fuel_rods"] > 0:
                self.player.credits   -= cost
                self.player.fuel_rods += 1
                p.stock["fuel_rods"]  -= 1
                self._msg(f"Bought 1 fuel rod  -{cost} CR")
            else:
                self._msg("Not enough credits or out of stock!", RED)

        elif self.b_min.clicked(x, y):
            cost = p.prices["minerals"]
            if (self.player.credits >= cost and p.stock["minerals"] > 0
                    and self.player.cargo_used < self.player.ship.cargo_capacity):
                self.player.credits          -= cost
                self.player.cargo["minerals"] += 1
                p.stock["minerals"]           -= 1
                self._msg(f"Bought 1 mineral  -{cost} CR")
            else:
                self._msg("Can't buy — check credits / cargo / stock!", RED)

        elif self.b_tech.clicked(x, y):
            cost = p.prices["tech"]
            if (self.player.credits >= cost and p.stock["tech"] > 0
                    and self.player.cargo_used < self.player.ship.cargo_capacity):
                self.player.credits      -= cost
                self.player.cargo["tech"] += 1
                p.stock["tech"]           -= 1
                self._msg(f"Bought 1 tech  -{cost} CR")
            else:
                self._msg("Can't buy — check credits / cargo / stock!", RED)

        elif self.s_min.clicked(x, y):
            if self.player.cargo["minerals"] > 0:
                sell = int(p.prices["minerals"] * 1.3)
                self.player.credits          += sell
                self.player.cargo["minerals"] -= 1
                self._msg(f"Sold 1 mineral  +{sell} CR")
            else:
                self._msg("No minerals to sell!", RED)

        elif self.s_tech.clicked(x, y):
            if self.player.cargo["tech"] > 0:
                sell = int(p.prices["tech"] * 1.3)
                self.player.credits      += sell
                self.player.cargo["tech"] -= 1
                self._msg(f"Sold 1 tech  +{sell} CR")
            else:
                self._msg("No tech to sell!", RED)

        elif self.recharge.clicked(x, y):
            if self.player.recharge(5):
                self._msg("Reactor recharged  +20 energy")
            else:
                self._msg("Need at least 5 fuel rods to recharge!", RED)

        if self.player.is_dead():
            self.window.show_view(GameOverView(self.player, self.galaxies))


# ───────────────────────────────────────────────────────────────────────────────

class GameOverView(arcade.View):
    def __init__(self, player, galaxies):
        super().__init__()
        self.player   = player
        self.galaxies = galaxies
        self.stars    = make_stars(200)
        self.restart  = Button(SCREEN_W // 2, 260, 240, 55,
                               "RESTART", (100, 25, 25), (155, 45, 45))

    def on_draw(self):
        self.clear()
        fill_rect(SCREEN_W / 2, SCREEN_H / 2, SCREEN_W, SCREEN_H, (4, 0, 8))
        draw_stars(self.stars)
        dtext("REACTOR DEAD", SCREEN_W // 2, 530,
              RED, size=54, anchor_x="center", bold=True)
        dtext("Your nuclear core has gone silent. The robot shuts down forever.",
              SCREEN_W // 2, 472, GRAY, size=16, anchor_x="center")
        dtext(f"Final Credits:  {self.player.credits} CR",
              SCREEN_W // 2, 415, YELLOW, size=22, anchor_x="center", bold=True)
        self.restart.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        self.restart.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.restart.clicked(x, y):
            new_galaxies = [Galaxy(d) for d in UNIVERSE_DATA]
            new_player   = Player()
            new_player.current_galaxy = new_galaxies[0]
            self.window.show_view(GalaxyMapView(new_player, new_galaxies))


# ── ENTRY POINT ────────────────────────────────────────────────────────────────

def main():
    window   = arcade.Window(SCREEN_W, SCREEN_H, TITLE)
    galaxies = [Galaxy(d) for d in UNIVERSE_DATA]
    player   = Player()
    player.current_galaxy = galaxies[0]
    window.show_view(MainMenuView(player, galaxies))
    arcade.run()

if __name__ == "__main__":
    main()