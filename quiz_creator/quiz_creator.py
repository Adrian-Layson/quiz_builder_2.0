print("=== WELCOME TO QUIZ BUILDER ===\n")

quizzes = []

while True:
    question = input("Enter your question: ")
    choices = []
    for i in range(4):
        choice = input(f"Choice {chr(65 + i)}: ")
        choices.append(choice)

    correct = input("Which one is correct? (A - D): ").upper()
    
    quiz = f"Q: {question}\n"
    letters = ["A", "B", "C", "D"]
    for i, choice in enumerate(choices):
        quiz += f"{letters[i]}. {choice}\n"
    quiz += f"Answer: {correct}\n\n"

    quizzes.append(quiz)

    again = input("Will you add another question? (y/n): ").lower()
    if again != 'y':
        print("\nExiting program...\n")
        break

with open("quiz_entries.txt", "a") as file:
    for q in quizzes:
        file.write(q)

print("Quiz saved to quiz_entries.txt")