import pandas as pd
import sqlite3
import random
import os
from IPython.display import clear_output


class CommandNotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UserCommand:
    def __init__(self, length):
        self.allowed_commands = {
            "Action": ['next', 'previous', 'exit', 'another round'],
            "SubmitAnswer": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
            "JumpToQuestion": [f'to {i}' for i in range(1, length+1)]
        }

    def check_command_format(self, command):
        for command_type, commands in self.allowed_commands.items():
            if command.split(', ')[0] in commands:
                return command_type, command
        raise CommandNotFoundError('Invalid command: '+command)


class QuestionOverfit(UserCommand):

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.df_questions = None
        self.q_id = 1
        self.execute = {
            "Action": self.execute_action,
            "SubmitAnswer": self.execute_submit_answers,
            "JumpToQuestion": self.execute_jump_to_question
        }
        self.fitting = True
        self.parsed_sampled_qs = None

    def load_questions(self, db='GRE-Verbal'):
        """
        Connect to the database.

        Current version only support built-in database

        Parameters
        ----------
        db: str
            The built-in database name

        Returns
        -------

        """
        if db == 'GRE-Verbal':
            db_path = os.path.join(os.path.dirname(__file__), 'gre_verbal.db')
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.df_questions = pd.read_sql_query(
                "SELECT * FROM questions_choices_answers",
                self.conn)

        else:
            raise NotImplementedError("Custom built database currently not supported in pre-release version. Try: 'GRE-Verbal' to have a taste.")

        return self

    def sample(self, show: int = 10, difficulty: str = None):
        if difficulty is not None:
            filteredID = self.cursor.execute(
                """
                SELECT QuestionID 
                FROM questions_choices_answers
                WHERE Difficulty = (?)
                """,
                (difficulty,)
            )
        else:
            filteredID = self.cursor.execute(
                """
                SELECT QuestionID 
                FROM questions_choices_answers
                """)

        to_be_sampled = [ID[0] for ID in filteredID.fetchall()]
        random_sampled = random.sample(to_be_sampled, show)
        placeholders = ','.join(['?'] * len(random_sampled))
        sql_query = f"""
        SELECT * 
        FROM questions_choices_answers
        WHERE QuestionID IN ({placeholders})
        """

        result = self.cursor.execute(sql_query, random_sampled)
        sampled_questions = result.fetchall()

        return sampled_questions

    @staticmethod
    def parse_sampled_question(sampled_question):
        parsed = dict()
        tracker = 0
        for ID, question in enumerate(sampled_question):
            if tracker % 9 == 0:
                current_id = ID // 9
                questionID = question[0]
                sectionID = question[1]

                if questionID % 10 == 0:
                    subQuestionID = 10
                else:
                    subQuestionID = questionID % 10

                difficulty = question[2]
                questionText = question[3]

                parsed[current_id + 1] = {
                    "QuestionID": questionID,
                    "Section": sectionID,
                    "SubQuestionID": subQuestionID,
                    "Difficulty": difficulty,
                    "Question": questionText,
                    "Choices": {question[-3]: [i for i in question[-2:]]}
                }

                tracker += 1

            else:
                parsed[current_id + 1]["Choices"][question[-3]] = [i for i in question[-2:]]
                tracker += 1

        return parsed

    @staticmethod
    def display_question(question_label, question):
        show = f"""
        Question: {question_label}
        Sampled From: {question['Section']} - {question['SubQuestionID']} 
        Difficulty: {question['Difficulty']}

        Question: 
        {question['Question']}

        {'A: ' + question['Choices']['A'][0] if question['Choices']['A'][0] is not None else ''}
        {'B: ' + question['Choices']['B'][0] if question['Choices']['B'][0] is not None else ''}
        {'C: ' + question['Choices']['C'][0] if question['Choices']['C'][0] is not None else ''}
        {'D: ' + question['Choices']['D'][0] if question['Choices']['D'][0] is not None else ''}
        {'E: ' + question['Choices']['E'][0] if question['Choices']['E'][0] is not None else ''}
        {'F: ' + question['Choices']['F'][0] if question['Choices']['F'][0] is not None else ''}
        {'G: ' + question['Choices']['G'][0] if question['Choices']['G'][0] is not None else ''}
        {'H: ' + question['Choices']['H'][0] if question['Choices']['H'][0] is not None else ''}
        {'I: ' + question['Choices']['I'][0] if question['Choices']['I'][0] is not None else ''}
        """
        print(show, end='\r', flush=True)
        clear_output(wait=True)

    def execute_action(self, command):
        if command == 'next':
            self.q_id += 1
        elif command == 'previous':
            self.q_id -= 1
        elif command == 'exit':
            self.fitting = False
        elif command == 'another round':
            self.parsed_sampled_qs = self.parse_sampled_question(self.sample(show=int(input("Questions: ")),
                                                                             difficulty=input("Difficulty: "))
                                                                 )
        return self

    def execute_submit_answers(self, command):
        choices = self.parsed_sampled_qs[self.q_id]['Choices']
        correct = {label: value[0] for (label, value) in choices.items() if value[1] == "True"}

        correct_label = [i for i in correct.keys()]
        answered_label = command.split(', ')
        correct_label.sort()
        answered_label.sort()

        if len(answered_label) == len(correct_label):
            # start checking
            results = [answer == true for answer, true in zip(answered_label, correct_label)]
            if all(results):
                print("Fantastic! You fitted this one well!")
            else:
                for result, answer, true in zip(results, answered_label, correct_label):
                    if not result:
                        print(f"Wrong answer: {answer} ")
                        print(f"Correct answer: {true} - {correct.get(true)}")

        else:
            print(f"Re-submit! You should submit {len(correct_label)} answers!")

    def execute_jump_to_question(self, command):
        q_id = command.split(' ')[1]
        self.q_id = int(q_id)
        print(self.q_id)
        return self

    def fit(self, show: int = 10, difficulty: str = None):
        """
        Fit (practice) with a number of questions of specified difficulty level
        The user interacts by entering commands that are in allowed format.
        Please call `QuestionOverfit().allowed_commands()` to get a list of allowed commands.

        Parameters
        ----------
        show: int
            How many questions to practice with. The parameter determines how many questions to randomly
            sample without replacement from the question base
        difficulty: str
            The difficulty level of the questions.
            Possible choices are: easy, medium, hard

        """
        super().__init__(show)
        self.parsed_sampled_qs = self.parse_sampled_question(self.sample(show=show, difficulty=difficulty))

        while self.fitting:
            self.display_question(self.q_id, self.parsed_sampled_qs[self.q_id])

            try:
                command_type, command = self.check_command_format(input("Command: "))
                to_execute = self.execute.get(command_type)

                if to_execute:
                    to_execute(command)

            except CommandNotFoundError:
                print("Invalid command!")


if __name__ == '__main__':
    overfit = QuestionOverfit()
    overfit.load_questions()

    overfit.fit(show=20, difficulty='medium')

    overfit.conn.close()
