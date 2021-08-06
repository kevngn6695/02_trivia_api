import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Method is for paginating number of questions
def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  pop_quizzes = [quiz.format() for quiz in questions]
  current_quiz = pop_quizzes[start:end]

  return current_quiz

# Create web app
def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # Set up CORS. Allow '*' for origins.
  CORS(app, resource={
    r"*/api/*": {"origins":"*"}
  })
  
  # CORS handlers
  @app.after_request
  def add_header_with_cors(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers.add('Access-Control-Allow-Methods', 'DELETE, GET, POST, PUT')
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers.add('Access-Control-Allow-Headers', headers)
    return response

#-------------------------------------------------------------------------------#
# View Categories (READ)
#-------------------------------------------------------------------------------#
  @app.route('/categories', methods=['GET'])
  def get_question_from_category_model():
    try:
      # Get info fropm Category model
      info = Category.query.order_by(Category.id).all()
      categories = {}

      # Loop through the Category type, which assigns to category dict with a specific id.
      for category in info:
        categories[category.id] = category.type
      
      # Return a successful notification to api
      return jsonify({
        'success': True,
        'status code': 200,
        'categories': categories
      })
    except:
      abort(405) # Handler for Method Not Allowed

#-------------------------------------------------------------------------------#
# View Questions (READ)
#-------------------------------------------------------------------------------#
  @app.route('/questions')
  def get_questions_from_question_model():
    # Get all of the questions with a specific id from Question model.
    questions = Question.query.order_by(Question.id).all()

    # Make pages
    current_quiz = paginate_questions(request, questions)

    # If number of page is different than 0, 
    # loop through the Category type assigning to category dict with a specific id.
    if len(current_quiz) != 0:
      info = Category.query.order_by(Category.id).all()
      categories = {}

      for category in info:
        categories[category.id] = category.type
    else:
      abort(404) # Handler for Nothing Found
    
    # Return a successful notification to api
    return jsonify({
      'success': True,
      'questions': current_quiz,
      'total_questions': Question.query.count(),
      'categories': categories,
      'current_category': None
    })

#-------------------------------------------------------------------------------#
# Delete Questions (DELETE)
#-------------------------------------------------------------------------------#
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    questions = Question.query.filter(Question.id == question_id).one_or_none()
    print(questions)
  
    try:
      questions.delete()

      # If number of page is different than 0, 
      # loop through the Category type assigning to category dict with a specific id.
      questions = Question.query.order_by(Question.id).all()
      current_quiz = paginate_questions(request, questions)

      info = Category.query.order_by(Category.id).all()
      categories = {}
      for category in info:
        categories[category.id] = category.type

    except:
      abort(400)

    if questions:
      return jsonify({
        'success': True,
        'questions': current_quiz,
        'total_questions': Question.query.count(),
        'categories': categories,
        'current_category': None
      })
    else:
      abort(404)

#-------------------------------------------------------------------------------#
# View Questions with a Single Category (READ)
#-------------------------------------------------------------------------------#
  @app.route('/categories/<int:id>/questions')
  def get_single_question_from_category_model(id):
    questions = Question.query.filter (Question.category == id).all()
    current_quiz =  paginate_questions(request, questions)
    if questions:
      try:
        # If number of page is different than 0, 
        # loop through the Category type assigning to category dict with a specific id.
        info = Category.query.order_by(Category.id).all()
        categories = {}
        for category in info:
          categories[category.id] = category.type
      except:
        abort(400) # Handler for bad request
    else:
      abort(404) # Handler for Nothing Found
    
    # Return successful notification to api
    return jsonify({
      'success': True,
      'questions': current_quiz,
      'total_questions': len(current_quiz),
      'current_category': id,
      'categories': categories
    })


#-------------------------------------------------------------------------------#
# Create Questions (CREATE)
#-------------------------------------------------------------------------------#
  
  @app.route('/questions/results', methods=['POST'])
  def create_question():
    info = request.get_json()
    question = info.get('question', None)
    answer = info.get('answer', None)
    category = info.get('category', None)
    difficulty = info.get('difficulty', None)
    
    try:
      if not info['answer'] and not info['question'] and not info['category'] and not info['difficulty']:
        abort(400)
      question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      question.insert()
      questions = Question.query.order_by(Question.id).all()
      paginate_questions(request, questions)

      return jsonify({
        'success': True,
        'question_id': question.id,
        'questions': info,
      }), 201
      
    except:
      abort(422)

#-------------------------------------------------------------------------------#
# Search Questions
#-------------------------------------------------------------------------------#
  @app.route('/questions/search', methods=['POST'])
  def search():
    search_term = request.get_json().get('searchTerm', None)

    if search_term:
      # If number of page is different than 0, 
      # loop through the Category type assigning to category dict with a specific id.
      questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
      current_quiz = paginate_questions(request, questions)

      info = Category.query.order_by(Category.id).all()
      categories = {}
      for category in info:
        categories[category.id] = category.type
    
      return jsonify({
        'success': True,
        'questions': current_quiz,
        'total_questions': len(questions.all()),
        'current_category': None
      })
      
#-------------------------------------------------------------------------------#
# Quiz Time
#-------------------------------------------------------------------------------#
  @app.route('/quizzes', methods=['POST'])
  def quiz_time():
    try:
        category = request.get_json()['quiz_category']['id']
        category = int(category)
        previous_questions = request.get_json()['previous_questions']
        num_prev_questions = len(previous_questions)
        if category != 0:
          questions = get_single_question_from_category_model(category).get_json()
        else:
          questions = get_questions_from_question_model().get_json()
        
        num_questions = len(questions['questions'])
        first_question = questions['questions'][0]

        pre_next_question_condition = questions['questions'][num_prev_questions]if num_questions > num_prev_questions else first_question

    except Exception as e:
        abort(400)
    except:
      if not category:
            abort(400)
    return jsonify({
      'quizCategory': 'ALL' if category == 0 else questions['categories'][str(category)],
      'categories': questions['categories'],
      'question': pre_next_question_condition,
      'success': True
    }), 200

#-------------------------------------------------------------------------------#
# Error Handler
#-------------------------------------------------------------------------------#
  # Handler for Bad Request
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message':'Bad request'
    }), 400

  # Handler for Nothing Found
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not Found Anything'
    }), 404

  # Handler for Method Not Allowed
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
    }), 405

  # Handler for Unprocessable Request
  @app.errorhandler(422)
  def not_processable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Request'
    }), 422

  # Handler for Interna Server Error
  @app.errorhandler(500)
  def not_allowed(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error'
    }), 500

  return app