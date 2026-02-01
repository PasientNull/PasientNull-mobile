from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import webbrowser
import requests
import threading
import socket
from plyer import battery

# --- MODERN THEME PALETTE ---
C_BG      = get_color_from_hex("#121212")  # Material Dark Background
C_SURFACE = get_color_from_hex("#1E1E1E")  # Card Background
C_ACCENT  = get_color_from_hex("#2979FF")  # Electric Blue (Primary)
C_TEXT    = get_color_from_hex("#FFFFFF")  # Primary Text
C_SUBTEXT = get_color_from_hex("#B0B0B0")  # Secondary Text
C_DANGER  = get_color_from_hex("#CF6679")  # Error/Danger

Window.clearcolor = C_BG

# --- CUSTOM MODERN WIDGETS ---

class ModernButton(Button):
    """A sleek, solid rounded button"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0)
        self.background_normal = ''
        self.color = C_TEXT
        self.bold = True
        self.font_size = "16sp"
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.btn_color = C_ACCENT 

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.btn_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

class ModernInput(TextInput):
    """A minimal input field with no ugly borders"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = C_SURFACE
        self.foreground_color = C_TEXT
        self.cursor_color = C_ACCENT
        self.padding = [15, 15, 15, 15]
        self.font_size = "16sp"
        self.hint_text_color = C_SUBTEXT
        self.multiline = False

class ToolCard(Button):
    """A Dashboard Card acting as a button"""
    def __init__(self, title, desc, icon_text, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0)
        self.title = title
        self.desc = desc
        self.icon_text = icon_text
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        self.canvas.after.clear()
        
        # Card Background
        with self.canvas.before:
            Color(*C_SURFACE)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        
        # Text Rendering manually because Button text layout is limited
        with self.canvas.after:
            # Icon (simulated with text)
            # You would normally use an Image widget here, but we are keeping it single-file
            pass

class LogLabel(Label):
    def on_ref_press(self, instance):
        webbrowser.open(instance)

# --- BASE SCREEN CLASS (Handles common layout) ---
class BaseScreen(Screen):
    def add_header(self, title, subtitle):
        header = BoxLayout(orientation='vertical', size_hint=(1, None), height=80, padding=[0, 10, 0, 10])
        header.add_widget(Label(text=title, font_size="24sp", bold=True, color=C_TEXT, halign="left", size_hint=(1, 0.6)))
        header.add_widget(Label(text=subtitle, font_size="14sp", color=C_SUBTEXT, halign="left", size_hint=(1, 0.4)))
        return header

    def add_back_btn(self):
        btn = Button(text="← Back", size_hint=(None, None), size=(100, 40), background_color=(0,0,0,0), color=C_ACCENT)
        btn.bind(on_press=self.go_back)
        return btn
    
    def go_back(self, *args):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'dash'

# --- SCREEN 1: DASHBOARD ---
class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main Container
        root = BoxLayout(orientation='vertical', padding=25, spacing=20)

        # 1. Header Area
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        header.add_widget(Label(text="PasientNull", font_size="28sp", bold=True, color=C_TEXT, size_hint=(1, 0.6), halign="left", text_size=(Window.width-50, None)))
        header.add_widget(Label(text="Command Center", font_size="16sp", color=C_SUBTEXT, size_hint=(1, 0.4), halign="left", text_size=(Window.width-50, None)))
        root.add_widget(header)

        # 2. Status Card (Mini Dashboard)
        status_card = BoxLayout(orientation='vertical', size_hint=(1, 0.15), padding=15)
        self.lbl_ip = Label(text="IP: ...", color=C_ACCENT, font_size="14sp", bold=True)
        self.lbl_bat = Label(text="Battery: ...", color=C_SUBTEXT, font_size="14sp")
        status_card.canvas.before.add(Color(*C_SURFACE))
        status_card.canvas.before.add(RoundedRectangle(pos=status_card.pos, size=status_card.size, radius=[15]))
        status_card.bind(pos=self.update_rect, size=self.update_rect)
        
        status_card.add_widget(self.lbl_ip)
        status_card.add_widget(self.lbl_bat)
        root.add_widget(status_card)

        # 3. Tools Grid
        scroll = ScrollView(size_hint=(1, 0.65), do_scroll_x=False)
        grid = GridLayout(cols=2, spacing=15, size_hint_y=None, padding=[0, 10, 0, 0])
        grid.bind(minimum_height=grid.setter('height'))

        # Helper to make cards
        def make_card(title, func):
            btn = ModernButton(text=title)
            btn.background_color = (0,0,0,0)
            btn.btn_color = C_SURFACE # Card color
            btn.color = C_TEXT
            btn.size_hint_y = None
            btn.height = 120
            btn.bind(on_press=func)
            return btn

        grid.add_widget(make_card("User\nHunt", lambda x: self.nav('user')))
        grid.add_widget(make_card("Net\nProbe", lambda x: self.nav('net')))
        grid.add_widget(make_card("Tech\nStack", lambda x: self.nav('tech')))
        grid.add_widget(make_card("Domain\nRecon", lambda x: self.nav('sub')))

        scroll.add_widget(grid)
        root.add_widget(scroll)
        self.add_widget(root)

        # Start Background Tasks
        Clock.schedule_interval(self.update_stats, 5)

    def update_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*C_SURFACE)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[15])

    def nav(self, name):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = name

    def update_stats(self, dt):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            self.lbl_ip.text = f"Local IP: {s.getsockname()[0]}"
            s.close()
        except: self.lbl_ip.text = "Local IP: Disconnected"

        try:
            self.lbl_bat.text = f"Battery: {battery.status.get('percentage', '?')}%"
        except: pass

# --- SCREEN 2: GENERIC TOOL SCREEN (Used for all tools) ---
class ToolScreen(BaseScreen):
    def __init__(self, name, title, placeholder, btn_text, logic_func, **kwargs):
        super().__init__(**kwargs)
        self.logic_func = logic_func
        
        root = BoxLayout(orientation='vertical', padding=25, spacing=20)
        
        # Header
        root.add_widget(self.add_back_btn())
        root.add_widget(Label(text=title, font_size="26sp", bold=True, color=C_TEXT, size_hint=(1, 0.1), halign="left", text_size=(Window.width-50, None)))

        # Input
        self.inp = ModernInput(hint_text=placeholder, size_hint=(1, None), height=60)
        root.add_widget(self.inp)

        # Action Button
        btn = ModernButton(text=btn_text, size_hint=(1, None), height=60)
        btn.bind(on_press=self.start_task)
        root.add_widget(btn)

        # Output Log (Card style)
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.out = LogLabel(text="Ready...", size_hint_y=None, markup=True, padding=[15,15])
        self.out.bind(texture_size=self.out.setter('size'))
        
        # Background for log
        with self.out.canvas.before:
            Color(*C_SURFACE)
            self.rect = RoundedRectangle(pos=self.out.pos, size=self.out.size, radius=[12])
        self.out.bind(pos=self.update_rect, size=self.update_rect)

        self.scroll.add_widget(self.out)
        root.add_widget(self.scroll)
        self.add_widget(root)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def log(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.out, 'text', self.out.text + msg + "\n"))

    def start_task(self, instance):
        target = self.inp.text
        self.out.text = "" # Clear
        threading.Thread(target=self.logic_func, args=(target, self.log), daemon=True).start()


# --- LOGIC FUNCTIONS (Separated for cleanliness) ---

def logic_user_hunt(target, log):
    log(f"[b]Scanning:[/b] {target}")
    if not target: return
    sites = {"GitHub": "https://github.com/{}", "Twitter": "https://twitter.com/{}", "Instagram": "https://instagram.com/{}", "Reddit": "https://reddit.com/user/{}"}
    for s, u in sites.items():
        try:
            if requests.get(u.format(target), headers={'User-Agent':'Moz'}, timeout=4).status_code == 200:
                log(f"[color=2979FF]Found: {s}[/color]")
                log(f"[ref={u.format(target)}]>> Open Profile[/ref]")
        except: pass
    log("Scan Complete.")

def logic_tech_stack(target, log):
    if not target.startswith("http"): target = "http://" + target
    log(f"Analyzing {target}...")
    try:
        r = requests.get(target, timeout=5, verify=False)
        if 'Server' in r.headers: log(f"Server: {r.headers['Server']}")
        if 'X-Powered-By' in r.headers: log(f"Powered By: {r.headers['X-Powered-By']}")
        
        # CMS Checks
        txt = r.text.lower()
        if 'wp-content' in txt: log("[color=2979FF]Detected: WordPress[/color]")
        elif 'shopify' in txt: log("[color=2979FF]Detected: Shopify[/color]")
        
        # Sensitive Files
        log("\nChecking Paths...")
        for f in ['robots.txt', 'sitemap.xml', 'admin']:
            if requests.head(f"{target}/{f}", timeout=3).status_code == 200:
                log(f"[color=00FF00]Found: /{f}[/color]")
    except Exception as e: log(f"[color=CF6679]Error: {e}[/color]")

def logic_subdomain(target, log):
    log(f"Querying Certificate Logs for {target}...")
    try:
        url = f"https://crt.sh/?q=%25.{target}&output=json"
        data = requests.get(url, timeout=10).json()
        subs = set([entry['name_value'] for entry in data])
        log(f"Found {len(subs)} subdomains:\n")
        for s in subs: log(f"> {s}")
    except: log("[color=CF6679]Query Failed[/color]")

def logic_netprobe(target, log):
    # My IP Check
    if not target:
        log("Fetching External IP...")
        try:
            d = requests.get("http://ip-api.com/json/", timeout=5).json()
            log(f"Public IP: {d['query']}")
            log(f"ISP: {d['isp']}")
            log(f"Location: {d['city']}, {d['country']}")
            return
        except: return log("Connection Failed")
    
    # Port Scan
    log(f"Scanning Ports: {target}")
    try:
        ip = socket.gethostbyname(target)
        log(f"IP: {ip}")
        for p in [21, 22, 80, 443, 3389, 8080]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0: log(f"[color=00FF00]Open: {p}[/color]")
            s.close()
    except: log("Resolution Failed")

# --- APP BUILDER ---
class PasientNullMobile(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='dash'))
        
        # We reuse the Generic Tool Screen to save code space
        sm.add_widget(ToolScreen(name='user', title="Identity Hunter", placeholder="Username", btn_text="Start Scan", logic_func=logic_user_hunt))
        sm.add_widget(ToolScreen(name='tech', title="Tech Stack", placeholder="domain.com", btn_text="Analyze", logic_func=logic_tech_stack))
        sm.add_widget(ToolScreen(name='sub', title="Domain Recon", placeholder="domain.com", btn_text="Find Subdomains", logic_func=logic_subdomain))
        sm.add_widget(ToolScreen(name='net', title="Net Probe", placeholder="IP/Domain (Empty for My IP)", btn_text="Diagnose", logic_func=logic_netprobe))
        
        return sm

if __name__ == '__main__':
    PasientNullMobile().run()
