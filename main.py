from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import requests
import threading

# --- THEME CONFIG ---
Window.clearcolor = (0.05, 0.05, 0.05, 1) # Black Background
C_GREEN = (0, 1, 0, 1)

class PasientNullMobile(App):
    def build(self):
        # Main Layout
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        self.header = Label(text="[b]PASIENTNULL MOBILE[/b]", markup=True, size_hint=(1, 0.1), color=C_GREEN)
        self.layout.add_widget(self.header)
        
        # Input Field
        self.target_input = TextInput(hint_text="Enter Username or IP", size_hint=(1, 0.1), 
                                      multiline=False, background_color=(0.2,0.2,0.2,1), foreground_color=(1,1,1,1))
        self.layout.add_widget(self.target_input)
        
        # Buttons Area
        btn_layout = BoxLayout(size_hint=(1, 0.15), spacing=5)
        
        btn_user = Button(text="USER HUNT", background_color=(0, 0.5, 0, 1))
        btn_user.bind(on_press=self.start_user_scan)
        
        btn_ip = Button(text="IP INTEL", background_color=(0, 0.5, 1, 1))
        btn_ip.bind(on_press=self.start_ip_scan)
        
        btn_layout.add_widget(btn_user)
        btn_layout.add_widget(btn_ip)
        self.layout.add_widget(btn_layout)

        # Output Area (Scrollable)
        self.scroll = ScrollView(size_hint=(1, 0.6))
        self.output_label = Label(text="System Ready...\n", size_hint_y=None, markup=True, halign="left", valign="top")
        self.output_label.bind(texture_size=self.output_label.setter('size'))
        self.scroll.add_widget(self.output_label)
        self.layout.add_widget(self.scroll)
        
        return self.layout

    def log(self, msg, color="ffffff"):
        # Helper to add text to the screen safely from background threads
        from kivy.clock import Clock
        def update(dt):
            self.output_label.text += f"[color={color}]{msg}[/color]\n"
        Clock.schedule_once(update)

    def start_user_scan(self, instance):
        target = self.target_input.text
        if not target: return
        self.output_label.text = "" # Clear screen
        self.log(f"SCANNING FOR: {target}...", "00ff00")
        threading.Thread(target=self.logic_user, args=(target,), daemon=True).start()

    def start_ip_scan(self, instance):
        self.output_label.text = ""
        self.log("FETCHING IP DATA...", "00ccff")
        threading.Thread(target=self.logic_ip, daemon=True).start()

    # --- LOGIC ---
    def logic_user(self, target):
        sites = {
            "Instagram": "https://www.instagram.com/{}",
            "GitHub": "https://github.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "Twitter": "https://twitter.com/{}",
            "Twitch": "https://www.twitch.tv/{}"
        }
        headers = {'User-Agent': 'Mozilla/5.0'}
        for site, url in sites.items():
            try:
                r = requests.get(url.format(target), headers=headers, timeout=3)
                if r.status_code == 200:
                    self.log(f"[+] FOUND: {site}", "00ff00")
                elif r.status_code == 404:
                    self.log(f"[-] Missing: {site}", "ff0000")
            except:
                self.log(f"[!] Error: {site}", "ffff00")
        self.log("SCAN COMPLETE.")

    def logic_ip(self, target=None):
        try:
            # Get Public IP info
            data = requests.get("http://ip-api.com/json/").json()
            self.log(f"IP: {data['query']}", "00ccff")
            self.log(f"ISP: {data['isp']}")
            self.log(f"LOC: {data['city']}, {data['country']}")
        except:
            self.log("Connection Failed.", "ff0000")

if __name__ == '__main__':
    PasientNullMobile().run()