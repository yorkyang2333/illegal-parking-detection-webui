from flask import Blueprint, request, jsonify, session
from models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate input
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'error': '用户名、邮箱和密码都是必填项'}), 400

        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400

        if len(password) < 6:
            return jsonify({'error': '密码长度至少为6位'}), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': '注册成功',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': '注册失败，请稍后重试'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    try:
        data = request.get_json()

        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)

        if not username or not password:
            return jsonify({'error': '用户名和密码都是必填项'}), 400

        # Find user
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401

        if not user.is_active:
            return jsonify({'error': '账户已被禁用'}), 403

        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        
        # Set session to permanent if remember me is checked
        if remember_me:
            session.permanent = True
        else:
            session.permanent = False

        return jsonify({
            'message': '登录成功',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': '登录失败，请稍后重试'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user"""
    session.clear()
    return jsonify({'message': '登出成功'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user info"""
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)

        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 404

        return jsonify({'user': user.to_dict()}), 200

    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({'error': '获取用户信息失败'}), 500
