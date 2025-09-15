import re
import json

# Input text
quiz_data = {
    "text": "*Quiz on Mathematics\n\nQuestions:\n\n1. What is the square root of 144?\n2. Solve for x: 5x + 10 = 25\n3. Find the area of a triangle with a base of 10 cm and a height of 8 cm.\n4. What is the probability of rolling a 6 on a standard six-sided die?\n5. Simplify the expression: (3x + 5)(x - 2)\n6. Find the volume of a sphere with a radius of 5 cm.\n7. Convert 25% to a decimal.\n8. What is the equation of a line with a slope of 2 and a y-intercept of 3?\n9. Solve for y: 2y - 5 = 11\n10. What is the value of the integral of x^2 from 0 to 2?\n\nAnswers:*\n\n1. 12\n2. x = 3\n3. 40 cm\u00b2\n4. 1/6\n5. 3x^2 - x - 10\n6. 523.6 cm\u00b3\n7. 0.25\n8. y = 2x + 3\n9. y = 8\n10. 8/3"
}

# Extract the text
text = quiz_data["text"]

# Use regex to extract the questions
questions_pattern = r"\d+\. .*?(?=\n\d+\.|\nAnswers:)"
questions = re.findall(questions_pattern, text, re.DOTALL)
print(questions)
# Clean and format the questions
questions = [q.strip() for q in questions]


# Output the questions
print("Extracted Questions:")
for question in questions:
    print(question)
