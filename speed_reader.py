
# speed_reader.py
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import time
import threading
import re
from themes import ThemeManager

class SpeedReader:
    def __init__(self, root):
        self.root = root
        self.theme_manager = ThemeManager()
        
        self.root.title("Enhanced Speed Reader")
        self.root.geometry("800x600")
        self.theme_manager.apply_theme(self.root)
        
        # Initialize styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Define theme-specific styles
        self.configure_styles()
        
        # Reading configuration
        self.text = ""
        self.wpm = 300
        self.words_per_chunk = 1
        self.running = False
        self.paused = False
        self.progress = 0
        self.base_delay = 60 / self.wpm
        
        # Animation configuration
        self.fade_steps = 10
        
        # Punctuation delays
        self.punctuation_delays = {
            '.': 2.0, '!': 2.0, '?': 2.0,
            ',': 1.5, ';': 1.5, ':': 1.5,
            '-': 1.2, '(': 1.2, ')': 1.2
        }
        
        self.setup_frames()
        self.setup_ui()
        self.root.bind('<Configure>', self.on_window_resize)
       
    def configure_styles(self):
        current_theme = self.theme_manager.current_theme
        theme = self.theme_manager.get_theme(current_theme)
        
        # Configure ttk Button style
        self.style.configure(f"{current_theme}.TButton", 
                           background=theme["button_background"],
                           foreground=theme["button_text"],
                           font=('Arial', 10))
        
        # Configure ttk Progressbar style
        self.style.configure(f"{current_theme}.Horizontal.TProgressbar", 
                           background=theme["progress_foreground"],
                           troughbackground=theme["progress_background"],
                           bordercolor=theme["progress_foreground"],
                           lightcolor=theme["progress_foreground"],
                           darkcolor=theme["progress_foreground"])
    
    def setup_frames(self):
        self.reading_frame = tk.Frame(self.root)
        self.control_frame = tk.Frame(self.root)
        self.theme_manager.apply_theme(self.reading_frame)
        self.theme_manager.apply_theme(self.control_frame)
            
    def setup_ui(self):
        self.setup_reading_frame()
        self.setup_control_frame()
        self.show_control_frame()
        self.apply_theme()  # Apply the theme after setting up the UI
        

    def fade_color(self, hex_color, opacity):
        """Convert color to a faded version by mixing with background."""
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Get background color
        bg_color = self.theme_manager.get_theme(self.theme_manager.current_theme)["background"]
        bg_r = int(bg_color[1:3], 16)
        bg_g = int(bg_color[3:5], 16)
        bg_b = int(bg_color[5:7], 16)
        
        # Mix colors based on opacity
        mixed_r = int(r * opacity + bg_r * (1 - opacity))
        mixed_g = int(g * opacity + bg_g * (1 - opacity))
        mixed_b = int(b * opacity + bg_b * (1 - opacity))
        
        return f"#{mixed_r:02x}{mixed_g:02x}{mixed_b:02x}"



    def setup_reading_frame(self):
        # Container for the reading display
        self.display_container = tk.Frame(self.reading_frame)
        self.display_container.pack(expand=True, fill=tk.BOTH)
        self.theme_manager.apply_theme(self.display_container)

        # Create a canvas for better animation control
        self.canvas = tk.Canvas(
            self.display_container,
            highlightthickness=0,
            bg=self.theme_manager.get_theme(self.theme_manager.current_theme)["background"]
        )
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Create text items on canvas
        theme = self.theme_manager.get_theme(self.theme_manager.current_theme)
        self.text_items = []
        
        # Calculate positions
        center_y = self.display_container.winfo_height() // 2 if self.display_container.winfo_height() > 0 else 300
        spacing = 80  # Vertical spacing between lines
        
        # Create text items with different colors and opacity
        positions = [
            {"y_offset": -spacing, "color": self.fade_color(theme["text"], 0.3)},  # Previous word (faded)
            {"y_offset": 0, "color": theme["accent"]},  # Current word (full opacity)
            {"y_offset": spacing, "color": self.fade_color(theme["text"], 0.3)}  # Next word (faded)
        ]
        
        for pos in positions:
            text_item = self.canvas.create_text(
                400,  # x position (will be centered later)
                center_y + pos["y_offset"],
                text="",
                font=("Arial", 48, "bold"),
                fill=pos["color"],
                anchor="center"
            )
            self.text_items.append(text_item)

        # Bind resize event to canvas
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        # Add progress information container
        self.progress_container = tk.Frame(self.reading_frame)
        self.progress_container.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        self.theme_manager.apply_theme(self.progress_container)

        # Add time remaining label
        self.reading_time_label = tk.Label(
            self.progress_container, 
            text="Time remaining: 0:00",
            font=("Arial", 12)
        )
        self.reading_time_label.pack(pady=(0, 5))
        self.theme_manager.apply_theme(self.reading_time_label)

        # Add progress bar
        self.reading_progress_bar = ttk.Progressbar(
            self.progress_container, 
            length=600,
            mode='determinate',
            style=f"{self.theme_manager.current_theme}.Horizontal.TProgressbar"
        )
        self.reading_progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Control buttons
        reading_buttons = tk.Frame(self.progress_container)
        reading_buttons.pack(pady=5)
        self.theme_manager.apply_theme(reading_buttons)

        self.reading_pause_button = ttk.Button(
            reading_buttons,
            text="Pause",
            command=self.pause_reading
        )
        self.reading_pause_button.pack(side=tk.LEFT, padx=5)

        self.reading_stop_button = ttk.Button(
            reading_buttons,
            text="Stop",
            command=self.stop_reading
        )
        self.reading_stop_button.pack(side=tk.LEFT, padx=5)
    

    def on_canvas_resize(self, event):
        """Handle canvas resize events."""
        # Update text positions
        self.canvas.update_idletasks()
        center_x = event.width // 2
        center_y = event.height // 2
        spacing = 80
        
        positions = [center_y - spacing, center_y, center_y + spacing]
        
        for text_item, y_pos in zip(self.text_items, positions):
            self.canvas.coords(text_item, center_x, y_pos)


    def update_display(self, prev_word, current_word, next_word):
        # Update text for each item
        words = [prev_word, current_word, next_word]
        
        # Calculate canvas center
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        spacing = 80

        # Update positions and text
        positions = [center_y - spacing, center_y, center_y + spacing]
        
        # Define font sizes
        font_size_small = 24
        font_size_large = 36
        
        for i, (text_item, word) in enumerate(zip(self.text_items, words)):
            # Update text
            self.canvas.itemconfig(text_item, text=word if word else "")
            
            # Update position
            self.canvas.coords(text_item, center_x, positions[i])
            
            # Adjust font size if needed
            if word:
                # Get current font configuration
                current_font = self.canvas.itemcget(text_item, "font")
                
                # Default font settings if none are specified
                font_family = "Arial"
                
                # Try to parse existing font settings
                try:
                    if isinstance(current_font, str):
                        font_parts = current_font.split()
                        if len(font_parts) >= 2:
                            font_family = font_parts[0]
                except (ValueError, IndexError):
                    # If parsing fails, use defaults
                    pass
                
                # Calculate maximum width
                max_width = canvas_width * 0.8
                
                # Create temporary text to measure width
                if i == 1:  # Middle row
                    test_font = (font_family, font_size_large)
                else:
                    test_font = (font_family, font_size_small)
                text_width = self.canvas.create_text(0, 0, text=word, font=test_font)
                bbox = self.canvas.bbox(text_width)
                self.canvas.delete(text_width)
                
                if bbox and bbox[2] - bbox[0] > max_width:
                    # Calculate new font size
                    if i == 1:  # Middle row
                        new_size = int(font_size_large * max_width / (bbox[2] - bbox[0]))
                    else:
                        new_size = int(font_size_small * max_width / (bbox[2] - bbox[0]))
                    new_size = max(12, min(new_size, 48))  # Keep size within reasonable bounds
                    self.canvas.itemconfig(text_item, font=(font_family, new_size, "bold"))
                else:
                    # Apply the current font settings
                    if i == 1:  # Middle row
                        self.canvas.itemconfig(text_item, font=(font_family, font_size_large, "bold"))
                    else:
                        self.canvas.itemconfig(text_item, font=(font_family, font_size_small, "bold"))


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
        """Handle main window resize events"""
        if event.widget == self.root:
            # If we have a canvas, update its text positions
            if hasattr(self, 'canvas') and hasattr(self, 'text_items'):
                self.canvas.update_idletasks()
                center_x = self.canvas.winfo_width() // 2
                center_y = self.canvas.winfo_height() // 2
                spacing = 80  # Vertical spacing between lines
                
                # Update position for each text item
                positions = [center_y - spacing, center_y, center_y + spacing]
                for text_item, y_pos in zip(self.text_items, positions):
                    self.canvas.coords(text_item, center_x, y_pos)
                    
                    # Get current text for this item
                    current_text = self.canvas.itemcget(text_item, "text")
                    if current_text:
                        # Check if text needs resizing
                        window_width = self.root.winfo_width()
                        max_width = window_width * 0.8
                        
                        # Create temporary text to measure width
                        current_font = self.canvas.itemcget(text_item, "font")
                        font_family, font_size = current_font.split()
                        test_font = (font_family, int(font_size))
                        temp_text = self.canvas.create_text(0, 0, text=current_text, font=test_font)
                        bbox = self.canvas.bbox(temp_text)
                        self.canvas.delete(temp_text)
                        
                        if bbox and bbox[2] - bbox[0] > max_width:
                            # Calculate new font size
                            new_size = int(int(font_size) * max_width / (bbox[2] - bbox[0]))
                            new_size = max(12, min(new_size, 48))  # Keep size within reasonable bounds
                            self.canvas.itemconfig(text_item, font=(font_family, new_size))
    
    def preprocess_text(self, text):
        def number_to_words(match):
            num = match.group(0)
            try:
                n = int(num)
                if 0 <= n <= 999:
                    return num
                return num
            except:
                return num
        
        text = re.sub(r'\b\d+\b', number_to_words, text)
        text = re.sub(r'([^\w\s])', r' \1 ', text)
        return ' '.join(text.split())
    
    def calculate_word_delay(self, word):
        delay = self.base_delay * self.words_per_chunk
        
        if len(word) > 8:
            delay *= 1.5
        elif len(word) > 6:
            delay *= 1.25
        
        for punct, mult in self.punctuation_delays.items():
            if punct in word:
                delay *= mult
                break
        
        return delay


    def format_word_with_focus(self, word):
        length = len(word)
        focus_index = max(1, min(length - 1, length // 3))
        
        before_focus = word[:focus_index]
        focus_char = word[focus_index]
        after_focus = word[focus_index + 1:]
        
        return before_focus, focus_char, after_focus
    
    
    def update_word_display(self, word):
        before, focus, after = self.format_word_with_focus(word)
        
        display_text = f"{before}{focus}{after}"
        self.word_display.config(text=display_text)
        
        self.focus_point.pack_configure(pady=(0, self.word_display.winfo_height() // 8))
    
    def setup_control_frame(self):
        self.label = tk.Label(self.control_frame, text="Speed Reader", 
                            font=("Arial", 24, "bold"))
        self.label.pack(pady=10)
        self.theme_manager.apply_theme(self.label)
        
        self.progress_bar = ttk.Progressbar(self.control_frame, 
                                          length=600, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.text_box = tk.Text(self.control_frame, height=5, width=60, 
                              font=("Arial", 12), 
                              bg=self.theme_manager.get_theme(self.theme_manager.current_theme)["text_box_background"], 
                              fg=self.theme_manager.get_theme(self.theme_manager.current_theme)["text_box_text"], 
                              insertbackground=self.theme_manager.get_theme(self.theme_manager.current_theme)["text_box_text"])
        self.text_box.pack(pady=10)
        self.theme_manager.apply_theme(self.text_box)
        
        self.button_frame = tk.Frame(self.control_frame)
        self.button_frame.pack()
        self.theme_manager.apply_theme(self.button_frame)
        
        self.start_button = ttk.Button(self.button_frame, text="Start", 
                                     command=self.handle_start_continue)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.load_button = ttk.Button(self.button_frame, text="Load Text", 
                                    command=self.load_text)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.setup_settings_ui()
        
    def setup_settings_ui(self):
        self.settings_frame = tk.Frame(self.control_frame)
        self.settings_frame.pack(pady=10)
        self.theme_manager.apply_theme(self.settings_frame)
        
        self.speed_label = tk.Label(self.settings_frame, 
                                  text=f"WPM: {self.wpm}", 
                                  font=("Arial", 12))
        self.speed_label.pack()
        self.theme_manager.apply_theme(self.speed_label)
        
        self.speed_slider = ttk.Scale(self.settings_frame, from_=100, to=1000, 
                                    orient="horizontal", command=self.update_speed)
        self.speed_slider.set(self.wpm)
        self.speed_slider.pack()
        
        self.chunk_frame = tk.Frame(self.control_frame)
        self.chunk_frame.pack(pady=5)
        self.theme_manager.apply_theme(self.chunk_frame)
        
        tk.Label(self.chunk_frame, text="Words per display:", 
                font=("Arial", 12)).pack(side=tk.LEFT)
        
        self.chunk_spinbox = ttk.Spinbox(self.chunk_frame, from_=1, to=5, width=5,
                                       command=self.update_chunk_size)
        self.chunk_spinbox.set(1)
        self.chunk_spinbox.pack(side=tk.LEFT, padx=5)
        
        self.stats_frame = tk.Frame(self.control_frame)
        self.stats_frame.pack(pady=5)
        self.theme_manager.apply_theme(self.stats_frame)
        
        self.time_label = tk.Label(self.stats_frame, text="Time remaining: 0:00", 
                                 font=("Arial", 12))
        self.time_label.pack()
        self.theme_manager.apply_theme(self.time_label)
        
        # Theme selection
        self.theme_label = tk.Label(self.settings_frame, text="Theme:")
        self.theme_label.pack()
        self.theme_manager.apply_theme(self.theme_label)
        
        self.theme_var = tk.StringVar()
        self.theme_var.set(self.theme_manager.current_theme)
        
        def update_theme_menu():
            self.theme_menu['values'] = list(self.theme_manager.themes.keys())
        
        self.theme_menu = ttk.Combobox(self.settings_frame,
                                     textvariable=self.theme_var,
                                     values=list(self.theme_manager.themes.keys()),
                                     postcommand=update_theme_menu)
        self.theme_menu.pack()
        
        self.theme_button = ttk.Button(self.settings_frame, text="Apply Theme",
                                     command=self.apply_theme)
        self.theme_button.pack()
    
    def apply_theme(self):
        theme = self.theme_manager.get_theme(self.theme_var.get())  # Get theme from theme_var
        self.theme_manager.current_theme = self.theme_var.get()  # Update current_theme

        self.theme_manager.apply_theme(self.reading_frame)
        self.theme_manager.apply_theme(self.control_frame)
        self.theme_manager.apply_theme(self.progress_container)
        self.theme_manager.apply_theme(self.display_container)

        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=theme["background"])

            for i, text_item in enumerate(self.text_items):
                if i == 1:
                    self.canvas.itemconfig(text_item, fill=theme["accent"])
                else:
                    self.canvas.itemconfig(text_item, fill=self.fade_color(theme["text"], 0.3))

        self.label.config(
            bg=theme["background"],
            fg=theme["text"]
        )
        self.speed_label.config(
            bg=theme["background"],
            fg=theme["text"]
        )
        self.time_label.config(
            bg=theme["background"],
            fg=theme["text"]
        )
        self.reading_time_label.config(
            bg=theme["background"],
            fg=theme["text"]
        )
        self.theme_label.config(
            bg=theme["background"],
            fg=theme["text"]
        )
        self.text_box.config(
            bg=theme["text_box_background"],
            fg=theme["text_box_text"],
            insertbackground=theme["text_box_text"]
        )

        self.start_button.config(
            style=f"{self.theme_manager.current_theme}.TButton"
        )
        self.load_button.config(
            style=f"{self.theme_manager.current_theme}.TButton"
        )
        self.reading_pause_button.config(
            style=f"{self.theme_manager.current_theme}.TButton"
        )
        self.reading_stop_button.config(
            style=f"{self.theme_manager.current_theme}.TButton"
        )
        self.theme_button.config(
            style=f"{self.theme_manager.current_theme}.TButton"
        )

        self.reading_progress_bar.configure(
            style=f"{self.theme_manager.current_theme}.Horizontal.TProgressbar"
        )

        self.progress_bar.configure(
            style=f"{self.theme_manager.current_theme}.Horizontal.TProgressbar"
        )
        self.speed_slider.configure(
            style=f"{self.theme_manager.current_theme}.Horizontal.TScale"
        )
        self.chunk_spinbox.configure(
            style=f"{self.theme_manager.current_theme}.TSpinbox"
        )
        self.theme_menu.configure(
            style=f"{self.theme_manager.current_theme}.TCombobox"
        )


        self.configure_styles() # Refresh styles
    
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
        self.base_delay = 60 / self.wpm  # Recalculate base_delay!
    
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
        time_text = f"Time remaining: {minutes}:{seconds:02d}"
        # Update both time labels
        self.time_label.config(text=time_text)
        self.reading_time_label.config(text=time_text)
    
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
                self.reading_pause_button.config(text="Continue")
                self.start_button.config(text="Start")
                self.show_control_frame()
            else:
                self.reading_pause_button.config(text="Pause")
                self.start_button.config(text="Continue")
                self.show_reading_frame()
    
    def stop_reading(self):
        self.running = False
        self.paused = False
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


            prev_chunk = self.get_word_chunk(self.current_word_index - self.words_per_chunk, 
                                            self.words_per_chunk, self.words)
            current_chunk = self.get_word_chunk(self.current_word_index, 
                                                self.words_per_chunk, self.words)
            next_chunk = self.get_word_chunk(self.current_word_index + self.words_per_chunk, 
                                            self.words_per_chunk, self.words)

            self.update_display(prev_chunk, current_chunk, next_chunk)

            # Update both progress bars
            progress_value = (self.current_word_index / total_words) * 100
            self.progress_bar["value"] = progress_value
            self.reading_progress_bar["value"] = progress_value

            self.update_time_remaining(total_words - self.current_word_index)

           # Calculate delay for each word in the chunk
            chunk_words = current_chunk.split()
            if chunk_words: #check if list is empty
                delay = sum(self.calculate_word_delay(word) for word in chunk_words) / len(chunk_words)

                # Adjust delay for chunk size.  IMPORTANT: No longer divide.
                # The individual word delays already consider the number of words displayed.
                # Multiplying by chunk size makes it much slower.
            else:
                delay = self.base_delay #if chunk is empty use the base delay

            time.sleep(delay)  # Use the calculated delay

            self.current_word_index += self.words_per_chunk
            
        if self.running:
            self.stop_reading()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedReader(root)
    root.mainloop()
