import tkinter as tk
from tkinter import ttk, messagebox
import pygame
from pathlib import Path

def load_quizzes(filename):
    try:
        with open(filename, "r", encoding='utf-8') as file:
            content = file.read().strip()
        raw_quizzes = content.split("\n\n")
        quizzes = []
        for raw in raw_quizzes:
            lines = raw.strip().split("\n")
            if len(lines) < 6:
                continue
            question = lines[0][3:].strip()
            choices = [line[3:].strip() for line in lines[1:5]]
            if not all(choices):
                continue
            correct = lines[5].split(":")[1].strip().upper()
            if correct not in ['A', 'B', 'C', 'D']:
                continue
            quizzes.append((question, choices, correct))
        return quizzes
    except FileNotFoundError:
        messagebox.showerror("Error", f"Quiz file '{filename}' not found!")
        return []
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load quizzes: {str(e)}")
        return []

class QuizApp:
    def __init__(self, root, quizzes):
        self.root = root
        self.root.title("Cool Quiz Player")
        self.root.geometry("800x600")
        self.canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_gradient()
        self.quizzes = quizzes
        self.q_index = 0
        self.score = 0
        self.selected = tk.StringVar()
        self.answered = False
        self.title_font = ("Segoe UI", 20, "bold")
        self.question_font = ("Segoe UI", 14, "bold")
        self.option_font = ("Segoe UI", 12)
        self.setup_audio()
        self.create_styles()
        self.create_welcome_screen()

    def draw_gradient(self):
        for i in range(600):
            r = 0
            g = min(128 + int(i/4), 255)
            b = min(128 + int(i/8), 255)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, 800, i, fill=color)

    def setup_audio(self):
        try:
            pygame.mixer.init()
            self.audio_files = {}
            bg_music = self.load_audio("background.mp3")
            if bg_music:
                pygame.mixer.music.load(bg_music)
                pygame.mixer.music.play(-1, 0.0)
            self.audio_files['correct'] = self.load_audio("correct.mp3")
            self.audio_files['wrong'] = self.load_audio("wrong.mp3")
            self.audio_files['perfect'] = self.load_audio("perfect.mp3")
            self.audio_files['pass'] = self.load_audio("pass.mp3")
            self.audio_files['zero'] = self.load_audio("zero.mp3")
            self.audio_files['check'] = self.load_audio("check.mp3")
        except Exception as e:
            messagebox.showwarning("Audio Error", f"Could not initialize audio: {str(e)}")

    def load_audio(self, filename):
        base_path = Path(__file__).parent
        possible_paths = [
            base_path / "music" / filename,
            base_path / filename,
            Path("music") / filename
        ]
        for path in possible_paths:
            if path.exists():
                return str(path)
        return None

    def create_styles(self):
        self.style = ttk.Style()
        self.style.configure("TProgressbar", thickness=15, troughcolor="#e0f7fa", background="#00acc1")
        self.style.configure("Small.TButton", 
                           font=("Segoe UI", 12, "bold"),
                           padding=(15, 5),
                           foreground="black",
                           background="#00838f")
        self.style.map("Small.TButton",
                      background=[("active", "#006064"), ("pressed", "#004d40")],
                      foreground=[("active", "black"), ("pressed", "black")])

    def create_welcome_screen(self):
        self.welcome_frame = tk.Frame(self.canvas, bg="#f0f8ff", bd=0, highlightthickness=0, relief=tk.FLAT)
        self.canvas.create_window(400, 300, window=self.welcome_frame, width=500, height=400, tags="welcome")
        self.canvas.create_rectangle(350, 250, 450, 350, fill="#d3d3d3", outline="", tags="shadow")
        
        title_label = tk.Label(self.welcome_frame, text="🌟 Maangas na Quiz 🌟", font=("Segoe UI", 24, "bold"), bg="#f0f8ff", fg="#2c3e50")
        title_label.pack(pady=(30, 10))
        
        subtitle_label = tk.Label(self.welcome_frame, text="Test your knowledge and have fun!", font=("Segoe UI", 12), bg="#f0f8ff", fg="#7f8c8d")
        subtitle_label.pack(pady=(0, 30))
        
        separator = ttk.Separator(self.welcome_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=50, pady=10)
        
        start_button = tk.Button(self.welcome_frame, text="START QUIZ", font=("Segoe UI", 14, "bold"), bg="#3498db", fg="white", activebackground="#2980b9", activeforeground="white", relief=tk.FLAT, bd=0, padx=30, pady=10, command=self.start_game)
        start_button.pack(pady=20)
        
        def on_enter(e):
            start_button['background'] = '#2980b9'
            start_button['cursor'] = 'hand2'
        
        def on_leave(e):
            start_button['background'] = '#3498db'
        
        start_button.bind("<Enter>", on_enter)
        start_button.bind("<Leave>", on_leave)
        
        footer_frame = tk.Frame(self.welcome_frame, bg="#f0f8ff")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        tk.Label(footer_frame, text="• • •", font=("Segoe UI", 20), bg="#f0f8ff", fg="#bdc3c7").pack()
        
        tk.Label(footer_frame, text="v2.0", font=("Segoe UI", 8), bg="#f0f8ff", fg="#95a5a6").pack(side=tk.RIGHT, padx=10)
        
        self.canvas.create_text(400, 550, text="Ready to challenge yourself?", font=("Segoe UI", 10, "italic"), fill="#7f8c8d")

    def start_game(self):
        self.welcome_frame.destroy()
        self.create_quiz_interface()
        self.load_question()

    def create_quiz_interface(self):
        self.main_frame = tk.Frame(self.canvas, bg="white", bd=2, relief=tk.RIDGE)
        self.canvas.create_window(400, 300, window=self.main_frame, width=750, height=550)
        
        self.header_frame = tk.Frame(self.main_frame, bg="white")
        self.header_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.header_frame, text="🌟 Quiz Time 🌟", font=self.title_font, bg="white", fg="#006666").pack(side=tk.LEFT)
        
        self.question_label = tk.Label(self.main_frame, text="", font=self.question_font, bg="white", fg="#333", 
                                     wraplength=700, justify="center", relief=tk.GROOVE, bd=2, padx=10, pady=10)
        self.question_label.pack(pady=(10, 20))
        
        self.choices_frame = tk.Frame(self.main_frame, bg="white")
        self.choices_frame.pack(pady=10)
        
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.choices_frame, text="", variable=self.selected, value=chr(65 + i), 
                              font=self.option_font, bg="white", fg="#333", selectcolor="#e0f7fa", 
                              activebackground="#e0f7fa", anchor="w", 
                              command=lambda: [self.play_sound('check'), self.enable_next_button()])
            rb.grid(row=i, column=0, sticky="w", pady=5, padx=20)
            self.radio_buttons.append(rb)
        
        self.progress_container = tk.Frame(self.main_frame, bg="white")
        self.progress_container.pack(fill=tk.X, pady=20)
        
        self.progress_frame = tk.Frame(self.progress_container, bg="white")
        self.progress_frame.pack(expand=True)
        
        self.progress = ttk.Progressbar(self.progress_frame, length=500, mode='determinate', style="TProgressbar")
        self.progress.pack(side=tk.LEFT)
        
        self.progress_label = tk.Label(self.progress_frame, text="0%", font=("Segoe UI", 10), bg="white", fg="#006666")
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ttk.Button(
            self.main_frame,
            text="Next",
            style="Small.TButton",
            command=self.next_question,
            state=tk.DISABLED
        )
        self.next_button.pack(pady=10)

    def enable_next_button(self):
        if not self.answered:
            self.next_button.config(state=tk.NORMAL)

    def update_progress(self):
        percent = (self.q_index / len(self.quizzes)) * 100
        self.progress["value"] = percent
        self.progress_label.config(text=f"{int(percent)}%")

    def load_question(self):
        self.answered = False
        self.next_button.config(state=tk.DISABLED)
        for rb in self.radio_buttons:
            rb.config(fg="#333", font=self.option_font)
        if self.q_index < len(self.quizzes):
            question, choices, _ = self.quizzes[self.q_index]
            self.question_label.config(text=f"Q{self.q_index + 1}: {question}")
            self.selected.set('')
            for i, choice in enumerate(choices):
                self.radio_buttons[i].config(text=f"{chr(65 + i)}. {choice}", state=tk.NORMAL)
            for i in range(len(choices), 4):
                self.radio_buttons[i].config(text="", state=tk.DISABLED)
            self.update_progress()
            if self.q_index == len(self.quizzes) - 1:
                self.next_button.config(text="Finish")

    def next_question(self):
        if not self.selected.get() and not self.answered:
            messagebox.showwarning("No selection", "Please choose an answer before continuing.")
            return
        
        if not self.answered:
            question, choices, correct = self.quizzes[self.q_index]
            user_answer = self.selected.get().upper()
            
            for i in range(4):
                if i < len(choices):
                    answer_char = chr(65 + i)
                    if answer_char == correct:
                        self.radio_buttons[i].config(fg="green", font=("Segoe UI", 12, "bold"))
                    elif answer_char == user_answer and user_answer != correct:
                        self.radio_buttons[i].config(fg="red", font=("Segoe UI", 12, "bold"))
            
            if user_answer == correct:
                self.score += 1
                self.play_sound('correct')
            else:
                self.play_sound('wrong')
            
            self.answered = True
            if self.q_index == len(self.quizzes) - 1:
                self.next_button.config(text="Finish")
            else:
                self.next_button.config(text="Next")
        else:
            self.q_index += 1
            if self.q_index >= len(self.quizzes):
                self.show_score()
            else:
                self.load_question()

    def play_sound(self, sound_type):
        if sound_type == 'background':
            if self.audio_files.get('background'):
                pygame.mixer.music.play(-1, 0.0)
        else:
            if self.audio_files.get(sound_type):
                sound = pygame.mixer.Sound(self.audio_files[sound_type])
                sound.play()

    def show_score(self):
        percentage = (self.score / len(self.quizzes)) * 100
        pygame.mixer.music.stop()
        
        if percentage == 100:
            self.play_sound('perfect')
        elif percentage >= 50:
            self.play_sound('pass')
        else:
            self.play_sound('zero')
        
        result_msg = f"You got {self.score} out of {len(self.quizzes)} correct!\n"
        result_msg += f"Score: {percentage:.1f}%"
        if percentage == 100:
            result_msg += "\nPerfect! 🎉"
        elif percentage >= 70:
            result_msg += "\nWell done! 👍"
        elif percentage >= 50:
            result_msg += "\nGood effort! 🙂"
        else:
            result_msg += "\nKeep practicing! 💪"
        
        messagebox.showinfo("Quiz Complete", result_msg)
        self.show_ending_screen()

    def show_ending_screen(self):
        self.main_frame.pack_forget()
        self.ending_frame = tk.Frame(self.canvas, bg="white", bd=3, relief=tk.RIDGE)
        self.canvas.create_window(400, 300, window=self.ending_frame, width=600, height=500)
        top_banner = tk.Frame(self.ending_frame, bg="#00acc1", height=80)
        top_banner.pack(fill=tk.X)
        tk.Label(
            top_banner,
            text="🏆",
            font=("Segoe UI", 40),
            bg="#00acc1",
            fg="white"
        ).pack(pady=10)
        tk.Label(
            self.ending_frame, 
            text="Thanks for playing!", 
            font=("Segoe UI", 24, "bold"), 
            bg="white", 
            fg="#006064"
        ).pack(pady=20)
        separator = ttk.Separator(self.ending_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=50, pady=5)
        tk.Label(
            self.ending_frame, 
            text="We hope you enjoyed the quiz!", 
            font=("Segoe UI", 14), 
            bg="white", 
            fg="#006064"
        ).pack(pady=10)
        score_frame = tk.Frame(self.ending_frame, bg="white")
        score_frame.pack(pady=15)
        tk.Label(
            score_frame,
            text=f"Final Score: {self.score}/{len(self.quizzes)}",
            font=("Segoe UI", 16, "bold"),
            bg="white",
            fg="#00acc1"
        ).pack()
        exit_button = tk.Button(
            self.ending_frame, 
            text="  Exit  ✕  ", 
            font=("Segoe UI", 14, "bold"), 
            bg="#00acc1", 
            fg="white", 
            activebackground="#00838f",
            activeforeground="white",
            relief=tk.RAISED,
            bd=3,
            command=self.root.quit
        )
        exit_button.pack(pady=25, ipadx=15, ipady=5)
        tk.Label(
            self.ending_frame,
            text="• • •",
            font=("Segoe UI", 20),
            bg="white",
            fg="#b2ebf2"
        ).pack(pady=10)

def main():
    filename = "quiz_entries.txt"
    quizzes = load_quizzes(filename)
    if quizzes:
        root = tk.Tk()
        app = QuizApp(root, quizzes)
        root.mainloop()

if __name__ == "__main__":
    main()