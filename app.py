from flask import Flask, render_template, request, redirect, url_for, session,flash
from datetime import datetime
import pymongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from user import users_collection, staff_collection, books_collection,members_collection
app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize the 'error' variable

    if request.method == 'POST':
        user_id = int(request.form['id'])
        password = request.form['password']

        user = users_collection.find_one({"id": user_id, "password": password})
        if user:
            session['user_id'] = str(user["_id"])
            flash("Login successful!", 'success')  
            if user["type"] == "admin":
                return redirect(url_for('admin_dashboard'))
            elif user["type"] == "staff":
                return redirect(url_for('staff_dashboard'))

            
    

        error = "Invalid credentials. Please try again."
        flash(error, 'danger')  

    return render_template('login.html', error=error)

    

# Route to add staff to the database
@app.route('/admin/modals/add_staff', methods=['POST'])
def add_staff():
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            qualification = request.form['qualification']
            experience = request.form['experience']
            skill_set = request.form['skill_set']
            grades = request.form['grades']
            contact_info = request.form['contact_info']
            role = request.form['role']
            staff_id = request.form['staff_id']
            password = request.form['password']

            # Check if staff with the same ID already exists
            existing_staff = staff_collection.find_one({"staff_id": staff_id.lower()})
            if existing_staff:
                flash("Staff with the same ID already exists!", 'danger')
                return redirect(url_for('admin_dashboard'))

            
        
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')


            # Insert data into the staff collection
            staff_data = {
                'qualification': qualification,
                'experience': experience,
                'skill_set': skill_set,
                'grades': grades,
                'contact_info': contact_info,
                'role': role,
                'staff_id': staff_id,
                'password': hashed_password  # Store hashed password
            }
            staff_id = staff_collection.insert_one(staff_data).inserted_id

            flash("Staff member added successfully!", 'success')
            return redirect(url_for('admin_dashboard'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('manage_staff'))

from datetime import datetime

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session:
    
        staff_count = staff_collection.count_documents({})
        book_count = books_collection.count_documents({})
        member_count = members_collection.count_documents({})

    
        current_month = datetime.now().strftime('%Y-%m')
        books_cataloged_current_month = books_collection.count_documents({
            "cataloging_date": {"$regex": f"^{current_month}"}
        })

        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        return render_template(
            'admin/admin_dashboard.html',
            username=user['username'],
            staff_count=staff_count,
            book_count=book_count,
            member_count=member_count,
            books_cataloged_current_month=books_cataloged_current_month
        )

    return redirect(url_for('login'))

@app.route('/staff_dashboard')
def staff_dashboard():
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        return f"Welcome, {user['username']} (Staff)!"

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/manage_staff')
def manage_staff():
    if 'user_id' in session:
        staff_data = staff_collection.find()  # Fetch all staff data from the collection
        return render_template('admin/staff.html', staff_data=staff_data)

    return redirect(url_for('login'))

@app.route('/admin/staff_list')
def staff_list():
    if 'user_id' in session:
        staff_data = staff_collection.find()  # Fetch all staff data from the collection
        return render_template('admin/staff_list.html', staff_data=staff_data)

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))

# Update staff route
@app.route('/update_staff/<string:staff_id>', methods=['POST'])
def update_staff(staff_id):
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            qualification = request.form['qualification']
            experience = request.form['experience']
            skill_set = request.form['skill_set']
            grades = request.form['grades']
            contact_info = request.form['contact_info']
            role = request.form['role']

            # Find the staff member by staff_id
            staff = staff_collection.find_one({"staff_id": staff_id})

            if staff:
                # Update staff information
                staff_collection.update_one(
                    {"staff_id": staff_id},
                    {
                        "$set": {
                            'qualification': qualification,
                            'experience': experience,
                            'skill_set': skill_set,
                            'grades': grades,
                            'contact_info': contact_info,
                            'role': role,
                        }
                    }
                )
                flash("Staff member updated successfully!", 'success')
                # Update staff count after adding a new staff
                staff_count = staff_collection.count_documents({})
                return redirect(url_for('manage_staff'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))

# Delete staff route
@app.route('/delete_staff/<string:staff_id>', methods=['POST'])
def delete_staff(staff_id):
    if 'user_id' in session:
        # Find the staff member by staff_id
        staff = staff_collection.find_one({"staff_id": staff_id})

        if staff:
            # Delete the staff member from the database
            staff_collection.delete_one({"staff_id": staff_id})
            flash("Staff member deleted successfully!", 'success')
            return redirect(url_for('manage_staff'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))
# Function to fetch books from the database

# Your existing route for managing books
@app.route('/admin/manage_books')
def manage_books():
    if 'user_id' in session:        
        # Fetch books data from the database
        #book_data = books_collection.find(),{'lending_info': 1, 'title': 1, 'author': 1, 'genre': 1, 'format': 1, 'cataloging_date': 1, 'cataloging_personnel': 1, 'reminder_config': 1, 'availability': 1})
        book_data = books_collection.find({}, {'lending_info': 1, 'title': 1, 'author': 1, 'genre': 1, 'format': 1, 'cataloging_date': 1, 'cataloging_personnel': 1, 'reminder_config': 1, 'availability': 1})


        
        
        return render_template('admin/manage_books.html', book_data= book_data)

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))
# Route to update a book
@app.route('/admin/update_book/<book_id>', methods=['POST'])
def update_book(book_id):
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            format = request.form['format']
            availability = request.form['availability']
            borrowing_limit = request.form.get('borrowing_limit', 10)

            
            almost_due = request.form['almost_due']
            past_due = request.form['past_due']
            overdue = request.form['overdue']

            # Update the book in the database
            books_collection.update_one(
                {'_id': ObjectId(book_id)},
                {
                    '$set': {
                        'title': title,
                        'author': author,
                        'genre': genre,
                        'format': format,
                        'availability': availability,
                        'borrowing_limit': int(borrowing_limit),
                        'reminder_config': {
                            'almost_due': int(almost_due),
                            'past_due': int(past_due),
                            'overdue': int(overdue),
                        },
                    }
                }
            )
            flash("Book updated successfully!", 'success')
            book_count = books_collection.count_documents({})
            return redirect(url_for('manage_books'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))

# Route to delete a book
@app.route('/admin/delete_book/<book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user_id' in session:
        # Delete the book from the database
        books_collection.delete_one({'_id': ObjectId(book_id)})
        flash("Book deleted successfully!", 'success')
        return redirect(url_for('manage_books'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))


 # Route for adding a book
@app.route('/admin/modals/add_book', methods=['POST'])
def add_book():
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            title = request.form['title']
            author = request.form['author']
            genre = request.form['genre']
            format = request.form['format']
            availability = request.form['availability']
            borrowing_limit = 10 

            # Reminder configuration
            reminder_config = {
                'almost_due': 3,
                'past_due': 1,
                'overdue': 7
            }
            # Cataloging information
            cataloging_date = request.form['cataloging_date']
            cataloging_personnel = request.form['cataloging_personnel']


            # Insert data into the books collection
            book_data = {
                'title': title,
                'author': author,
                'genre': genre,
                'format': format,
                'borrowing_limit': borrowing_limit,
                'reminder_config': reminder_config,
                'availability': availability,
                'cataloging_date': cataloging_date,
                'cataloging_personnel': cataloging_personnel,
                'lending_info': {
                'current_borrower': '',  
                'due_date': '',  # 
                'return_condition': ''  
            }}

            books_collection.insert_one(book_data)

            flash("Book added successfully!", 'success')
            return redirect(url_for('manage_books'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))


# Route for adding a member
@app.route('/admin/modals/add_member', methods=['POST'])
def add_member():
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            name = request.form['name']
            postal_address = request.form['postal_address']
            physical_address = request.form['physical_address']

            # Default values
            enrollment_date = datetime.now().strftime('%Y-%m-%d')
            status = 'active'
            overdue_occurrences = 0
            lending_preferences = ''

            # Insert data into the members collection
            member_data = {
                'name': name,
                'contact_details': {
                    'postal_address': postal_address,
                    'physical_address': physical_address
                },
                'enrollment_date': enrollment_date,
                'status': status,
                'lending_behavior': {
                     'transactions':[],
                    'overdue_occurrences': overdue_occurrences,
                    'lending_preferences': lending_preferences
                }
            }

            
            members_collection.insert_one(member_data)
            flash("Member added successfully!", 'success')
            return redirect(url_for('manage_member'))  
            

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))
# Your existing route for managing books
@app.route('/admin/manage_member')
def manage_member():
    if 'user_id' in session:        
        # Fetch books data from the database
     member_data = members_collection.find({}, {'lending_behavior': 1, 'name': 1, 'contact_details': 1, 'enrollment_date': 1, 'status': 1})

        
        
    return render_template('admin/manage_member.html', member_data= member_data)

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))

@app.route('/admin/update_member/<member_id>', methods=['POST', 'PUT'])
def update_member(member_id):
    if 'user_id' in session:
        if request.method in ['POST', 'PUT']:
            # Extract form data
            name = request.form['name']
            postal_address = request.form['postal_address']
            physical_address = request.form['physical_address']

            # Update member information in the database
            members_collection.update_one(
                {'_id': ObjectId(member_id)},
                {'$set': {
                    'name': name,
                    'contact_details.postal_address': postal_address,
                    'contact_details.physical_address': physical_address
                    # Update other fields as needed
                }}
            )
            member_count = members_collection.count_documents({})
            flash("Member updated successfully!", 'success')
            return redirect(url_for('manage_members'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))
@app.route('/admin/delete_member/<member_id>', methods=['POST', 'DELETE'])
def delete_member(member_id):
    if 'user_id' in session:
        if request.method == 'POST':
            # Delete the member from the database
            members_collection.delete_one({'_id': ObjectId(member_id)})

            flash("Member deleted successfully!", 'success')
            return redirect(url_for('manage_members'))

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))


from datetime import datetime, timedelta

@app.route('/admin/modals/borrow_book', methods=['POST'])
def borrow_book():
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            member_id = request.form['member_id']
            book_ids = request.form.getlist('book_ids')

            # Validate member and book information
            member = members_collection.find_one({'_id': ObjectId(member_id)})
            books = books_collection.find({'_id': {'$in': [ObjectId(book_id) for book_id in book_ids]}})

            if member and books:
                # Check if the books are available for borrowing
                available_books = [book for book in books if book['availability'] == 'available']

                if available_books:
                    # Update member's lending behavior
                    lending_behavior = member['lending_behavior']
                    lending_behavior['overdue_occurrences'] = 0  # Reset overdue occurrences
                    lending_behavior['lending_preferences'] = ''  # Update lending preferences

                    # Update member's transaction history
                    transaction = {
                        'transaction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'book_ids': book_ids,
                        'status': 'checked_out',
                        'due_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')  # Set due date (14 days from now)
                    }

                    members_collection.update_one(
                        {'_id': ObjectId(member_id)},
                        {
                            '$push': {'transactions': transaction},
                            '$set': {'lending_behavior': lending_behavior}
                        }
                    )

                    # Update book availability status
                    books_collection.update_many(
                        {'_id': {'$in': [ObjectId(book_id) for book_id in book_ids]}},
                        {'$set': {'availability': 'checked_out'}}
                    )

                    flash("Books checked out successfully!", 'success')
                    return redirect(url_for('manage_books'))  # Redirect to the manage books page

                else:
                    flash("Some or all selected books are not available for borrowing.", 'danger')

            else:
                flash("Invalid member or book information.", 'danger')

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))
@app.route('/admin/modals/return_book', methods=['POST'])
def return_book():
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            member_id = request.form['member_id']
            book_ids = request.form.getlist('book_ids')
            condition = request.form['condition']  

            # Validate member and book information
            member = members_collection.find_one({'_id': ObjectId(member_id)})
            books = books_collection.find({'_id': {'$in': [ObjectId(book_id) for book_id in book_ids]}})

            if member and books:
                # Update member's transaction history
                transaction = {
                    'transaction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'book_ids': book_ids,
                    'status': 'returned',
                    'condition': condition
                }

                members_collection.update_one(
                    {'_id': ObjectId(member_id)},
                    {'$push': {'transactions': transaction}}
                )

                # Update book availability status
                books_collection.update_many(
                    {'_id': {'$in': [ObjectId(book_id) for book_id in book_ids]}},
                    {'$set': {'availability': 'available'}}
                )

                flash("Books returned successfully!", 'success')
                return redirect(url_for('manage_books'))  

            else:
                flash("Invalid member or book information.", 'danger')

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))

from datetime import datetime 

@app.route('/lend_book/<book_id>', methods=['POST'])
def lend_book(book_id):
    if 'user_id' in session:
        if request.method == 'POST':
            # Extract form data
            membership_id = request.form['membership_id']
            due_date = request.form['due_date']
            return_condition = request.form.get('return_condition', '')

           
            books_collection.update_one(
                {'_id': ObjectId(book_id)},
                {
                    '$set': {
                        'lending_info': {
                            'current_borrower': membership_id,
                            'due_date': due_date,
                            'return_condition': return_condition
                        }
                    }
                }
            )

            
            members_collection.update_one(
                {'member_id': membership_id},
                {
                    '$set': {
                        'lending_behavior': {
                            'overdue_occurrences': 0,
                            'lending_preferences': ''
                        }
                    }
                }
            )

            flash("Book lending/returning processed successfully!", 'success')
            return redirect(url_for('manage_books'))  

    flash("Unauthorized access", 'danger')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
