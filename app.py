from config import app, db,stripe

from flask import jsonify, request, make_response, redirect, url_for,send_file
from models import Course, Student, Admin, Module, Message
import jwt
from functools import wraps
import datetime
from sqlalchemy.exc import IntegrityError
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from sqlalchemy import and_
from sqlalchemy.orm import joinedload





# Define your token_required decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get("jwttoken")
        if not token:
            return make_response({"ERROR": "Where is your access token"}, 403)
        try:
            decode_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = Student.query.get(decode_data['id']) or Admin.query.get(decode_data['id'])
            if not current_user:
                return make_response({"ERROR": "User not found"}, 403)
        except Exception as e:
            return make_response({"ERROR": "Invalid access token"}, 403)
        return f(current_user, *args, **kwargs)
    return decorator



#We can get all courses
@app.route('/course', methods=['GET'])
# @token_required
def get_all_courses():
    try:
        courses = Course.query.all()
        # Serialize the courses to JSON
        
        course_data = [course.to_dict(only=('id', 'title', 'description', 'thumbnail', 'price')) for course in courses]
        return jsonify({'courses': course_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve courses', 'message': str(e)}), 500




# This is the routes for student login
@app.route('/student/login', methods=['POST'])
def student_login():
    user = request.get_json()    
    email = user["email"]
    password = user["password"]

    student = Student.query.filter_by(email=email).first()

    if student:
        if student.authenticate(password):
            token_generated = jwt.encode({
                "id": student.id, 
                "email": student.email,
                "user_type": "student",  # Include user_type property
                "exp": datetime.datetime.now() + datetime.timedelta(minutes=45)
                }, 
                app.config["SECRET_KEY"], algorithm="HS256")
            return make_response({"message": "Student login successful", "token": token_generated}, 200)
        else:
            return make_response({"message": "Incorrect student credentials"}, 403)
    else:
        return make_response({"message": "Student not found"}, 404)

# Admin Login Route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    user = request.get_json()    
    email = user["email"]
    password = user["password"]

    admin = Admin.query.filter_by(email=email).first()

    if admin:
        if admin.authenticate(password):
            token_generated = jwt.encode({
                "id": admin.id, 
                "email": admin.email,
                "user_type": "admin",  # Include user_type property
                "exp": datetime.datetime.now() + datetime.timedelta(minutes=45)
                }, 
                app.config["SECRET_KEY"], algorithm="HS256")
            return make_response({"message": "Admin login successful", "token": token_generated}, 200)
        else:
            return make_response({"message": "Incorrect admin credentials"}, 403)
    else:
        return make_response({"message": "Admin not found"}, 404)


#Below are Signup routes and views for Student and Admin
@app.route('/signup/student', methods=['POST'])
def signup_student():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': 'Email, password, and username are required!'}), 400

    email = data['email']
    password = data['password']
    username = data['username']

    if Student.query.filter_by(email=email).first():
        return jsonify({'error': 'Student already exists!'}), 409

    # Create a new student
    student = Student(email=email, username=username)
    student.password_hash = password  # This uses the setter method to hash the password

    # Save the student to the database
    db.session.add(student)
    db.session.commit()

    # Generate JWT token for the new student
    token = jwt.encode({'id': student.id, 'email': student.email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Student created successfully!', 'token': token}), 201

@app.route('/signup/admin', methods=['POST'])
def signup_admin():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required!'}), 400

    email = data['email']
    password = data['password']

    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'Admin already exists!'}), 409

    # Create a new admin
    admin = Admin(email=email)
    admin.password_hash = password  # This uses the setter method to hash the password

    # Save the admin to the database
    db.session.add(admin)
    db.session.commit()

    # Generate JWT token for the new admin
    token = jwt.encode({'id': admin.id, 'email': admin.email, 'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)},
                       app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'message': 'Admin created successfully!', 'token': token}), 201





# This is the Profile route for student
@app.route('/profile/student', methods=['GET', 'POST'])
@token_required
def student_profile(current_user):
    if request.method == 'GET':
        return jsonify({
            'username': current_user.username,
            'email': current_user.email
        }), 200

    elif request.method == 'POST':
        data = request.get_json()
        if 'username' in data:
            current_user.username = data['username']
        if 'password' in data:
            current_user.password_hash = data['password']
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully!'}), 200



# This is the Profile route for admin
@app.route('/profile/admin', methods=['GET', 'POST'])
@token_required
def admin_profile(current_user):
    if request.method == 'GET':
        try:
            admin = Admin.query.filter_by(id=current_user.id).first()  # Assuming Admin model has an 'id' attribute
            if not admin:
                return jsonify({'error': 'Admin not found!'}), 404

            return jsonify({
                'email': admin.email
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        data = request.get_json()
        if 'password' in data:
            try:
                admin = Admin.query.filter_by(id=current_user.id).first()  # Assuming Admin model has an 'id' attribute
                if not admin:
                    return jsonify({'error': 'Admin not found!'}), 404
                
                admin.password_hash = data['password']
                db.session.commit()

                return jsonify({'message': 'Profile updated successfully!'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Password not provided!'}), 400



# This will get all courses a current student is enrolled
@app.route('/courses/student', methods=['GET'])
@token_required
def get_student_courses(current_user):
    try:
        student_courses = current_user.courses
        course_data = [{'id': course.id, 'title': course.title, 'description': course.description, 'thumbnail': course.thumbnail, 'price': course.price} for course in student_courses]
        
        return jsonify({'courses': course_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve courses', 'message': str(e)}), 500



@app.route('/student/course/<int:course_id>', methods=['GET'])
@token_required
def get_student_course_details(current_user, course_id):
    try:
        # Check if the current user is a student
        if not isinstance(current_user, Student):
            return jsonify({'error': 'Unauthorized access'}), 403

        # Get the course details from the database
        course = Course.query.filter_by(id=course_id).first()

        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Get the admin details associated with the course
        admin_email = course.admins[0].email

        # Serialize the course details to JSON
        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'thumbnail': course.thumbnail,
            'admin_email': admin_email
        }

        return jsonify(course_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve course details', 'message': str(e)}), 500


@app.route('/student/course/<int:course_id>/module', methods=['GET'])
@token_required
def get_student_course_modules(current_user, course_id):
    try:
        # Check if the current user is a student
        if not isinstance(current_user, Student):
            return jsonify({'error': 'Unauthorized access'}), 403

        # Get the modules associated with the course from the database
        modules = Module.query.filter_by(course_id=course_id).all()

        # Serialize modules data
        modules_data = []
        for module in modules:
            module_data = {
                'id': module.id,
                'title': module.title,
                'media': module.media,
                'notes': module.notes
            }
            modules_data.append(module_data)

        return jsonify(modules_data), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve course modules', 'message': str(e)}), 500




# Lets define route for retrieving courses belonging to a certain admin
@app.route('/courses/admin', methods=['GET', 'POST', 'PATCH'])
@token_required
def admin_courses(current_user):
    if request.method == 'GET':
        # Check if the current user is an Admin
        admin = Admin.query.filter_by(id=current_user.id).first()  # Assuming Admin model has an 'id' attribute
        if not admin:
            return jsonify({'error': 'Admin not found!'}), 404
        print(admin.courses)
        # Get all courses associated with the logged-in admin
        courses = Course.query.filter(Course.admin_id == admin.id).options(joinedload(Course.modules)).all()

        # Serialize the courses
        courses_data = [
            {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "thumbnail": course.thumbnail,
                "price": course.price,
                "admin_id": course.admin_id,
                "modules": [
                    {
                        "id": module.id,
                        "title": module.title,
                        "media": module.media,
                        "notes": module.notes,
                        "course_id": module.course_id
                    }
                    for module in course.modules
                ]
            }
            for course in courses
        ]
        
        return jsonify({"courses": courses_data}), 200

    elif request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('title') or not data.get('description') or not data.get('price') or not data.get('modules'):
            return jsonify({'error': 'Incomplete course data!'}), 400

        # Extract course data
        title = data['title']
        description = data['description']
        thumbnail = data.get('thumbnail')
        price = data['price']

        # Create a new Course object
        new_course = Course(title=title, description=description, thumbnail=thumbnail, price=price, admin_id=current_user.id)
        
        # Add modules to the course
        for module_data in data['modules']:
            title = module_data.get('title')
            media = module_data.get('media')
            notes = module_data.get('notes')

            # Create a new Module object and add it to the course
            new_module = Module(title=title, media=media, notes=notes)
            new_course.modules.append(new_module)

        # Add the new course to the database session
        db.session.add(new_course)
        db.session.commit()

        return jsonify({'message': 'Course created successfully!', 'course_id': new_course.id}), 201

    elif request.method == 'PATCH':
        data = request.get_json()
        if not data or not data.get('course_id'):
            return jsonify({'error': 'Incomplete update data!'}), 400

        course_id = data['course_id']
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found!'}), 404

        # Update course information
        if 'title' in data:
            course.title = data['title']
        if 'description' in data:
            course.description = data['description']
        if 'thumbnail' in data:
            course.thumbnail = data['thumbnail']
        if 'price' in data:
            course.price = data['price']

        # Update modules information
        if 'modules' in data:
            for module_data in data['modules']:
                module_id = module_data.get('id')
                if module_id:
                    module = Module.query.get(module_id)
                    if module:
                        if 'title' in module_data:
                            module.title = module_data['title']
                        if 'media' in module_data:
                            module.media = module_data['media']
                        if 'notes' in module_data:
                            module.notes = module_data['notes']

        db.session.commit()

        return jsonify({'message': 'Course updated successfully!'}), 200
    


#Delete Course
@app.route('/courses/admin/<int:courseId>', methods=['DELETE'])
@token_required
def delete_admin_course(current_user, courseId):
    # Check if the current user has permission to delete the course
    if not current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Fetch the course using the courseId from the URL path parameter.
    course = Course.query.get(courseId)
    if not course:
        return jsonify({'error': 'Course not found!'}), 404


    try:
        # Delete associated modules first
        for module in course.modules:
            db.session.delete(module)

        # Delete the course and commit the transaction.
        db.session.delete(course)
        db.session.commit()

        return jsonify({'message': 'Course and associated modules deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while deleting the course and associated modules.'}), 500





#Messages for Admin and User
# @app.route('/messages/student', methods=['GET'])
# @token_required
# def student_messages(current_user):
#     if request.method == 'GET':
#         # Retrieve messages sent to the current student
#         messages_received = Message.query.filter_by(student_id=current_user.id).all()
#         message_data = [
#             {
#                 'id': message.id,
#                 'title': message.title,
#                 'content': message.content,
#                 'email': message.admin.email  # Include admin's email
#             }
#             for message in messages_received
#         ]
#         return jsonify({'messages_received': message_data}), 200


    # elif request.method == 'POST':
    #     data = request.get_json()
    #     if not data or not data.get('title') or not data.get('content'):
    #         return jsonify({'error': 'Incomplete message data!'}), 400
        
    #     # Create a new message from the student
    #     new_message = Message(title=data['title'], content=data['content'], student_id=current_user.id)
    #     db.session.add(new_message)
    #     db.session.commit()

    #     return jsonify({'message': 'Message created successfully!', 'message_id': new_message.id}), 201


# Route to send a message from student to admin
@app.route('/messages/student', methods=['POST'])
@token_required
def send_message_to_admin(current_user):
    try:
        data = request.json

        # Extract data from the request
        title = data.get('title')
        content = data.get('content')
        admin_id = data.get('admin_id')

        if not title or not content or not admin_id:
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the admin_id belongs to a valid admin
        admin = Admin.query.get(admin_id)
        if not admin:
            return jsonify({'message': 'Invalid admin ID'}), 400

        # Create a new message object
        message = Message(title=title, content=content, sender_id=current_user.id, receiver_id=admin_id)

        # Add the message to the database session
        db.session.add(message)
        db.session.commit()

        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500


# Route to fetch admins based on email substring
@app.route('/admins', methods=['GET'])
@token_required
def get_admins(current_user):
    try:
        # Get email substring from query parameter
        email = request.args.get('email', '')

        # Query database for admins whose email matches the substring
        matching_admins = Admin.query.filter(Admin.email.like(f'%{email}%')).all()

        # Serialize the matching admins
        serialized_admins = [{'id': admin.id, 'email': admin.email} for admin in matching_admins]

        # Return the serialized admins as JSON response
        return jsonify({'admins': serialized_admins}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

# Route to fetch Student based on email substring
@app.route('/studentsmail', methods=['GET'])
@token_required
def get_students_by_email_substring(current_user):
    try:
        # Get email substring from query parameter
        email = request.args.get('email', '')

        # Query database for students whose email matches the substring
        matching_students = Student.query.filter(Student.email.like(f'%{email}%')).all()

        # Serialize the matching students
        serialized_students = [{'id': student.id, 'email': student.email} for student in matching_students]

        # Return the serialized students as JSON response
        return jsonify({'students': serialized_students}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    


#Will display @ Inbox all the messeges for this Student
@app.route('/messages/from-admin', methods=['GET'])
@token_required
def messages_from_admin(current_user):
    try:
        # Ensure the current_user is a student
        if not isinstance(current_user, Student):
            return jsonify({'error': 'Unauthorized access'}), 403

        # Fetch all messages sent by admins to the current user (student)
        messages = Message.query.filter(
            and_(
                Message.receiver_id == current_user.id,
                Message.admin_sender_id.isnot(None)
            )
        ).all()

        if not messages:
            print(f'No messages found for student ID {current_user.id} from admins.')


        # Serialize messages
        messages_data = [{
            'id': message.id,
            'title': message.title,
            'content': message.content,
            'sender_id': message.admin_sender.id if message.admin_sender else None,
            'sender_email': message.admin_sender.email if message.admin_sender else None
        } for message in messages]

        return jsonify({'messages': messages_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500






#Messages in the Inbox of Admin
@app.route('/messages/admin', methods=['GET', 'POST'])
@token_required
def admin_messages(current_user):
    if request.method == 'GET':
        try:
            # Retrieve all messages sent to the logged-in Admin
            admin_received_messages = current_user.received_messages
            
            # Format message data
            messages_data = []
            for message in admin_received_messages:
                sender_name = message.sender.username if message.sender else "Unknown"
                messages_data.append({
                    'id': message.id,
                    'title': message.title,
                    'content': message.content,                    
                    'sender_name': sender_name
                })

            return jsonify({'messages': messages_data}), 200
        except Exception as e:
            return jsonify({'error': 'Failed to retrieve admin messages: ' + str(e)}), 500

    elif request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('title') or not data.get('content') or not data.get('email'):
            return jsonify({'error': 'Incomplete message data!'}), 400
        
        try:
            # Find the student by email
            student = Student.query.filter_by(email=data['email']).first()
            if not student:
                return jsonify({'error': 'Student not found!'}), 404
            
            # Create a new message from the admin
            new_message = Message(
                title=data['title'],
                content=data['content'],
                admin_sender_id=current_user.id,
                receiver_id=student.id
            )
            db.session.add(new_message)
            db.session.commit()

            return jsonify({'message': 'Message created successfully!', 'message_id': new_message.id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500




@app.route('/checkout/<int:course_id>', methods=['GET'])
@token_required
def checkout(current_user, course_id):
    # Query the course by ID
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Calculate the unit_amount, ensuring it meets the minimum requirements
    unit_amount = max(int(course.price * 100), 50)

    try:
        # Create a Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': course.title,
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',    
            # success_url=url_for('success', _external=True),
            # success_url=f'http://localhost:3000/success?course_title={course.title}&course_price={course.price}',
            success_url=f'http://localhost:3000/success?course_id={course_id}&course_title={course.title}&course_price={course.price}',
            cancel_url=url_for('cancel', _external=True),
        )

        current_user.courses.append(course)
        db.session.commit()

        return jsonify({'checkout_url': session.url}), 200
    except IntegrityError as e:
        db.session.rollback()  # Rollback the transaction
        return jsonify({'error': 'Student already enrolled in this course'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Function to generate PDF receipt
def generate_receipt(current_user, course_title, course_price):
    # Create a PDF file
    pdf_buffer = io.BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Insert logo thumbnail (assuming logo_image is the path to your logo image)
    p.drawImage("logo.png", 100, 800, width=100, height=100)

    # Draw other text
    p.drawString(100, 750, "Moringa School")
    p.drawString(100, 730, "Thank you for enrolling in our course.")
    p.drawString(100, 710, f"Student Name: {current_user.username}")
    p.drawString(100, 690, f"Email: {current_user.email}")
    p.drawString(100, 670, f"Course Title: {course_title}")
    p.drawString(100, 650, f"Course Price: ${course_price}")

    # Add date and time
    purchase_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p.drawString(100, 100, f"Purchase Date: {purchase_datetime}")

    # Save and return PDF buffer
    p.showPage()
    p.save()
    pdf_buffer.seek(0)
    return pdf_buffer


@app.route('/success')
@token_required
def success(current_user):
    course_title = request.args.get('course_title')
    course_price = request.args.get('course_price')
    course_id = request.args.get('course_id') 

    # Generate PDF receipt
    pdf_buffer = generate_receipt(current_user, course_title, course_price)

    # Create response with PDF attachment
    response = make_response(send_file(pdf_buffer, as_attachment=True, download_name='course_receipt.pdf', mimetype='application/pdf'))
    response.headers['Content-Disposition'] = 'attachment; filename=course_receipt.pdf'
    return response





@app.route('/cancel')
def cancel():
    return jsonify({"message": "Purchase canceled"})




if __name__ == '__main__':
    app.run(port=5000, debug=True)
