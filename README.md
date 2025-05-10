# Dev Forum

A community forum for developers to discuss and share knowledge about various programming topics.

## Features

- User authentication (register, login, logout)
- User profiles with bio and activity history
- Categories for organizing discussions
- Topics and posts with comments
- Admin dashboard for managing the forum
- Responsive design for mobile and desktop
- Dark mode support
- Search functionality
- Markdown support for posts
- Pagination for topics and posts
- Caching for improved performance
- Rate limiting to prevent abuse

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, JavaScript, CSS
- **Database**: SQLite (can be easily changed to PostgreSQL or MySQL)
- **Caching**: Flask-Caching
- **Security**: Flask-Limiter, CSRF protection

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/dev-forum.git
   cd dev-forum
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Initial Setup

The application will automatically create an admin user with the following credentials:
- Username: admin
- Password: admin

It will also create some initial categories for discussions.

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates
- `static/`: Static files (CSS, JavaScript, images)
- `static/css/style.css`: Custom CSS styles
- `static/js/script.js`: Custom JavaScript

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add new feature'`)
5. Push to the branch (`git push origin feature-branch`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.