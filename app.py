import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forum.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config['POSTS_PER_PAGE'] = 10
app.config['TOPICS_PER_PAGE'] = 20
# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
cache = Cache(app)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
# Custom Jinja2 filters
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        value = str(value)
        return Markup(value.replace('\n', '<br>'))
    return value

@app.template_filter('format_content')
def format_content(value):
    if not value:
        return value

    value = str(value)

    # Process code blocks
    import re
    # Updated pattern to be more flexible with whitespace and newlines
    pattern = r'```([\w-]*)\s*(.*?)\s*```'

    def replace_code_block(match):
        language = match.group(1).strip() or 'plaintext'
        code = match.group(2)
        # Preserve line breaks in the code
        code = code.replace('\r\n', '\n')  # Normalize line breaks
        # Escape HTML entities in the code
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre class="line-numbers"><code class="language-{language}">{code}</code></pre>'

    # Replace code blocks with properly formatted HTML
    processed_value = re.sub(pattern, replace_code_block, value, flags=re.DOTALL)

    # Apply nl2br to the rest of the content (outside code blocks)
    # We need to split by the pre tags and apply nl2br only to the parts outside
    parts = re.split(r'(<pre class="line-numbers"><code class="language-.*?">.*?</code></pre>)', processed_value, flags=re.DOTALL)
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Even parts are outside code blocks
            result.append(part.replace('\n', '<br>'))
        else:  # Odd parts are code blocks
            result.append(part)

    return Markup(''.join(result))
@app.template_filter('time_since')
def time_since(dt):
    now = datetime.utcnow()
    diff = now - dt
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"
# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text, nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    topics = db.relationship('Topic', backref='category', lazy='dynamic', cascade='all, delete-orphan')
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True)
    posts = db.relationship('Post', backref='topic', lazy='dynamic', cascade='all, delete-orphan')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False, index=True)
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False, index=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('sent_messages', lazy='dynamic'))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=db.backref('received_messages', lazy='dynamic'))
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Routes
@app.route('/')
def index():
    categories = Category.query.all()
    topic_count = Topic.query.count()
    user_count = User.query.count()
    return render_template('index.html', categories=categories, topic_count=topic_count, user_count=user_count)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Username already exists.')
            return redirect(url_for('register'))
        if email_exists:
            flash('Email already exists.')
            return redirect(url_for('register'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password')
        return redirect(url_for('login'))
    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('profile.html', user=user, posts=posts)
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio')
        current_user.bio = bio
        # Check if password change was requested
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if current_password and new_password and confirm_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.')
                return redirect(url_for('edit_profile'))
            if new_password != confirm_password:
                flash('New passwords do not match.')
                return redirect(url_for('edit_profile'))
            current_user.set_password(new_password)
            flash('Password updated successfully.')
        db.session.commit()
        flash('Profile updated successfully.')
        return redirect(url_for('profile', username=current_user.username))
    return render_template('edit_profile.html')
@app.route('/category/<int:category_id>')
@app.route('/category/<int:category_id>/page/<int:page>')
@cache.cached(timeout=60, query_string=True)
def category(category_id, page=1):
    category = Category.query.get_or_404(category_id)
    topics = Topic.query.filter_by(category_id=category_id).order_by(Topic.created_at.desc()).paginate(
        page=page, per_page=app.config['TOPICS_PER_PAGE'], error_out=False)
    return render_template('category.html', category=category, topics=topics)
@app.route('/topic/new/<int:category_id>', methods=['GET', 'POST'])
@login_required
def new_topic(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'GET':
        flash('Tip: To insert code, wrap your code in triple backticks with a language name, e.g. ```python for Python code.')
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        content = request.form.get('content')
        if not title or not content:
            flash('Title and content are required.')
            return redirect(url_for('new_topic', category_id=category_id))
        topic = Topic(title=title, description=description, category_id=category_id)
        db.session.add(topic)
        db.session.commit()
        post = Post(content=content, user_id=current_user.id, topic_id=topic.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('topic', topic_id=topic.id))
    return render_template('new_topic.html', category=category)
@app.route('/topic/<int:topic_id>')
@app.route('/topic/<int:topic_id>/page/<int:page>')
@cache.cached(timeout=30, query_string=True)
def topic(topic_id, page=1):
    topic = Topic.query.get_or_404(topic_id)
    posts = Post.query.filter_by(topic_id=topic_id).order_by(Post.created_at).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('topic.html', topic=topic, posts=posts)
@app.route('/post/new/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def new_post(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    if request.method == 'GET':
        flash('Tip: To insert code, wrap your code in triple backticks with a language name, e.g. ```python for Python code.')
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('Content is required.')
            return redirect(url_for('new_post', topic_id=topic_id))
        post = Post(content=content, user_id=current_user.id, topic_id=topic_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('topic', topic_id=topic_id))
    return render_template('new_post.html', topic=topic)
@app.route('/comment/new/<int:post_id>', methods=['POST'])
@login_required
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if not content:
        flash('Comment content is required.')
        return redirect(url_for('topic', topic_id=post.topic_id))
    comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
    db.session.add(comment)
    db.session.commit()

    # Check if request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON response for AJAX requests
        return {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'time_since': app.jinja_env.filters['time_since'](comment.created_at),
            'author': {
                'id': current_user.id,
                'username': current_user.username,
                'profile_url': url_for('profile', username=current_user.username)
            },
            'formatted_content': app.jinja_env.filters['format_content'](comment.content)
        }

    # Return normal redirect for non-AJAX requests
    return redirect(url_for('topic', topic_id=post.topic_id))
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return render_template('search.html', results=None)
    topics = Topic.query.filter(Topic.title.contains(query)).all()
    posts = Post.query.filter(Post.content.contains(query)).all()
    return render_template('search.html', query=query, topics=topics, posts=posts)
# Admin routes
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    users = User.query.all()
    categories = Category.query.all()
    topic_count = Topic.query.count()
    post_count = Post.query.count()
    return render_template('admin.html', users=users, categories=categories, topic_count=topic_count, post_count=post_count)
@app.route('/admin/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            flash('Category name is required.')
            return redirect(url_for('new_category'))
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully.')
        return redirect(url_for('admin'))
    return render_template('new_category.html')
# Initialize the database
with app.app_context():
    db.create_all()
    # Create admin user if it doesn't exist
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        # Create some initial categories
        categories = [
            Category(name='General Discussion', description='General topics related to development'),
            Category(name='Web Development', description='Discussions about web technologies'),
            Category(name='Mobile Development', description='Topics related to mobile app development'),
            Category(name='Data Science', description='Discussions about data science and machine learning'),
            Category(name='DevOps', description='Topics related to DevOps practices')
        ]
        db.session.add_all(categories)
        db.session.commit()
# Chat routes
@app.route('/messages')
@login_required
def messages():
    # Get all users that the current user has conversations with
    sent_to_users = db.session.query(User).join(Message, User.id == Message.recipient_id).filter(Message.sender_id == current_user.id).distinct().all()
    received_from_users = db.session.query(User).join(Message, User.id == Message.sender_id).filter(Message.recipient_id == current_user.id).distinct().all()

    # Combine the lists and remove duplicates
    conversation_users = list(set(sent_to_users + received_from_users))

    # Get the last message for each conversation
    conversations = []
    for user in conversation_users:
        # Get the last message between the current user and this user
        last_message = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.recipient_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.recipient_id == current_user.id))
        ).order_by(Message.created_at.desc()).first()

        # Count unread messages
        unread_count = Message.query.filter_by(
            sender_id=user.id, 
            recipient_id=current_user.id, 
            is_read=False
        ).count()

        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count
        })

    # Sort conversations by the timestamp of the last message
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)

    return render_template('messages.html', conversations=conversations)

@app.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def conversation(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                content=content,
                sender_id=current_user.id,
                recipient_id=user.id
            )
            db.session.add(message)
            db.session.commit()
            flash('Message sent.')
            return redirect(url_for('conversation', username=username))

    # Get all messages between the current user and the other user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == user.id)) |
        ((Message.sender_id == user.id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at).all()

    # Mark unread messages as read
    unread_messages = Message.query.filter_by(
        sender_id=user.id, 
        recipient_id=current_user.id, 
        is_read=False
    ).all()

    for message in unread_messages:
        message.is_read = True

    db.session.commit()

    return render_template('conversation.html', user=user, messages=messages)

@app.route('/messages/new/<username>', methods=['GET', 'POST'])
@login_required
def new_message(username):
    user = User.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                content=content,
                sender_id=current_user.id,
                recipient_id=user.id
            )
            db.session.add(message)
            db.session.commit()
            flash('Message sent.')
            return redirect(url_for('conversation', username=username))

    return render_template('new_message.html', user=user)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()  # Roll back the session in case of database errors
    return render_template('errors/500.html'), 500
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403
# Context processors
@app.context_processor
def utility_processor():
    def recent_topics(limit=5):
        return Topic.query.order_by(Topic.created_at.desc()).limit(limit).all()
    def recent_posts(limit=5):
        return Post.query.order_by(Post.created_at.desc()).limit(limit).all()
    def user_count():
        return User.query.count()
    def topic_count():
        return Topic.query.count()
    def post_count():
        return Post.query.count()
    def unread_messages_count():
        if current_user.is_authenticated:
            return Message.query.filter_by(
                recipient_id=current_user.id,
                is_read=False
            ).count()
        return 0
    return {
        'recent_topics': recent_topics,
        'recent_posts': recent_posts,
        'user_count': user_count,
        'topic_count': topic_count,
        'post_count': post_count,
        'unread_messages_count': unread_messages_count
    }
if __name__ == '__main__':
    app.run(debug=True)
