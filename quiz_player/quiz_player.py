import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import time

def load_quizzes(filename):
    with open(filename, "r") as file:
        content = file.read().strip()
    raw_quizzes = content.split("\n\n")
    quizzes = []
    for raw in raw_quizzes:
        lines = raw.strip().split("\n")
        if len(lines) < 6:
            continue
        question = lines[0][3:]
        choices = [line[3:] for line in lines[1:5]]
        correct = lines[5].split(":")[1].strip()
        quizzes.append((question, choices, correct))
    return quizzes

class QuizApp:
    def __init__(self, root, quizzes):
        self.root = root
        self.root.title("Vibrant Quiz Player")
        self.root.geometry("700x500")
        self.root.configure(bg="#008080")
        self.quizzes = quizzes
        self.q_index = 0
        self.score = 0
        self.selected = tk.StringVar()

        pygame.mixer.init()
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.play(-1)

        self.start_frame = tk.Frame(root, bg="#008080")
        self.start_frame.pack(expand=True)
        tk.Label(self.start_frame, text="Welcome to the Quiz!", font=("Helvetica", 20, "bold"), bg="#008080", fg="black").pack(pady=20)
        tk.Button(self.start_frame, text="Start Quiz", font=("Helvetica", 14), bg="#004d40", fg="white", command=self.start_quiz).pack()

        self.quiz_frame = tk.Frame(root, bg="#008080")
        self.question_label = tk.Label(self.quiz_frame, text="", font=("Helvetica", 16), bg="forest green", fg="white", wraplength=600, justify="center", padx=10, pady=10, relief="solid", bd=3)
        self.question_label.pack(pady=20)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_frame, text="", variable=self.selected, value=chr(65 + i),
                                font=("Helvetica", 14), bg="#008080", fg="black", anchor="w", activebackground="#004d40", activeforeground="white", relief="solid", width=25)
            rb.pack(anchor="center", pady=5)
            self.radio_buttons.append(rb)

        self.progress = ttk.Progressbar(self.quiz_frame, length=300, mode='determinate')
        self.progress.pack(pady=15)

        self.score_label = tk.Label(self.quiz_frame, text="Score: 0", font=("Helvetica", 14), bg="#008080", fg="black")
        self.score_label.pack(pady=10)

        self.next_button = tk.Button(self.quiz_frame, text="Next", font=("Helvetica", 14), bg="#004d40", fg="white", command=self.next_question)
        self.next_button.pack(pady=10)

    def start_quiz(self):
        self.start_frame.pack_forget()
        self.quiz_frame.pack(expand=True)
        self.load_question()

    def load_question(self):
        if self.q_index < len(self.quizzes):
            question, choices, _ = self.quizzes[self.q_index]
            self.question_label.config(text=f"Q{self.q_index + 1}: {question}")
            self.selected.set(None)
            for i, choice in enumerate(choices):
                self.radio_buttons[i].config(text=f"{chr(65 + i)}. {choice}", value=chr(65 + i))
            self.progress["value"] = (self.q_index / len(self.quizzes)) * 100
            self.score_label.config(text=f"Score: {self.score}")
        else:
            self.show_score()

    def next_question(self):
        if not self.selected.get():
            messagebox.showwarning("No selection", "Please choose an answer before continuing.")
            return

        _, _, correct = self.quizzes[self.q_index]
        if self.selected.get() == correct:
            self.score += 1
            pygame.mixer.Sound("correct.mp3").play()
            self.feedback_animation("Correct!", "#00e676")
        else:
            pygame.mixer.Sound("wrong.mp3").play()
            self.feedback_animation("Wrong!", "#d50000")

        self.q_index += 1
        self.load_question()

    def feedback_animation(self, feedback_text, color):
        feedback_label = tk.Label(self.quiz_frame, text=feedback_text, font=("Helvetica", 24, "bold"), fg=color, bg="#008080")
        feedback_label.pack(pady=10)
        self.root.after(500, feedback_label.destroy)
        self.root.after(1000, self.show_next_button)

    def show_next_button(self):
        self.next_button.pack(pady=10)

    def show_score(self):
        pygame.mixer.music.stop()

        if self.score == len(self.quizzes):
            pygame.mixer.Sound("perfect.mp3").play()
        elif self.score == 0:
            pygame.mixer.Sound("zero.mp3").play()
        elif self.score > 0:
            pygame.mixer.Sound("pass.mp3").play()

        messagebox.showinfo("Quiz Complete", f"You got {self.score} out of {len(self.quizzes)} correct!")
        self.root.quit()

filename = "quiz_entries.txt"
quizzes = load_quizzes(filename)

if quizzes:
    root = tk.Tk()
    app = QuizApp(root, quizzes)
    root.mainloop()
else:
    print("No quizzes found in the file.")