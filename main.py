import pymysql
import hashlib
import json
from flask import Flask, request, render_template, redirect, url_for, flash, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'secret_key'


#==============================================================================#
# 会用到的 function 们                                                           #
#==============================================================================#

# 用于 /login 和 /register 页面
def is_password_valid(password):
    # 密码长度要求
    min_length = 6
    max_length = 20
    if len(password) < min_length or len(password) > max_length:
        return "Password length must be between 6 and 20 characters."

    # 密码字符类型要求
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    special_chars = '!@#$%^&*()-_=+[]{};:,.<>/?'
    has_special = any(char in special_chars for char in password)

    if not has_upper:
        return "Password must contain at least one uppercase letter."
    if not has_lower:
        return "Password must contain at least one lowercase letter."
    if not has_digit:
        return "Password must contain at least one digit."
    if not has_special:
        return f"Password must contain at least one special character: \n{special_chars}"

    # 密码符合所有要求
    return True


# 用于 /login 和 /register 页面
def encrypt_password(password):
    #print(f"Original password: {password}") 
    encrypted = hashlib.sha256(password.encode()).hexdigest()
    #print(f"Encrypted password: {encrypted}")
    return encrypted



# 用于 /login 页面
def validate_login(identifier, password):
    print(f"Attempting to validate login for {identifier}")
    
    try:
        encrypted_password = encrypt_password(password)
        print(f"Encrypted password for login: {encrypted_password}")
        conn = pymysql.connect(user='root', password='newroot', db='library')
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT UserID, Username FROM User WHERE (Username=%s OR Email=%s OR SSN=%s) AND Password=%s",
                (identifier, identifier, identifier, encrypted_password)
            )
            user_record = cursor.fetchone()
            print(f"User record found: {user_record}")

            if user_record:
                cursor.execute(
                    "SELECT UserID FROM Staff WHERE UserID=%s",
                    (user_record[0],)
                )
                staff_record = cursor.fetchone()
                print(f"Staff record found: {staff_record}")
                
                user_type = 'staff' if staff_record else 'reader'
                user_info = {
                    'user_id': user_record[0],
                    'username': user_record[1],
                    'user_type': user_type
                }

                if user_info:
                    print(f"Login successful for: {user_info}")
                else:
                    print("Login failed for identifier:", identifier)
                    
                return user_info

        print("User not found or password does not match.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        if conn:
            conn.close()

    return None



# 用于 /profile 页面
def get_user_info(user_id):
    try:
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            # 获取用户的个人信息
            cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
            user_info = cursor.fetchone()
            #print('main.py 103')

            if not user_info:
                return None

            # 获取用户借阅的书籍信息
            cursor.execute("""
                SELECT b.Title, b.Author, bh.BorrowDate
                FROM BookHistory bh
                INNER JOIN Copy c ON bh.CopyID = c.CopyID
                INNER JOIN Book b ON c.BookID = b.BookID
                WHERE bh.UserID = %s AND bh.ReturnDate IS NULL
            """, (user_id,))
            user_info['borrowed_books'] = cursor.fetchall()
            #print('main.py 117')

            # 获取用户的会议室预定信息
            cursor.execute("""
                SELECT sr.RoomNumber, rr.ReserveDate, rr.ReserveTimeStart, rr.ReserveTimeEnd
                FROM RoomReservation rr
                INNER JOIN StudyRoom sr ON rr.StudyRoomID = sr.StudyRoomID
                WHERE rr.UserID = %s AND rr.ReserveDate >= CURDATE()
            """, (user_id,))
            reservations_raw = cursor.fetchall()
            #print('main.py 127')
            #print(user_info)
            #print(reservations_raw)

            base_time = datetime(1900, 1, 1)  # 创建一个基准时间

            user_info['studyroom_reservations'] = [{
                'RoomNumber': reservation['RoomNumber'],
                'ReserveDate': reservation['ReserveDate'].strftime('%Y-%m-%d') if reservation['ReserveDate'] else None,
                'ReserveTimeStart': (base_time + reservation['ReserveTimeStart']).strftime('%H:%M:%S') if reservation['ReserveTimeStart'] else None,
                'ReserveTimeEnd': (base_time + reservation['ReserveTimeEnd']).strftime('%H:%M:%S') if reservation['ReserveTimeEnd'] else None,
            } for reservation in reservations_raw]

            # 将日期和时间转换为字符串格式，便于在 Jinja 模板中渲染
            #user_info['studyroom_reservations'] = [{
             #   'RoomNumber': reservation['RoomNumber'],
              #  'ReserveDate': reservation['ReserveDate'].strftime('%Y-%m-%d') if reservation['ReserveDate'] else None,
            # 'ReserveTimeStart': reservation['ReserveTimeStart'].strftime('%H:%M:%S') if reservation['ReserveTimeStart'] else None,
            #    'ReserveTimeEnd': reservation['ReserveTimeEnd'].strftime('%H:%M:%S') if reservation['ReserveTimeEnd'] else None,
           # } for reservation in reservations_raw]
            
            #print('main.py 136')
            #print(user_info)

            # 获取用户参与的活动信息
            cursor.execute("""
                SELECT e.EventName, e.DateAndTime, e.Location, e.Description
                FROM EventParticipate ep
                INNER JOIN Event e ON ep.EventID = e.EventID
                WHERE ep.UserID = %s
            """, (user_id,))
            user_info['events'] = cursor.fetchall()
            #print('main.py 146')
            

            # 如果用户是员工，获取员工详情
            cursor.execute("""
                SELECT EmployeeStartTime, JobTitle, Salary, Responsibility
                FROM Staff
                WHERE UserID = %s
            """, (user_id,))
            staff_info = cursor.fetchone()
            #print('main.py 156', staff_info)
            
            # 如果查询到员工信息，则添加到 user_info 字典中
            if staff_info:
                user_info['staff_info'] = staff_info
            #print('main.py 174', user_info)
            
        return user_info
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        if conn:
            conn.close()


            
# 用于 /study_room 页面
# 从数据库检索所有的会议室
def retrieve_study_rooms():
    rooms = []
    try:
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM StudyRoom")
            rooms = cursor.fetchall()
            
    except Exception as e:
        print(f"Database Error: {e}")
        
    finally:
        if conn:
            conn.close()
            
    return rooms



# 用于 /study_room 页面
# 根据日期检索所有会议室的预定情况
def get_reservations_for_date(date):
    reservations = []
    
    try:
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            # 执行查询特定日期预定情况的 SQL 语句
            cursor.execute("SELECT StudyRoomID, ReserveDate, ReserveTimeStart, ReserveTimeEnd, UserID FROM RoomReservation WHERE ReserveDate = %s", (date,))
            rows = cursor.fetchall()
            #print(rows)
            
            for row in rows:
                # 格式化日期和时间字段
                row['ReserveDate'] = row['ReserveDate'].strftime('%Y-%m-%d') if row['ReserveDate'] else None
                row['ReserveTimeStart'] = row['ReserveTimeStart'].strftime('%H:%M:%S') if row['ReserveTimeStart'] else None
                row['ReserveTimeEnd'] = row['ReserveTimeEnd'].strftime('%H:%M:%S') if row['ReserveTimeEnd'] else None
                
                reservations.append(row)
                
    except Exception as e:
        print(f"Database ERROR: {e}")
        
    finally:
        if conn:
            conn.close()
            
    return reservations


# 用于 /study_room 页面
# 创建一个新的会议室预定
def make_reservation(room_id, date, start_time, end_time, user_id):
    try:
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            # 执行创建新预定的 SQL 语句
            affected_rows = cursor.execute("""
                INSERT INTO RoomReservation 
                (StudyRoomID, ReserveDate, ReserveTimeStart, ReserveTimeEnd, UserID) 
                VALUES (%s, %s, %s, %s, %s)
            """, (room_id, date, start_time, end_time, user_id))
            conn.commit()
            
            if affected_rows == 0:
                # 如果没有行受影响，表示插入未成功执行
                print("No rows affected, reservation may not have been added.")
            else:
                return True
            
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()


            
# 用于 /study_room 页面
def generate_time_slots():
    start_time = datetime.strptime('08:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')
    time_slots = []
    
    while start_time < end_time:
        time_slots.append(start_time.strftime('%H:%M'))
        start_time += timedelta(minutes=30)
        
    return time_slots



# 用于 /study_room 页面
def get_user_from_session():
    user_id = session.get('user_id')
    
    if user_id is None:
        return None
    
    try:
        conn = pymysql.connect(
            user='root',
            password='newroot',
            db='library',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
        with conn.cursor() as cursor:
            # 执行查询，获取用户信息
            cursor.execute("SELECT * FROM User WHERE UserID = %s", (user_id,))
            user = cursor.fetchone()
            return user
        
    except Exception as e:
        print(f"Error getting user from session: {e}")
        return None
    
    finally:
        conn.close()


        
# 用于 /profile/edit 页面
# 更新密码的函数
def update_password(user_id, encrypted_password):
    try:
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4')
        with conn.cursor() as cursor:
            cursor.execute("UPDATE User SET Password=%s WHERE UserID=%s", (encrypted_password, user_id))
            conn.commit()
        return True
    
    except Exception as e:
        print(f"密码更新时发生错误: {e}")
        return False
    
    finally:
        if conn:
            conn.close()



            
#==============================================================================#
# main / login page                                                            #
#==============================================================================#
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        # validate_login现在会返回一个字典或者None
        user_info = validate_login(identifier, password)

        if user_info:  # 如果不是None，说明登录成功
            session['login'] = True
            session['user_id'] = user_info['user_id']
            session['username'] = user_info['username']
            session['user_type'] = user_info['user_type']

            # 根据用户类型重定向
            if session['user_type'] == 'staff':
                return redirect(url_for('staff_page'))
            else:
                return redirect(url_for('user_profile'))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect('/')

    return render_template('login.html')


#==============================================================================#
# regtister page                                                               #
#==============================================================================#
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form['user_type']
        username = request.form['username']
        ssn = request.form['ssn']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 检查密码是否符合要求
        password_check = is_password_valid(password)
        if password_check != True:
            flash(password_check)  # 显示具体的错误信息
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('The passwords entered twice do not match, please try again.')
            return redirect(url_for('register'))

        # 密码符合要求，进行加密
        encrypted_password = encrypt_password(password)

        conn = None 
        # 连接数据库，执行注册逻辑
        try:
            conn = pymysql.connect(user='root', password='newroot', db='library')
            with conn.cursor() as cursor:
                # 检查SSN是否已经存在
                cursor.execute("SELECT * FROM User WHERE SSN=%s", (ssn,))
                
                if cursor.fetchone() is not None:
                    flash('This SSN has been used.')
                    return redirect(url_for('register'))
                
                if len(ssn) != 9 or not ssn.isdigit():
                    flash('SSN must be a nine-digit number.')
                    return redirect(url_for('register'))

                # 检查email是否已经存在
                cursor.execute("SELECT * FROM User WHERE Email=%s", (email,))
                if cursor.fetchone() is not None:
                    flash('This email has been used.')
                    return redirect(url_for('register'))

                # 检查username是否已经存在
                cursor.execute("SELECT * FROM User WHERE Username=%s", (username,))
                if cursor.fetchone() is not None:
                    flash('The username already exists, please select a different username.')
                    return redirect(url_for('register'))

                register_time = datetime.now()

                # 插入User表的代码
                cursor.execute(
                    "INSERT INTO User (Username, SSN, Email, Password, Balance, BooksLimit, StudyRoomLimit, RegisterTime) VALUES (%s, %s, %s, %s, 50, 10, 5, %s)",
                    (username, ssn, email, encrypted_password, register_time)
                )

                if user_type == 'staff':
                    # 如果是员工，获取额外的员工信息
                    job_title = request.form['job_title']
                    salary = request.form['salary']
                    responsibility = request.form['responsibility']
                        
                    # 获取刚刚插入的User记录的UserID
                    cursor.execute("SELECT LAST_INSERT_ID();")
                    user_id = cursor.fetchone()[0]
                        
                    # 使用这个UserID来插入Staff表
                    cursor.execute(
                        "INSERT INTO Staff (UserID, EmployeeStarttime, JobTitle, Salary, Responsibility) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, register_time, job_title, salary, responsibility)
                    )

                conn.commit()
                flash('Registration is successful！')
                return redirect('/')
        
        except pymysql.MySQLError as e:
            print("Database error:", e)
            flash('Database error occurred. Please try again.')
            
        except Exception as e:
            print("General error:", e)
            flash('An unexpected error occurred. Please try again.')
            
        finally:
            if conn and conn.open: 
                conn.close()  

    return render_template('register.html',
                           user_types=['reader', 'staff'])

#==============================================================================#
# profile page                                                                 #
#==============================================================================#
@app.route('/profile')
def user_profile():
    print(session)
    if not session.get('login'):
        flash('Please log in to view your profile.')
        return redirect(url_for('login'))
    #print('login successfully')
    
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    #print('423 user_id: ', user_id)
    #print('424 user_info: ', user_info)
    
    
    if user_info:
        return render_template('profile.html', user_info=user_info)
    else:
        flash('User information is not available, please log back in.')
        return redirect(url_for('login'))

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    # 检查用户是否已登录
    if 'login' not in session or not session['login']:
        flash('请先登录。')
        return redirect(url_for('login'))

    # GET 请求，展示当前用户信息
    if request.method == 'GET':
        user_info = get_user_info(session['user_id'])
        return render_template('edit_profile.html', user_info=user_info)

    # POST 请求，处理用户信息的更新
    if request.method == 'POST':
        user_id = session['user_id']
        username = request.form.get('username')
        ssn = request.form.get('ssn')
        email = request.form.get('email')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        try:
            conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4')
            with conn.cursor() as cursor:
                update_fields = []
                params = []

                # 如果提供了新的用户名，更新用户名
                if username:
                    update_fields.append("Username = %s")
                    params.append(username)
                # 如果提供了新的社会保障号码，更新SSN
                #if ssn:
                 #   update_fields.append("SSN = %s")
                 #   params.append(ssn)
                 
                # 如果提供了新的邮箱，更新邮箱
                if email:
                    update_fields.append("Email = %s")
                    params.append(email)
                # 如果提供了新的密码，验证旧密码，更新密码
                if new_password:
                    password_validity = is_password_valid(new_password)
                    if password_validity is not True:
                        flash(password_validity)
                        return redirect(url_for('edit_profile'))
                    
                    # 验证旧密码是否正确
                    user_info = validate_login(session['username'], old_password)
                    if user_info or (email and user_info['email'] == email):
                        encrypted_password = encrypt_password(new_password)
                        update_fields.append("Password = %s")
                        params.append(encrypted_password)
                    else:
                        flash('The old password is wrong.')
                        return redirect(url_for('edit_profile'))

                # 构造更新语句
                if update_fields:
                    update_statement = "UPDATE User SET " + ", ".join(update_fields) + " WHERE UserID = %s"
                    params.append(user_id)
                    cursor.execute(update_statement, params)
                    conn.commit()
                    flash('Your profile has been successfully updated.')
                else:
                    flash('No new profile.')

        except Exception as e:
            flash(f"error: {e}")
            
        finally:
            if conn:
                conn.close()

        return redirect(url_for('edit_profile'))



#==============================================================================#
# staff page                                                                   #
# boroow books, book study rooms, manage events                                #
#==============================================================================#
@app.route('/staff')
def staff_page():
    if not session.get('login'):
        flash('Please log in to access the staff page.')
        return redirect('/') 

    user_type = session.get('user_type')
    if user_type != 'staff':
        flash('You do not have permission to view the staff page.')
        return redirect('/profile')  # 非员工重定向到个人资料页面

    return render_template('staff.html')

#==============================================================================#
# book page                                                                    #
# boroow and return books                                                      #
#==============================================================================#
@app.route('/books', methods=['GET', 'POST'])
def books():
    search_results = []  # 保存搜索结果
    message = ''  # 显示消息给用户
    all_available_copies = {}  # 所有可用副本的字典
    conn = None  # 数据库连接初始化

    try:
        # 创建数据库连接
        conn = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4')
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if request.method == 'POST':
            action = request.form.get('action')
            # 搜索请求
            if 'keyword' in request.form:
                # 默认搜索类型为标题
                search_type = request.form.get('search_type', 'title')
                keyword = request.form.get('keyword')

                # 执行搜索查询
                query = f"""
                SELECT b.BookID, b.Title, b.Author, b.Nation, b.Category, 
                       (b.Quantity - IFNULL(SUM(bh.BorrowDate IS NOT NULL AND bh.ReturnDate IS NULL), 0)) AS Available,
                       sh.Floor, sh.Row, sh.Shelf
                FROM Book b
                LEFT JOIN Copy c ON b.BookID = c.BookID
                LEFT JOIN BookHistory bh ON c.CopyID = bh.CopyID
                LEFT JOIN Shelf sh ON c.ShelfID = sh.ShelfID
                WHERE b.{search_type} LIKE %s 
                GROUP BY b.BookID
                """
                cursor.execute(query, ('%' + keyword + '%',))
                search_results = cursor.fetchall()

                # 查询每本书的所有副本状态
                for book in search_results:
                    cursor.execute("""
                    SELECT CopyID, Status FROM Copy WHERE BookID = %s
                    """, (book['BookID'],))
                    copies = cursor.fetchall()
                    all_available_copies[book['BookID']] = copies

            # 处理借书请求
            elif action == 'borrow':
                copyID = request.form.get('copyID')
                userID = request.form.get('userID')
                #print('499 copyID: ', copyID)
                #print('499 userID: ', userID)

                # 检查该副本是否可借
                cursor.execute("""
                SELECT Status FROM Copy WHERE CopyID = %s
                """, (copyID,))
                copy = cursor.fetchone()
                #print('507 copy:', copy)

                if copy and copy['Status'] == 'Available':
                    # 进行借书操作
                    cursor.execute("""
                    INSERT INTO BookHistory (CopyID, UserID, BorrowDate) 
                    VALUES (%s, %s, NOW())
                    """, (copyID, userID))
                    
                    # 更新副本状态为已借出
                    cursor.execute("""
                    UPDATE Copy SET Status = 'Borrowed' WHERE CopyID = %s
                    """, (copyID,))
                    
                    # 更新书籍数量
                    cursor.execute("""
                    UPDATE Book SET Quantity = Quantity - 1 WHERE BookID = 
                    (SELECT BookID FROM Copy WHERE CopyID = %s)
                    """, (copyID,))
                    
                    # 提交事务
                    conn.commit()
                    message = 'Book has been successfully borrowed.'
                else:
                    message = 'This copy is currently not available for borrowing.'

            # 处理还书请求
            elif action == 'return':
                copyID = request.form.get('copyID')
                userID = request.form.get('userID')

                # 更新BookHistory记录还书时间
                cursor.execute("""
                UPDATE BookHistory SET ReturnDate = NOW() 
                WHERE CopyID = %s AND UserID = %s AND ReturnDate IS NULL
                """, (copyID, userID))
                affected_rows = cursor.rowcount

                if affected_rows > 0:
                    # 如果有记录被更新，则更新副本状态和数量
                    cursor.execute("""
                    UPDATE Copy SET Status = 'Available' WHERE CopyID = %s
                    """, (copyID,))
                    
                    cursor.execute("""
                    UPDATE Book SET Quantity = Quantity + 1 WHERE BookID = 
                    (SELECT BookID FROM Copy WHERE CopyID = %s)
                    """, (copyID,))
                    conn.commit()
                    message = 'Book has been successfully returned.'
                else:
                    message = 'No matching borrow record found or book has already been returned.'

    except Exception as e:
        # 捕获异常，显示错误信息，并回滚数据库更改
        conn.rollback()
        message = f'ERROR: {e}'

    finally:
        if conn:
            conn.close()

    # 使用渲染模板显示结果和消息
    return render_template(
        'books.html', search_results=search_results,
        message=message, all_available_copies=all_available_copies)



#==============================================================================#
# study-room page                                                              #
# study room reservation                                                       #
#==============================================================================#
@app.route('/study_rooms', methods=['GET', 'POST'])
def study_rooms():
    rooms = retrieve_study_rooms()
    reservations = {}
    time_slots = generate_time_slots()
    current_date = datetime.now().date()
    current_time = datetime.now().time()

    # 假设user是从数据库或会话中检索的用户对象
    user = get_user_from_session()
    if user is None:
        # 用户未登录的情况
        flash('Please log in to reserve study rooms.')
        return redirect(url_for('login'))
    
    userReservationsLimit = user['StudyRoomLimit'] * 2

    # 默认选择的日期是当前日期
    selected_date = request.form.get('selected_date', str(current_date))
    
    if request.method == 'POST':
        print("Processing POST request")
        selected_room = request.form.get('selected_room')
        selected_time = request.form.get('selected_times')
        #print("selected room: ", selected_room) 
        #print("selected time: ", selected_time)
        
        # 检查selected_time是否存在
        if not selected_time:
            flash('Please select a time slot.')
            return redirect(url_for('study_rooms'))
        
        # 如果 selected_time 存在，确保它是一个有效的时间字符串
        try:
            end_time = (datetime.strptime(selected_time, '%H:%M') + timedelta(minutes=30)).time()
        except ValueError:
            flash('Invalid time format.')
            return redirect(url_for('study_rooms'))

        user_id = session.get('user_id')

        # 检查是否尝试预定过去的日期或时间
        try:
            date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
            time_obj = datetime.strptime(selected_time, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.')
            return redirect(url_for('study_rooms'))

        if date_obj < current_date or (date_obj == current_date and time_obj < current_time):
            flash('Cannot reserve a room for past dates or times.')
            return redirect(url_for('study_rooms'))

        #print(f"Room: {selected_room}, Date: {selected_date}, Time: {selected_time}")
        
        # 执行预定
        booking = make_reservation(selected_room, selected_date, selected_time, str(end_time), user_id)
        if booking:
            print("Reservation made successfully")
            flash('Reservation successful!')
        else:
            print("Reservation failed")
            flash('Failed to make a reservation.')

    # 如果是GET请求或者选择了一个日期来查看会议室的可用性
    reservations = get_reservations_for_date(selected_date)
    
    # 如果选择的日期是今天，则过滤掉已经过去的时间段
    #if selected_date == str(current_date):
    #    time_slots = [slot for slot in time_slots if slot >= current_time.strftime('%H:%M')]
    
    return render_template(
        'study_rooms.html',
        rooms=rooms,
        reservations=reservations,
        time_slots=time_slots,
        userReservationsLimit=userReservationsLimit,
        current_date=current_date,
        current_time=current_time
    )


    
#==============================================================================#
# events                                                                       #
# event management                                                             #
#==============================================================================#
@app.route('/events')
def events():
    # 建立数据库连接
    connection = pymysql.connect(
        user='root', password='newroot',
        db='library', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            # 获取所有事件信息
            sql_events = "SELECT EventID, EventName, DateAndTime, Location, Description, Host FROM Event;"
            cursor.execute(sql_events)
            events_info = cursor.fetchall()
            
            # 对于每一个事件，获取参与的用户数量和用户ID
            for event in events_info:
                sql_participants = """
                SELECT EventID, GROUP_CONCAT(UserID ORDER BY UserID ASC) as UserIDs 
                FROM EventParticipate WHERE EventID = %s GROUP BY EventID;
                """
                cursor.execute(sql_participants, (event['EventID'],))
                participants = cursor.fetchone()
                event['ParticipantCount'] = 0 if participants is None else len(participants['UserIDs'].split(','))
                event['UserIDs'] = '' if participants is None else participants['UserIDs']
    
    # 关闭数据库连接
    connection.close()
    
    # 渲染模板并传递事件信息
    return render_template('events.html', events=events_info)


@app.route('/join_event', methods=['POST'])
def join_event():
    user_id = request.form.get('user_id')
    event_id = request.form.get('event_id')
    
    # 创建数据库连接并执行插入操作
    connection = pymysql.connect(
        user='root', password='newroot',
        db='library', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
            # 尝试添加用户到活动参与表
            sql_join = """
            INSERT INTO EventParticipate (EventID, UserID) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE EventID=EventID;
            """
            
            try:
                cursor.execute(sql_join, (event_id, user_id))
                connection.commit()
            except pymysql.err.IntegrityError as e:
                #print("Database error:", e)
                flash('Database error occurred. Please try again.')
    
    # 关闭数据库连接
    connection.close()
    return redirect(url_for('events'))



@app.route('/leave_event', methods=['POST'])
def leave_event():
    user_id = request.form.get('user_id')
    event_id = request.form.get('event_id')
    
    # 创建数据库连接并执行删除操作
    connection = pymysql.connect(user='root', password='newroot', db='library', charset='utf8mb4')
    with connection:
        with connection.cursor() as cursor:
            # 从活动参与表中删除用户
            sql_leave = "DELETE FROM EventParticipate WHERE EventID = %s AND UserID = %s;"
            cursor.execute(sql_leave, (event_id, user_id))
            connection.commit()
    
    # 关闭数据库连接
    connection.close()
    return redirect(url_for('events'))


#==============================================================================#
# logout and jump to main/login page                                           #
#==============================================================================#
@app.route('/logout', methods=['POST'])
def logout():
    # 清除会话信息
    session.clear()
    flash('You have been logged out.')
    return redirect('/') 


if __name__ == '__main__':
    app.run(debug=True)

app.run(host='127.0.0.1', port=5000)
