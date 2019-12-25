"""questions.py"""

from PyInquirer import prompt, print_json


def yes_no_question(attribute, message):
    """Make a question about a feauture

    Args:
        attribute (str): The feature to be implemented.
        message (str): The question to ask.

    Return:
        O for N 1 for Y
    """

    questions = [
        {
            'type': 'confirm',
            'name': attribute,
            'message': message,
            'default': True
        }
    ]
    answers = prompt(questions)
   
    return answers[attribute]


def get_input(attribute, message):
    """Ask user for input"""

    questions = [
        {
            'type': 'input',
            'name': attribute,
            'message': message,
        }
    ]
    answers = prompt(questions)

    return answers[attribute]
