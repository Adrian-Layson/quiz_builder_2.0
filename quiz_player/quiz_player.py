import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os
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
        self.root.geometry("600x500")
        self.root.configure(bg="#008080")
        
        self.center_window()

        try:
            pygame.mixer.init()
            self.setup_audio()
        except Exception as e:
            messagebox.showwarning("Audio Error", f"Could not initialize audio: {str(e)}")

        self.quizzes = quizzes
        self.q_index = 0
        self.score = 0
        self.selected = tk.StringVar()

        self.setup_styles()
        self.create_widgets()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_audio(self):
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

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", 
                           thickness=12, 
                           troughcolor="#006666", 
                           background="#00acc1", 
                           bordercolor="#00acc1",
                           lightcolor="#00bcd4",
                           darkcolor="#0097a7")
        
        self.style.configure("TButton", 
                           font=("Helvetica", 12),
                           padding=6,
                           background="#26c6da",
                           foreground="white")
        self.style.map("TButton",
                      background=[('active', '#00acc1')])

    def create_widgets(self):
        self.start_frame = tk.Frame(self.root, bg="#008080")
        self.start_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(self.start_frame, 
                text="Welcome to the Quiz!", 
                font=("Helvetica", 18, "bold"), 
                bg="#008080", 
                fg="white").pack(pady=20)
        
        ttk.Button(self.start_frame, 
                  text="Start Quiz", 
                  command=self.start_quiz).pack(pady=10)

        self.quiz_frame = tk.Frame(self.root, bg="#008080")
        
        self.question_label = tk.Label(self.quiz_frame, 
                                       text="", 
                                       font=("Helvetica", 14, "bold"), 
                                       bg="#008080", 
                                       fg="white", 
                                       wraplength=500, 
                                       justify="center")
        self.question_label.pack(pady=(20, 10))

        self.choices_frame = tk.Frame(self.quiz_frame, bg="#008080")
        self.choices_frame.pack(pady=10)
        
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.choices_frame, 
                               text="", 
                               variable=self.selected, 
                               value=chr(65 + i),
                               font=("Helvetica", 12), 
                               bg="#008080", 
                               fg="white", 
                               selectcolor="#006666",
                               activebackground="#006666",
                               anchor="w")
            rb.grid(row=i, column=0, sticky="w", pady=2)
            self.radio_buttons.append(rb)

        self.progress = ttk.Progressbar(self.quiz_frame, 
                                     length=400, 
                                     mode='determinate')
        self.progress.pack(pady=15)

        self.next_button = ttk.Button(self.quiz_frame, 
                                   text="Next", 
                                   command=self.next_question)
        self.next_button.pack(pady=10)

    def start_quiz(self):
        if not self.quizzes:
            messagebox.showerror("Error", "No quizzes available to start!")
            return
            
        self.start_frame.pack_forget()
        self.quiz_frame.pack(expand=True, fill=tk.BOTH)
        self.load_question()

    def load_question(self):
        if self.q_index < len(self.quizzes):
            question, choices, _ = self.quizzes[self.q_index]
            self.question_label.config(text=f"Q{self.q_index + 1}: {question}")
            self.selected.set('')
            
            for i, choice in enumerate(choices):
                self.radio_buttons[i].config(text=f"{chr(65 + i)}. {choice}", 
                                           state=tk.NORMAL)
            
            for i in range(len(choices), 4):
                self.radio_buttons[i].config(text="", state=tk.DISABLED)
                
            self.progress["value"] = (self.q_index / len(self.quizzes)) * 100
            
            if self.q_index == len(self.quizzes) - 1:
                self.next_button.config(text="Finish")
        else:
            self.show_score()

    def next_question(self):
        if not self.selected.get():
            messagebox.showwarning("No selection", "Please choose an answer before continuing.")
            return

        _, _, correct = self.quizzes[self.q_index]
        user_answer = self.selected.get().upper()
        
        if user_answer == correct:
            self.score += 1
            self.play_sound('correct')
        else:
            self.play_sound('wrong')

        self.q_index += 1
        self.load_question()

    def play_sound(self, sound_type):
        if sound_type == 'background':
            if self.audio_files.get('background'):
                pygame.mixer.music.play(-1, 0.0)
        else:
            if self.audio_files.get(sound_type):
                pygame.mixer.Sound(self.audio_files[sound_type]).play()

    def show_score(self):
        self.progress["value"] = 100
        percentage = (self.score / len(self.quizzes)) * 100
        
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
        pygame.mixer.music.stop()
        self.root.quit()

def main():
    filename = "quiz_entries.txt"
    quizzes = load_quizzes(filename)

    if quizzes:
        root = tk.Tk()
        app = QuizApp(root, quizzes)
        root.mainloop()

if __name__ == "__main__":
    main()