from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text, Integer, ForeignKey

# You must use this pattern:
#   -> postgresql://user:password@localhost:5432/database_name
database_name = "trivia"
database_path = "postgresql://postgres:000000@{}/{}".format('localhost:5432', database_name)
db = SQLAlchemy()


def setup_db(app, db_p=database_path):
    """
    binds a flask application and a SQLAlchemy service
    """
    app.config["SQLALCHEMY_DATABASE_URI"] = db_p
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db.drop_all()
    db.create_all()


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(String(255))
    answer = Column(Text)
    difficulty = Column(Integer)

    category_id = Column(Integer, ForeignKey('categories.id'))

    def __init__(self, question, answer, difficulty):
        self.question = question
        self.answer = answer
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(255))

    # Suppose that OneCategory have a lot of question -> OneToMany
    questions = relationship("Question", backref="categories")

    def __init__(self, _type):
        self.type = _type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
