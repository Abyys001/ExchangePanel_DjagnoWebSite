# Pardis Exchange Panel

A professional Django-based exchange rate management system for administrators.

## Features

- **User Management**: Custom user roles (Superuser, Exchange Admin, Exchange Manager)
- **Category Management**: Organize currencies into categories (e.g., Tether, Bitcoin, etc.)
- **Price Type Management**: Define buy/sell operations within categories
- **Price Management**: Track current and historical prices with automatic history tracking
- **Responsive Design**: Modern, mobile-friendly interface
- **Security**: Comprehensive security measures and authentication
- **Logging**: Detailed logging for all operations

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Pardis_panel
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Copy `env_example.txt` to `.env`
   - Update the environment variables:
     ```env
     SECRET_KEY=your-secret-key-here
     DEBUG=True
     ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Admin User**
   ```bash
   python manage.py create_admin --username admin --email admin@example.com --password admin123 --role superuser
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Accessing the Application

- **Main Dashboard**: `http://localhost:8000/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Login**: `http://localhost:8000/accounts/login/`

### User Roles

1. **Superuser**: Full access to all features and admin panel
2. **Exchange Admin**: Can manage categories, price types, and prices
3. **Exchange Manager**: Limited access to price management

### Managing Categories

1. Navigate to "Categories" from the main menu
2. Click "Add New Category" to create a category
3. Define price types within the category (Buy/Sell operations)
4. Set base and target currencies for each price type

### Managing Prices

1. Go to "Prices" from the main menu
2. Select a category to edit prices
3. Update current prices for each price type
4. Historical changes are automatically tracked

## Project Structure

```
Pardis_panel/
├── Pardis_panel/          # Main Django project
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── pricing/               # Pricing app
│   ├── models.py         # Category, PriceType, Price models
│   ├── views.py          # Pricing views
│   ├── forms.py          # Pricing forms
│   ├── admin.py          # Admin configuration
│   └── templates/        # Pricing templates
├── users/                 # User management app
│   ├── models.py         # Custom User model
│   ├── views.py          # Authentication views
│   ├── forms.py          # User forms
│   └── middlewares.py    # Authentication middleware
├── pages/                 # Static pages
│   ├── templates/        # Base templates
│   └── static/           # Static files
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Security Features

- **Environment-based Configuration**: Sensitive settings via environment variables
- **Secure Headers**: XSS protection, content type sniffing prevention
- **HTTPS Enforcement**: Automatic SSL redirect in production
- **Authentication Middleware**: Custom login requirement for all pages
- **Input Validation**: Comprehensive form and model validation
- **Logging**: Security event logging

## Production Deployment

### Environment Variables

Set these environment variables in production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Static Files

```bash
python manage.py collectstatic
```

### Database

For production, consider using PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/pardis_panel
```

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout

### Categories
- `GET /pricing/categories/` - List all categories
- `POST /pricing/categories/create/` - Create new category
- `GET /pricing/categories/<id>/edit/` - Edit category
- `POST /pricing/categories/<id>/delete/` - Delete category

### Prices
- `GET /pricing/prices/` - List all prices
- `GET /pricing/categories/<slug>/prices/` - Edit category prices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.
