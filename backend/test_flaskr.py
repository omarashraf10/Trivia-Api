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
        self.database_name = "trivia"
        #self.database_path = "trivia://{}/{}".format(
        #    'localhost:5432', self.database_name)
        data_base_user_name=os.environ['UserName']
        data_base_user_password=os.environ['Password']
        self.database_path ="postgresql://{}:{}@{}/{}".formatdata_base_user_name,data_base_user_password,"localhost:5432",self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }

         # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_paginate_questions(self):
        """Tests question pagination success"""
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_request_beyond_valid_page(self):
        """ Tests error if user tries to access nonexistent page """
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get("/categories/2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_invalid_category_id(self):
        """Test for invalid category id"""

        # request with invalid category id 1987
        response = self.client().get('/categories/jhfsdkj')
        data = json.loads(response.data)

        # Assertions to ensure 422 error is returned
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        question = Question(question="delete question", answer="new answer",
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)

        question = Question.query.get(question_id)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_with_invalid_id(self):
        response = self.client().delete('/questions/hhhhhh')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')   

    def test_create_question(self):
        """Tests question creation"""
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }

        # get questions before post. Create question, load response data
        # and get num questions after
        questions_before = len(Question.query.all())

        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        questions_after = len(Question.query.all())

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(questions_after, questions_before + 1)

    def test_422_create_question(self):
        """test failure of question creation error 400"""
        # get num of questions before post, create question without json data,
        # get num questions after
        questions_before = Question.query.all()

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)
        questions_after = Question.query.all()

        # check status code, false success message
        # and compare length before & after
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(questions_before) == len(questions_after))

    def test_search_question(self):
        """test success fo searchin questions"""
        # send post request with search term, load response data
        # new_search = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json={
            'searchTerm': 'palace'})
        data = json.loads(response.data)

        # check status code, success message,
        # that there are questions in the search results
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_questions(self):
        """test for no search results 404"""
        response = self.client().post('/questions/search', json={
            'searchTerm': ''})
        data = json.loads(response.data)

        # check status code, false success message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_category_questions(self):
        """test success of getting questions by categories"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        # check status code, success message,
        # num of questions and current category
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_category_questions(self):
        """test for 404 error with no questions from category"""
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        # check status code, false success message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quiz(self):
        """test success of playing quiz"""
        quiz_round = {'previous_questions': [], 'quiz_category': {
            'type': 'Geography', 'id': 15}}
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)

        # check status code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_422_get_quiz(self):
        """test 422 error if quiz game fails"""
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # check status code, false success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()