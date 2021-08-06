import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        # If it is matched with these self-checks, it prints ok
        self.host = os.getenv('HOST')
        self.database_password = os.getenv('DATABASE_PASSWORD')
        self.database_username = os.getenv('DATABASE_USER')
        self.database_name = os.getenv('DATABASE_NAME')
        self.database_path = "postgres://{}:{}@{}/{}".format(self.database_username, self.database_password, self.host, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass



#--------------------------------------------------------------------
# Success Testing
#--------------------------------------------------------------------
    # Test for paginating questions
    def test_paginate_questions(self):
        responses = self.client().get('/questions')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(info['success'], True)
        self.assertTrue(info['categories'])
        self.assertTrue(len(info['questions']))

    # Test for viewing category
    def test_get_all_category(self):
        responses = self.client().get('/categories')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(info['success'], True)

    # Test for viewing all of the questions
    def test_get_all_questions(self):
        responses = self.client().get('/questions')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(info['success'], True)
        self.assertTrue(len(info['questions']))

    # Test for single question in a category
    def test_get_single_question_from_category_model(self):
        responses = self.client().get('/categories/1/questions')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(info['success'], True)
        self.assertEqual(info['current_category'], 1)
        self.assertTrue(len(info['questions']))

    # Test for posting questions.
    def test_questions_post(self):
        test_data = {
            'question': 'Who is the president of kenya',
            'answer': 'Uhuru kenyatta',
            'difficulty': 1,
            'category': 4
        }
        responses = self.client().post('/questions/results', json=test_data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 201)
        self.assertEqual(responses.get_json()['success'], True)
        self.assertTrue(len(responses.get_json()['questions']))

    # Test for deleting question
    def test_delete_questions(self):
        responses = self.client().delete('/questions/4')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 200)
        self.assertEqual(info['success'], True)
        self.assertTrue(len(info['questions']))
#--------------------------------------------------------------------
# Error Testing
#--------------------------------------------------------------------
    # Test for sending info
    def test_sending_info_on_valid_page_404(self):
        responses = self.client().get('/questions?page=1000')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 404)
        self.assertEqual(info['success'], False)
        self.assertEqual(info['message'],'Not Found Anything')

    def test_get_all_category_405(self):
        responses = self.client().post('/categories')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 405)
        self.assertEqual(info['success'], False)
        self.assertEqual(info['message'], 'Method Not Allowed')

    def test_questions_post_422(self):
        test_data = {
            'question': 'Who is the president of United States',
            'category': 4
        }
        responses = self.client().post('/questions/results', json=test_data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 422)
        self.assertEqual(responses.get_json()['success'], False)
        self.assertTrue(len(responses.get_json()['message']), 'bad request')
    
    def test_category_questions_404(self):
        responses = self.client().get('/categories/411/questions')
        info = json.loads(responses.data)

        # If it is matched with these self-checks, it prints ok
        self.assertEqual(responses.status_code, 404)
        self.assertEqual(info['success'], False)
        self.assertEqual(info['message'], 'Not Found Anything')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()