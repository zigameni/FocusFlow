import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import time
import threading
import re


class SpeedReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Speed Reader")
        self.root.geometry("800x600")
        self.root.configure(bg="#2E3440")
        
        # Reading configuration
        self.text = ""
        self.wpm = 300
        self.words_per_chunk = 1
        self.running = False
        self.paused = False
        self.progress = 0
        self.base_delay = 60 / self.wpm
        
        # Animation configuration
        self.fade_steps = 10  # Number of opacity steps for fade effect
        
        # Punctuation delays (multiplier of base delay)
        self.punctuation_delays = {
            '.': 2.0, '!': 2.0, '?': 2.0,
            ',': 1.5, ';': 1.5, ':': 1.5,
            '-': 1.2, '(': 1.2, ')': 1.2
        }
        
        self.setup_frames()
        self.setup_ui()
        self.root.bind('<Configure>', self.on_window_resize)
        
    def setup_frames(self):
        self.reading_frame = tk.Frame(self.root, bg="#2E3440")
        self.control_frame = tk.Frame(self.root, bg="#2E3440")
            
    def setup_ui(self):
        self.setup_reading_frame()
        self.setup_control_frame()
        self.show_control_frame()
        
        
    def setup_reading_frame(self):
        # Container for the reading display
        self.display_container = tk.Frame(self.reading_frame, bg="#2E3440")
        self.display_container.pack(expand=True, fill=tk.BOTH)

        # Create a vertical container for the text rows
        self.text_container = tk.Frame(self.display_container, bg="#2E3440")
        self.text_container.place(relx=0.5, rely=0.5, anchor="center")

        # Create three rows with minimal spacing
        self.text_rows = []
        colors = ["#4C566A", "#88C0D0", "#4C566A"]  # Dimmed, Bright, Dimmed

        for i in range(3):
            label = tk.Label(self.text_container, text="",
                            font=("Arial", 48, "bold"),
                            bg="#2E3440", fg=colors[i],
                            justify=tk.CENTER)
            label.pack(pady=5)  # Adjust pady to control spacing between rows
            self.text_rows.append(label)

        # Control buttons
        reading_buttons = tk.Frame(self.reading_frame, bg="#2E3440")
        reading_buttons.pack(side=tk.BOTTOM, pady=20)

        self.reading_pause_button = ttk.Button(reading_buttons, text="Pause",
                                             command=self.pause_reading)
        self.reading_pause_button.pack(side=tk.LEFT, padx=5)

        self.reading_stop_button = ttk.Button(reading_buttons, text="Stop",
                                            command=self.stop_reading)
        self.reading_stop_button.pack(side=tk.LEFT, padx=5)
    
    def update_display(self, prev_word, current_word, next_word):
        # Update all three rows
        self.text_rows[0].config(text=prev_word if prev_word else "")
        self.text_rows[1].config(text=current_word)
        self.text_rows[2].config(text=next_word if next_word else "")

        # Ensure text fits within window width
        for i, row in enumerate(self.text_rows):
            text = row.cget("text")
            if text:
                label_width = len(text) * self.get_font_size(row)
                if label_width > self.root.winfo_width() * 0.8:
                    # If text is too long, reduce font size
                    new_size = int(self.root.winfo_width() * 0.8 / len(text))
                    new_size = max(12, min(new_size, 72))
                    row.configure(font=("Arial", new_size, "bold"))

    def get_word_chunk(self, index, chunk_size, words):
        if index < 0 or index >= len(words):
            return ""
        end = min(index + chunk_size, len(words))
        return " ".join(words[index:end])
    
    def get_font_size(self, label):
        font = label.cget("font")
        if font:
            return int(font.split()[1])
        return 0
    
    def on_window_resize(self, event):
        if event.widget == self.root:
            window_width = event.width
            window_height = event.height
            
            # Calculate new font size based on window dimensions
            max_font_size = min(72, max(24, int(min(window_width / 25, window_height / 8))))
            
            # Ensure text fits within the window width
            max_word_width = max(len(word) for word in self.words) if hasattr(self, 'words') else 10
            max_font_size = min(max_font_size, int((window_width * 0.8) / max_word_width))
            
            # Update font sizes for all rows
            for row in self.text_rows:
                row.configure(font=("Arial", max_font_size, "bold"))
    
    def preprocess_text(self, text):
        # Convert numbers to words if they're relatively simple
        def number_to_words(match):
            num = match.group(0)
            try:
                n = int(num)
                if 0 <= n <= 999:  # Only convert "simple" numbers
                    return num  # For now, keeping numbers as is
                return num
            except:
                return num
        
        # Replace numbers with words
        text = re.sub(r'\b\d+\b', number_to_words, text)
        
        # Add spaces around special characters for better reading
        text = re.sub(r'([^\w\s])', r' \1 ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def calculate_word_delay(self, word):
        delay = self.base_delay * self.words_per_chunk  # Adjust delay for multiple words
        
        # Adjust for word length
        if len(word) > 8:
            delay *= 1.5
        elif len(word) > 6:
            delay *= 1.25
        
        # Check for punctuation
        for punct, mult in self.punctuation_delays.items():
            if punct in word:
                delay *= mult
                break
        
        return delay


    def format_word_with_focus(self, word):
        # Find the optimal focus point (roughly 1/3 into the word)
        length = len(word)
        focus_index = max(1, min(length - 1, length // 3))
        
        # Split the word into parts
        before_focus = word[:focus_index]
        focus_char = word[focus_index]
        after_focus = word[focus_index + 1:]
        
        return before_focus, focus_char, after_focus
    
    
    def update_word_display(self, word):
        # Format word with focus point
        before, focus, after = self.format_word_with_focus(word)
        
        # Update display with formatted word
        display_text = f"{before}{focus}{after}"
        self.word_display.config(text=display_text)
        
        # Position focus point indicator above the focus character
        # (This is approximate since we're using a monospace font)
        self.focus_point.pack_configure(pady=(0, self.word_display.winfo_height() // 8))
    
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
        # Remove the line below
        # self.word_display.config(text="")
        self.progress_bar["value"] = 0
        self.time_label.config(text="Time remaining: 0:00")
        self.reading_pause_button.config(text="Pause")
        self.start_button.config(text="Start")
        self.show_control_frame()
    
    def run_reader(self):
        text = self.preprocess_text(self.text)
        self.words = text.split()
        total_words = len(self.words)
        
        while self.current_word_index < total_words:
            if not self.running:
                break
            if self.paused:
                time.sleep(0.1)
                continue
            
            # Get previous, current, and next chunks
            prev_chunk = self.get_word_chunk(self.current_word_index - self.words_per_chunk, 
                                           self.words_per_chunk, self.words)
            current_chunk = self.get_word_chunk(self.current_word_index, 
                                              self.words_per_chunk, self.words)
            next_chunk = self.get_word_chunk(self.current_word_index + self.words_per_chunk, 
                                           self.words_per_chunk, self.words)
            
            # Update display with all three chunks
            self.update_display(prev_chunk, current_chunk, next_chunk)
            
            # Update progress
            self.progress_bar["value"] = self.current_word_index
            self.update_time_remaining(total_words - self.current_word_index)
            
            # Calculate delay based on the word characteristics
            delay = self.calculate_word_delay(current_chunk)
            
            self.current_word_index += self.words_per_chunk
            time.sleep(delay)
        
        if self.running:
            self.stop_reading()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReader(root)
    root.mainloop()