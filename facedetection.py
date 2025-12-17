import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import pyttsx3
from deepface import DeepFace
import threading

# Colors for a modern Dark UI
BG_COLOR = "#1e1e2e"        # Deep navy/black
SIDEBAR_COLOR = "#181825"   # Darker sidebar
ACCENT_COLOR = "#89b4fa"    # Soft blue
TEXT_COLOR = "#cdd6f4"      # Off-white
SUCCESS_COLOR = "#a6e3a1"   # Soft green

def speak_text(text):
    def run_speech():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.say(text)
            engine.runAndWait()
        except: pass
    threading.Thread(target=run_speech, daemon=True).start()

class ModernFaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sic Mundus | AI Dashboard")
        self.root.geometry("1000x800")
        self.root.configure(bg=BG_COLOR)
        self.current_path = None
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=BG_COLOR)
        style.configure("Sidebar.TFrame", background=SIDEBAR_COLOR)
        
        # Modern Button Style
        style.configure("Action.TButton", 
                        background=ACCENT_COLOR, 
                        foreground=BG_COLOR, 
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("Action.TButton", background=[('active', SUCCESS_COLOR)])

    def create_widgets(self):
        # --- Sidebar ---
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="SIC MUNDUS", font=("Segoe UI", 18, "bold"), 
                 bg=SIDEBAR_COLOR, fg=ACCENT_COLOR).pack(pady=30)
        
        self.btn_open = ttk.Button(self.sidebar, text="📂 Load Image", 
                                   style="Action.TButton", command=self.open_file)
        self.btn_open.pack(pady=10, padx=20, fill=tk.X)

        self.btn_analyze = ttk.Button(self.sidebar, text="🧠 Analyze Face", 
                                      style="Action.TButton", command=self.analyze_image)
        self.btn_analyze.pack(pady=10, padx=20, fill=tk.X)

        tk.Label(self.sidebar, text="V 2.0 Offline Engine", font=("Segoe UI", 8), 
                 bg=SIDEBAR_COLOR, fg="#585b70").pack(side=tk.BOTTOM, pady=20)

        # --- Main Content ---
        self.main_content = ttk.Frame(self.root)
        self.main_content.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=40, pady=40)

        # Image Container (Rounded-look Card)
        self.img_card = tk.Label(self.main_content, text="Select an image to begin", 
                                 bg=SIDEBAR_COLOR, fg="#6c7086", 
                                 font=("Segoe UI", 12), width=60, height=18,
                                 highlightthickness=1, highlightbackground=ACCENT_COLOR)
        self.img_card.pack(pady=(0, 20))

        # Results Console
        self.results_text = tk.Text(self.main_content, height=12, width=80, 
                                   font=("Consolas", 11), bg="#11111b", 
                                   fg=SUCCESS_COLOR, borderwidth=0, 
                                   padx=20, pady=20, insertbackground='white')
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.insert(tk.END, "> System Ready...\n> Awaiting input...")

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png")])
        if filename:
            self.current_path = filename
            img = Image.open(filename)
            img.thumbnail((500, 400))
            img_tk = ImageTk.PhotoImage(img)
            self.img_card.config(image=img_tk, text="")
            self.img_card.image = img_tk
            self.results_text.insert(tk.END, f"\n> Loaded: {filename.split('/')[-1]}")

    def analyze_image(self):
        if not self.current_path:
            messagebox.showwarning("System", "Please load an image first.")
            return

        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "> Initializing DeepFace Neural Network...\n")
        self.results_text.insert(tk.END, "> Running local inference (No Cloud)...\n")
        self.root.update()

        try:
            results = DeepFace.analyze(img_path=self.current_path, 
                                      actions=['age', 'gender', 'emotion'],
                                      enforce_detection=False)

            full_report = ""
            speech_msg = ""

            for i, face in enumerate(results):
                emo = face['dominant_emotion'].upper()
                age = face['age']
                gen = face['dominant_gender']
                
                full_report += f"\n[SUBJECT #{i+1}]\n"
                full_report += f"  AGE     : {age}\n"
                full_report += f"  GENDER  : {gen}\n"
                full_report += f"  EMOTION : {emo}\n"
                full_report += "-"*30 + "\n"
                speech_msg += f"Subject {i+1} is a {age} year old {gen} feeling {emo}. "

            self.results_text.insert(tk.END, full_report)
            speak_text(speech_msg)

        except Exception as e:
            self.results_text.insert(tk.END, f"\n[ERROR]: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFaceApp(root)
    root.mainloop()
