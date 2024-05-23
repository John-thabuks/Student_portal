from sqlalchemy.orm import backref
from config import bcrypt, db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

class Student(db.Model, SerializerMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    
    courses = db.relationship('Course', secondary='student_courses', backref=db.backref('students', lazy='dynamic'))
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', back_populates='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', back_populates='receiver')

    serialize_only = ("email", "username")

    @hybrid_property
    def password_hash(self):
        return self._password
    
    @password_hash.setter   
    def password_hash(self, user_password):
        new_password_hash = bcrypt.generate_password_hash(user_password.encode("utf-8"))
        self._password = new_password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode("utf-8"))

class Admin(db.Model, SerializerMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column(db.String(), nullable=False)
    
    courses = db.relationship('Course', secondary='admin_courses', backref=db.backref('admins', lazy='dynamic'))
    sent_messages = db.relationship('Message', foreign_keys='Message.admin_sender_id', back_populates='admin_sender')
    received_messages = db.relationship('Message', foreign_keys='Message.admin_receiver_id', back_populates='admin_receiver')

    serialize_only = ("email",)

    @hybrid_property
    def password_hash(self):
        return self._password
    
    @password_hash.setter   
    def password_hash(self, user_password):
        new_password_hash = bcrypt.generate_password_hash(user_password.encode("utf-8"))
        self._password = new_password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password, password.encode("utf-8"))

class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    thumbnail = db.Column(db.String(120), nullable=True)
    price = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    
    modules = db.relationship('Module', backref='course', lazy=True)    

    serialize_only = ("title", "description", "thumbnail", "price", "admin_id")

class Module(db.Model, SerializerMixin):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    media = db.Column(db.String(120), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    serialize_only = ("title", "media", "notes", "course_id")

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=True)
    admin_sender_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='CASCADE'), nullable=True)
    admin_receiver_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='CASCADE'), nullable=True)

    sender = db.relationship('Student', foreign_keys=[sender_id], back_populates='sent_messages')
    receiver = db.relationship('Student', foreign_keys=[receiver_id], back_populates='received_messages')
    admin_sender = db.relationship('Admin', foreign_keys=[admin_sender_id], back_populates='sent_messages')
    admin_receiver = db.relationship('Admin', foreign_keys=[admin_receiver_id], back_populates='received_messages')

    serialize_only = ("title", "content", "sender_id", "receiver_id", "admin_sender_id", "admin_receiver_id")

# Association table for Student-Course many-to-many relationship
student_courses = db.Table('student_courses',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

# Association table for Admin-Course many-to-many relationship
admin_courses = db.Table('admin_courses',
    db.Column('admin_id', db.Integer, db.ForeignKey('admins.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)
