from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
import webbrowser
import requests
import threading
import json

# --- THEME CONFIG ---
Window.clearcolor = (0.05, 0.05, 0.05, 1) # Void Black
C_NEON = get_color_from_hex("#00FF41")    # Hacker Green
C_CYAN = get_color_from_hex("#00E5FF")    # Cyber Blue
C_WARN = get_color_from_hex("#FFD700")    # Gold
C_ERR  = get_color_from_hex("#FF3333")    # Red

# --- CUSTOM WIDGETS (For the Modern Look) ---
class NeonButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0) # Transparent
        self.color = C_NEON
        self.font_name = "Roboto"
        self.font_size = "18sp"
        self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.color)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 10), width=1.5)

class TerminalLabel(Label):
    def on_ref_press(self, instance):
        # This handles the clickable links
        webbrowser.open(instance)

# --- SCREEN 1: HOME MENU ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Header
        layout.add_widget(Label(text="[b]PASIENTNULL[/b]\nMOBILE COMMAND", markup=True, 
                                font_size='24sp', color=C_NEON, size_hint=(1, 0.3)))
        
        # Buttons
        btn_user = NeonButton(text="IDENTITY HUNTER")
        btn_user.bind(on_press=self.go_user)
        layout.add_widget(btn_user)

        btn_spy = NeonButton(text="SERVER SPY (HTTP)")
        btn_spy.color = C_CYAN
        btn_spy.bind(on_press=self.go_spy)
        layout.add_widget(btn_spy)

        btn_ip = NeonButton(text="IP GEOLOCATOR")
        btn_ip.color = C_WARN
        btn_ip.bind(on_press=self.go_ip)
        layout.add_widget(btn_ip)

        layout.add_widget(Label(size_hint=(1, 0.2))) # Spacer
        self.add_widget(layout)

    def go_user(self, *args): self.manager.transition = SlideTransition(direction="left"); self.manager.current = 'user'
    def go_spy(self, *args): self.manager.transition = SlideTransition(direction="left"); self.manager.current = 'spy'
    def go_ip(self, *args): self.manager.transition = SlideTransition(direction="left"); self.manager.current = 'ip'

# --- SCREEN 2: USER HUNTER ---
class UserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        vbox = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Top Bar
        hbox = BoxLayout(size_hint=(1, 0.1))
        btn_back = Button(text="<", size_hint=(0.2, 1), background_color=(0.2,0.2,0.2,1))
        btn_back.bind(on_press=self.go_back)
        self.inp = TextInput(hint_text="Username", size_hint=(0.8, 1), multiline=False, 
                             background_color=(0.1,0.1,0.1,1), foreground_color=(1,1,1,1))
        hbox.add_widget(btn_back)
        hbox.add_widget(self.inp)
        vbox.add_widget(hbox)

        # Action Button
        btn_scan = NeonButton(text="INITIATE SCAN", size_hint=(1, 0.1))
        btn_scan.bind(on_press=self.start_scan)
        vbox.add_widget(btn_scan)

        # Output
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.out = TerminalLabel(text="Waiting for target...", size_hint_y=None, markup=True, padding=(10,10))
        self.out.bind(texture_size=self.out.setter('size'))
        self.scroll.add_widget(self.out)
        vbox.add_widget(self.scroll)
        self.add_widget(vbox)

    def go_back(self, *args): self.manager.transition = SlideTransition(direction="right"); self.manager.current = 'menu'

    def log(self, msg):
        # Kivy requires UI updates on main thread
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: setattr(self.out, 'text', self.out.text + msg + "\n"))

    def start_scan(self, instance):
        target = self.inp.text
        if not target: return
        self.out.text = ""
        self.log(f"[color=#00ff00]SCANNING: {target}[/color]\n")
        threading.Thread(target=self.run_logic, args=(target,), daemon=True).start()

    def run_logic(self, target):
        # EXPANDED DATABASE (Add as many as you want here)
        sites = {
            "Instagram": "https://www.instagram.com/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "Twitter": "https://twitter.com/{}",
            "GitHub": "https://github.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "Twitch": "https://www.twitch.tv/{}",
            "Pinterest": "https://www.pinterest.com/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "DeviantArt": "https://www.deviantart.com/{}",
            "Steam": "https://steamcommunity.com/id/{}",
            "Wikipedia": "https://en.wikipedia.org/wiki/User:{}",
            "Pastebin": "https://pastebin.com/u/{}",
            "Patreon": "https://www.patreon.com/{}",
            "Medium": "https://medium.com/@{}",
            "Vimeo": "https://vimeo.com/{}"
        }
        
        headers = {'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:68.0)'}
        found_count = 0

        for site, url_temp in sites.items():
            url = url_temp.format(target)
            try:
                r = requests.get(url, headers=headers, timeout=4)
                if r.status_code == 200:
                    found_count += 1
                    # CLICKABLE LINK MARKUP
                    self.log(f"[color=#00ff41][b]FOUND: {site}[/b][/color]")
                    self.log(f"[ref={url}][color=#00E5FF]>> OPEN LINK[/color][/ref]")
                elif r.status_code == 404:
                    self.log(f"[color=#555555]Missing: {site}[/color]")
            except:
                self.log(f"[color=#FF3333]Error: {site}[/color]")
        
        self.log(f"\n[b]SCAN COMPLETE. FOUND {found_count} PROFILES.[/b]")

# --- SCREEN 3: SERVER SPY ---
class SpyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        vbox = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        hbox = BoxLayout(size_hint=(1, 0.1))
        btn_back = Button(text="<", size_hint=(0.2, 1), background_color=(0.2,0.2,0.2,1))
        btn_back.bind(on_press=self.go_back)
        self.inp = TextInput(hint_text="Domain (google.com)", size_hint=(0.8, 1), multiline=False, background_color=(0.1,0.1,0.1,1), foreground_color=(1,1,1,1))
        hbox.add_widget(btn_back)
        hbox.add_widget(self.inp)
        vbox.add_widget(hbox)

        btn_scan = NeonButton(text="ANALYZE SERVER", size_hint=(1, 0.1))
        btn_scan.color = C_CYAN
        btn_scan.bind(on_press=self.start_scan)
        vbox.add_widget(btn_scan)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.out = TerminalLabel(text="Ready to intercept...", size_hint_y=None, markup=True, padding=(10,10))
        self.out.bind(texture_size=self.out.setter('size'))
        self.scroll.add_widget(self.out)
        vbox.add_widget(self.scroll)
        self.add_widget(vbox)

    def go_back(self, *args): self.manager.transition = SlideTransition(direction="right"); self.manager.current = 'menu'
    
    def start_scan(self, instance):
        target = self.inp.text
        if not target: return
        if not target.startswith("http"): target = "http://" + target
        self.out.text = ""
        threading.Thread(target=self.run_logic, args=(target,), daemon=True).start()

    def run_logic(self, target):
        from kivy.clock import Clock
        def log(msg): Clock.schedule_once(lambda dt: setattr(self.out, 'text', self.out.text + msg + "\n"))
        
        log(f"[color=#00E5FF]CONNECTING TO: {target}[/color]")
        try:
            r = requests.head(target, timeout=5)
            log(f"STATUS: {r.status_code}")
            
            # Interesting Headers
            keys = ['Server', 'X-Powered-By', 'Strict-Transport-Security', 'Content-Security-Policy']
            for k in r.headers:
                val = r.headers[k]
                if k in keys:
                     log(f"[color=#00ff41]{k}:[/color] {val}")
                else:
                     log(f"[color=#888]{k}: {val}[/color]")
            
            if 'Server' not in r.headers:
                log("\n[!] Server header is hidden (Good OpSec).")
                
        except Exception as e:
            log(f"[color=#FF3333]CONNECTION FAILED:\n{str(e)}[/color]")

# --- SCREEN 4: IP GEOLOCATOR ---
class IPScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        vbox = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        hbox = BoxLayout(size_hint=(1, 0.1))
        btn_back = Button(text="<", size_hint=(0.2, 1), background_color=(0.2,0.2,0.2,1))
        btn_back.bind(on_press=self.go_back)
        self.inp = TextInput(hint_text="IP (Leave empty for my IP)", size_hint=(0.8, 1), multiline=False, background_color=(0.1,0.1,0.1,1), foreground_color=(1,1,1,1))
        hbox.add_widget(btn_back)
        hbox.add_widget(self.inp)
        vbox.add_widget(hbox)

        btn_scan = NeonButton(text="LOCATE TARGET", size_hint=(1, 0.1))
        btn_scan.color = C_WARN
        btn_scan.bind(on_press=self.start_scan)
        vbox.add_widget(btn_scan)

        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.out = TerminalLabel(text="Global Positioning Ready...", size_hint_y=None, markup=True, padding=(10,10))
        self.out.bind(texture_size=self.out.setter('size'))
        self.scroll.add_widget(self.out)
        vbox.add_widget(self.scroll)
        self.add_widget(vbox)

    def go_back(self, *args): self.manager.transition = SlideTransition(direction="right"); self.manager.current = 'menu'

    def start_scan(self, instance):
        target = self.inp.text
        self.out.text = ""
        threading.Thread(target=self.run_logic, args=(target,), daemon=True).start()

    def run_logic(self, target):
        from kivy.clock import Clock
        def log(msg): Clock.schedule_once(lambda dt: setattr(self.out, 'text', self.out.text + msg + "\n"))
        
        url = f"http://ip-api.com/json/{target}" if target else "http://ip-api.com/json/"
        log(f"[color=#FFD700]TRACING SIGNAL...[/color]")
        
        try:
            data = requests.get(url, timeout=5).json()
            if data.get('status') == 'fail':
                log("[!] QUERY FAILED")
                return

            log(f"[b]IP:[/b] {data.get('query')}")
            log(f"[b]ISP:[/b] {data.get('isp')}")
            log(f"[b]ORG:[/b] {data.get('org')}")
            log(f"[b]CITY:[/b] {data.get('city')}")
            log(f"[b]REGION:[/b] {data.get('regionName')}")
            log(f"[b]COUNTRY:[/b] {data.get('country')}")
            
            # Map Link
            lat = data.get('lat')
            lon = data.get('lon')
            map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            log(f"\n[ref={map_url}][color=#00E5FF]>> OPEN ON GOOGLE MAPS[/color][/ref]")

        except Exception as e:
            log(f"[color=#FF3333]Error: {str(e)}[/color]")

# --- APP BUILDER ---
class PasientNullMobile(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(UserScreen(name='user'))
        sm.add_widget(SpyScreen(name='spy'))
        sm.add_widget(IPScreen(name='ip'))
        return sm

if __name__ == '__main__':
    PasientNullMobile().run()
