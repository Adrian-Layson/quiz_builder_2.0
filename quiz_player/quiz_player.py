import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pygame

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
        pygame.mixer.init()
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.play(-1)

        self.root = root
        self.root.title("Cool Quiz Player")
        self.root.geometry("600x500")
        self.root.configure(bg="teal")

        self.quizzes = quizzes
        self.q_index = 0
        self.score = 0
        self.selected = tk.StringVar()

        self.start_frame = tk.Frame(root, bg="teal")
        self.start_frame.pack(expand=True)
        tk.Label(self.start_frame, text="Welcome to the Quiz!", font=("Helvetica", 20, "bold"), bg="teal", fg="black").pack(pady=20)
        tk.Button(self.start_frame, text="Start Quiz", font=("Helvetica", 16), bg="white", fg="black", command=self.start_quiz).pack()

        self.quiz_frame = tk.Frame(root, bg="teal")

        self.question_box = tk.LabelFrame(self.quiz_frame, text="Question", font=("Helvetica", 14, "bold"), fg="black", bg="forest green", width=500, height=100, labelanchor="n")
        self.question_box.pack(pady=20)
        self.question_label = tk.Label(self.question_box, text="", font=("Helvetica", 14), bg="forest green", fg="black", wraplength=450, justify="center")
        self.question_label.pack(pady=10)

        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self.quiz_frame, text="", variable=self.selected, value=chr(65 + i),
                                font=("Helvetica", 12), bg="teal", fg="black", anchor="w", command=self.play_check_sfx)
            rb.pack(anchor="center", pady=5)
            self.radio_buttons.append(rb)

        self.feedback_label = tk.Label(self.quiz_frame, text="", font=("Helvetica", 12, "bold"), bg="teal", fg="black")
        self.feedback_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.quiz_frame, length=300, mode='determinate')
        self.progress.pack(pady=15)

        self.next_button = tk.Button(self.quiz_frame, text="Next", font=("Helvetica", 12), bg="white", fg="black", command=self.next_question)
        self.next_button.pack(pady=10)

        self.score_label = tk.Label(self.quiz_frame, text="", font=("Helvetica", 14), bg="teal", fg="black")
        self.score_label.pack(pady=10)

    def start_quiz(self):
        pygame.mixer.Sound("check.mp3").play()
        self.start_frame.pack_forget()
        self.quiz_frame.pack(expand=True)
        self.load_question()

    def play_check_sfx(self):
        pygame.mixer.Sound("check.mp3").play()

    def load_question(self):
        self.feedback_label.config(text="")
        if self.q_index < len(self.quizzes):
            question, choices, _ = self.quizzes[self.q_index]
            self.question_label.config(text=f"{question}")
            self.selected.set(None)
            for i, choice in enumerate(choices):
                self.radio_buttons[i].config(text=f"{chr(65 + i)}. {choice}", value=chr(65 + i))
            self.progress["value"] = (self.q_index / len(self.quizzes)) * 100
        else:
            self.show_score()

    def next_question(self):
        if not self.selected.get():
            messagebox.showwarning("No selection", "Please choose an answer before continuing.")
            return
        _, _, correct = self.quizzes[self.q_index]
        if self.selected.get() == correct:
            pygame.mixer.Sound("correct.mp3").play()
            self.feedback_label.config(text="Correct!", fg="white", bg="green")
            self.score += 1
        else:
            pygame.mixer.Sound("wrong.mp3").play()
            self.feedback_label.config(text=f"Wrong! Correct answer was {correct}", fg="white", bg="red")

        self.root.after(1000, self.advance_question)

    def advance_question(self):
        self.q_index += 1
        self.load_question()

    def show_score(self):
        self.progress["value"] = 100
        self.question_label.config(text="Quiz Complete")
        for rb in self.radio_buttons:
            rb.config(state="disabled")
        self.score_label.config(text=f"You scored {self.score} out of {len(self.quizzes)}")

        if self.score == len(self.quizzes):
            pygame.mixer.music.stop()
            pygame.mixer.music.load("perfect.mp3")
            pygame.mixer.music.play()
        elif self.score == 0:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("zero.mp3")
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.pause()
            pygame.mixer.music.load("pass.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            pygame.mixer.music.load("background.mp3")
            pygame.mixer.music.play(-1)

filename = "quiz_entries.txt"
quizzes = load_quizzes(filename)

if quizzes:
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')
    style.configure("TProgressbar", thickness=10, troughcolor="white", background="black", bordercolor="black")
    app = QuizApp(root, quizzes)
    root.mainloop()
else:
    print("No quizzes found in the file.")