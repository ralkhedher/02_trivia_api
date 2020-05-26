import random

from flask_cors import CORS
from flask import Flask, request, abort, jsonify
from werkzeug.exceptions import NotFound, HTTPException, UnprocessableEntity, InternalServerError
from starter.backend.models import setup_db, Question, Category, database_path

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    """
    create and configure the app
    """
    app = Flask(__name__)
    setup_db(app, db_p=database_path)
    # TODO: Set up CORS. Allow '*' for origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    return app


app = create_app()


@app.after_request
def after_request(response):
    """
    TODO: Use the after_request decorator to set Access-Control-Allow
    """
    white_origin = ['*', 'http://localhost:5000', 'http://localhost:3000']
    if 'Origin' not in response.headers.keys():
        return response

    if request.headers['Origin'] in white_origin:
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
        response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'

    return response


@app.route('/questions', methods=['GET'])
def questions():
    """
    TODO: Create an endpoint to handle GET requests for all available questions.
    """
    data = {'questions': list(), 'other_information': dict()}
    page = request.args.get('page', 1, type=int)
    questions = Question.query.options().paginate(page, max_per_page=10)
    _categories = Category.query.all()

    data['other_information'] = {
        'number_of_total_questions': questions.total,
        'categories': [category.type for category in _categories]
    }

    for question in questions.items:
        data['questions'].append({
            'question': question.question,
            'current_category': question.categories.type,
        })

    if data is None:
        return jsonify({
            'success': True,
            'questions': data['questions'],
            'other_information': data['other_information'],
            'message': 'No questions exist'
        }), 404

    return jsonify({
        'success': True,
        'questions': data['questions'],
        'other_information': data['other_information'],
        'message': ''
    }), 200


@app.route('/categories', methods=['GET'])
def categories():
    """
    TODO: Create an endpoint to handle GET requests for all available categories.
    """
    data = {}
    _categories = Category.query.all()

    for _category in _categories:
        data[_category.id] = _category.type

    if data is None:
        return jsonify({
            'success': True,
            'categories': data,
            'message': 'No category exist'
        }), 404

    return jsonify({
        'success': True,
        'categories': data,
        'message': ''
    }), 200


@app.route('/question/<id>/', methods=['DELETE'])
def delete_question(id):
    """
    TODO: Create an endpoint to DELETE question using a question ID.
    """
    question = Question.query.filter_by(id=id).first()
    if question is None:
        return jsonify({
            'success': True,
            'message': 'question doesn\'t exit'
        }), 404

    question.delete()

    return jsonify({
        'success': True,
        'message': 'question was deleted'
    }), 200


@app.route('/questions', methods=['POST'])
def add_question():
    """
    TODO: Create an endpoint to POST a new question, which will require the question and answer text, category,
          and difficulty score
    """
    body = request.get_json()

    question = body.get('question', None)
    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)

    category_object = Category.query.filter_by(type=category).first()
    if category_object is None:
        return jsonify({
            'success': False,
            'inserted_question': None,
            'message': 'Category doesn\'n existe'
        }), 404

    question = Question(question=question, answer=answer, difficulty=difficulty)
    question.categories = category_object
    question.insert()

    return jsonify({
        'success': True,
        'inserted_question': {
            'id': question.id,
            'question': question.question,
            'answer': question.answer,
            'difficulty': question.difficulty,
            'category': category
        },
        'message': 'question was inserted in databases'
    }), 201


@app.route('/questions/<string>/search', methods=['GET'])
def search_question(string):
    """
    TODO: Create an endpoint to get questions based on a search term.
        It should return any questions for whom the search term  is a substring of the question.
    """
    data = []
    search = "%{}%".format(string)
    qs = Question.query.filter(Question.question.like(search)).all()
    if not qs:
        return jsonify({
            'success': True,
            'message': 'No question exit for pattern send'
        }), 404

    for question in qs:
        data.append({
            'question': question.question,
            'id': question.id,
        })

    return jsonify({
        'success': True,
        'questions': data,
        'message': ''
    }), 200


@app.route('/questions/category/<id>', methods=['GET'])
def question_for_category(id):
    """
    TODO: Create a GET endpoint to get questions based on category.
    """
    data = []
    qs = Question.query.filter_by(category_id=id).all()
    if not qs:
        return jsonify({
            'success': True,
            'message': 'No question exit for id {}'.format(id)
        }), 404

    for question in qs:
        data.append({
            'question': question.question,
            'id': question.id,
        })

    return jsonify({
        'success': True,
        'questions': data,
        'message': ''
    }), 200


@app.route('/questions/play_quiz', methods=['POST'])
def random_question_for_category():
    """
    TODO: Create a POST endpoint to get questions to play the quiz.
        This endpoint should take category and previous question parameters and return a random questions
        within the given category, if provided, and that is not one of the previous questions.
    """
    body = request.get_json()

    category_id = body.get('category_id', None)
    prev_question_id = body.get('prev_question_id', 0)

    qs = Question.query.filter(Question.category_id == category_id).filter(Question.id >= prev_question_id).all()
    if not qs:
        return jsonify({
            'success': True,
            'message': 'No question exit for id {}'.format(category_id)
        }), 404

    random_number = random.randrange(len(qs))

    return jsonify({
        'success': True,
        'questions': {
            'question': qs[random_number].question,
            'id': qs[random_number].id
        },
        'message': ''
    }), 200


@app.errorhandler(HTTPException)
def handle_bad_request(e):
    """
    Create error handlers for all expected errors for 400 http code error
    """
    return jsonify({
        'success': False,
        'message': 'Bad request {}'.format(e)
    }), 400


@app.errorhandler(NotFound)
def handle_not_found(e):
    """
    Create error handlers for all expected errors for 404 http code error
    """
    return jsonify({
        'success': False,
        'message': 'Not found {}'.format(e)
    }), 404


@app.errorhandler(UnprocessableEntity)
def handle_unprocessed_entity(e):
    """
    Create error handlers for all expected errors for 422 http code error
    """
    return jsonify({
        'success': False,
        'message': 'UnprocessedEntity {}'.format(e)
    }), 422


@app.errorhandler(InternalServerError)
def handle_internal_error(e):
    """
    Create error handlers for all expected errors for 500 http code error
    """
    return jsonify({
        'success': False,
        'message': 'Server error {}'.format(e)
    }), 500
