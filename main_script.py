import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import time
import threading

class SpeedReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Speed Reader")
        self.root.geometry("800x600")
        self.root.configure(bg="#2E3440")
        
        self.text = ""
        self.wpm = 300
        self.words_per_chunk = 1
        self.running = False
        self.paused = False
        self.progress = 0
        
        # Create frames for different states
        self.setup_frames()
        self.setup_ui()
        
    def setup_frames(self):
        self.reading_frame = tk.Frame(self.root, bg="#2E3440")
        self.control_frame = tk.Frame(self.root, bg="#2E3440")
        
    def setup_ui(self):
        self.setup_reading_frame()
        self.setup_control_frame()
        self.show_control_frame()
        
    def setup_reading_frame(self):
        self.word_display = tk.Label(self.reading_frame, text="", 
                                   font=("Arial", 48, "bold"),
                                   bg="#2E3440", fg="#88C0D0")
        self.word_display.pack(expand=True, pady=50)
        
        reading_buttons = tk.Frame(self.reading_frame, bg="#2E3440")
        reading_buttons.pack(side=tk.BOTTOM, pady=20)
        
        self.reading_pause_button = ttk.Button(reading_buttons, text="Pause", 
                                             command=self.pause_reading)
        self.reading_pause_button.pack(side=tk.LEFT, padx=5)
        
        self.reading_stop_button = ttk.Button(reading_buttons, text="Stop", 
                                            command=self.stop_reading)
        self.reading_stop_button.pack(side=tk.LEFT, padx=5)
        
    def setup_control_frame(self):
        self.label = tk.Label(self.control_frame, text="Speed Reader", 
                            font=("Arial", 24, "bold"), bg="#2E3440", fg="#D8DEE9")
        self.label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.control_frame, length=600, 
                                          mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.text_box = tk.Text(self.control_frame, height=5, width=60, 
                               font=("Arial", 12), bg="#3B4252", fg="#ECEFF4", 
                               insertbackground="white")
        self.text_box.pack(pady=10)
        
        self.button_frame = tk.Frame(self.control_frame, bg="#2E3440")
        self.button_frame.pack()
        
        # Create Start/Continue button
        self.start_button = ttk.Button(self.button_frame, text="Start", 
                                     command=self.handle_start_continue)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_button = ttk.Button(self.button_frame, text="Load Text", 
                                    command=self.load_text)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.setup_settings_ui()
        
    def setup_settings_ui(self):
        self.settings_frame = tk.Frame(self.control_frame, bg="#2E3440")
        self.settings_frame.pack(pady=10)
        
        self.speed_label = tk.Label(self.settings_frame, text=f"WPM: {self.wpm}", 
                                  font=("Arial", 12), bg="#2E3440", fg="#D8DEE9")
        self.speed_label.pack()
        
        self.speed_slider = ttk.Scale(self.settings_frame, from_=100, to=1000, 
                                    orient="horizontal", command=self.update_speed)
        self.speed_slider.set(self.wpm)
        self.speed_slider.pack()
        
        self.chunk_frame = tk.Frame(self.control_frame, bg="#2E3440")
        self.chunk_frame.pack(pady=5)
        
        tk.Label(self.chunk_frame, text="Words per display:", 
                bg="#2E3440", fg="#D8DEE9").pack(side=tk.LEFT)
        
        self.chunk_spinbox = ttk.Spinbox(self.chunk_frame, from_=1, to=5, width=5,
                                       command=self.update_chunk_size)
        self.chunk_spinbox.set(1)
        self.chunk_spinbox.pack(side=tk.LEFT, padx=5)
        
        self.stats_frame = tk.Frame(self.control_frame, bg="#2E3440")
        self.stats_frame.pack(pady=5)
        self.time_label = tk.Label(self.stats_frame, text="Time remaining: 0:00", 
                                 bg="#2E3440", fg="#D8DEE9")
        self.time_label.pack()

    def handle_start_continue(self):
        if self.paused:
            self.paused = False
            self.show_reading_frame()
        else:
            self.start_reading()

    def show_reading_frame(self):
        self.control_frame.pack_forget()
        self.reading_frame.pack(expand=True, fill=tk.BOTH)
        
    def show_control_frame(self):
        self.reading_frame.pack_forget()
        self.control_frame.pack(expand=True, fill=tk.BOTH)
        
    def update_chunk_size(self):
        try:
            self.words_per_chunk = int(self.chunk_spinbox.get())
        except ValueError:
            self.words_per_chunk = 1
            self.chunk_spinbox.set(1)
    
    def update_speed(self, value):
        self.wpm = int(float(value))
        self.speed_label.config(text=f"WPM: {self.wpm}")
    
    def load_text(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.text = file.read()
                    self.text_box.delete("1.0", tk.END)
                    self.text_box.insert(tk.END, self.text)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def get_word_chunk(self, index, chunk_size):
        words = self.text.split()
        start = index
        end = min(start + chunk_size, len(words))
        return " ".join(words[start:end])
    
    def update_time_remaining(self, words_remaining):
        minutes_remaining = (words_remaining / self.words_per_chunk) * (60 / self.wpm)
        minutes = int(minutes_remaining)
        seconds = int((minutes_remaining - minutes) * 60)
        self.time_label.config(text=f"Time remaining: {minutes}:{seconds:02d}")
    
    def start_reading(self):
        self.text = self.text_box.get("1.0", tk.END).strip()
        if not self.text:
            messagebox.showwarning("Warning", "Please enter or load some text first.")
            return
            
        if not self.running:
            self.running = True
            self.paused = False
            self.current_word_index = 0
            self.words = self.text.split()
            self.progress_bar["maximum"] = len(self.words)
            self.progress_bar["value"] = 0
            self.show_reading_frame()
            thread = threading.Thread(target=self.run_reader)
            thread.daemon = True
            thread.start()
    
    def pause_reading(self):
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.reading_pause_button.config(text="Pause")
                self.start_button.config(text="Continue")
                self.show_control_frame()
            else:
                self.reading_pause_button.config(text="Pause")
                self.start_button.config(text="Start")
                self.show_reading_frame()
    
    def stop_reading(self):
        self.running = False
        self.paused = False
        self.word_display.config(text="")
        self.progress_bar["value"] = 0
        self.time_label.config(text="Time remaining: 0:00")
        self.reading_pause_button.config(text="Pause")
        self.start_button.config(text="Start")
        self.show_control_frame()
    
    def run_reader(self):
        delay = 60 / self.wpm
        total_words = len(self.text.split())
        
        while self.current_word_index < total_words:
            if not self.running:
                break
            if self.paused:
                time.sleep(0.1)
                continue
                
            chunk = self.get_word_chunk(self.current_word_index, self.words_per_chunk)
            self.word_display.config(text=chunk)
            self.progress_bar["value"] = self.current_word_index
            self.update_time_remaining(total_words - self.current_word_index)
            
            self.current_word_index += self.words_per_chunk
            time.sleep(delay)
            
        if self.running:
            self.stop_reading()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReader(root)
    root.mainloop()