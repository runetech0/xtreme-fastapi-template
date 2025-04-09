# FastAPI Template

This is a general-purpose FastAPI template that provides a solid foundation for building RESTful APIs with features such as user management, authentication, and payment integration. The template includes pre-configured routes for handling common use cases, such as user settings, authentication, admin operations, and payment processing.

### Features:
- User Authentication and Registration
- User Profile and Settings Management
- Admin Dashboard and User Management
- Payment Processing Integration
- Modular and Extendable

### Endpoints Overview:

#### **Authentication Routes:**
- **POST `/auth/sign`**: Register a new user with email, password, and other details.
- **POST `/auth/login`**: Login a user with email and password. Returns an access token and refresh token.
- **POST `/auth/refresh-token`**: Refresh the access token using the provided refresh token.

#### **Admin Routes:**
- **POST `/admin/login`**: Admin login for accessing the admin dashboard.
- **GET `/admin/settings`**: Retrieve the configuration or settings for the admin panel.
- **GET `/admin/users`**: Get a list of all registered users in the app.
- **GET `/admin/users/{id}`**: Retrieve details for a specific user.
- **PUT `/admin/users/{id}`**: Update user details (like name, email, role).
- **DELETE `/admin/users/{id}`**: Delete a specific user from the system.
- **GET `/admin/stats`**: Get platform statistics such as total user count, active users, etc.
- **GET `/admin/logs`**: Fetch system logs including user actions and admin activity.
- **GET `/admin/roles`**: Get a list of all roles and their associated permissions.
- **POST `/admin/roles`**: Create a new role with specific permissions.
- **PUT `/admin/roles/{role_name}`**: Update an existing role's permissions.
- **DELETE `/admin/roles/{role_name}`**: Delete a role from the system.
- **GET `/admin/config`**: Retrieve the app configuration (app name, version, etc.).
- **PUT `/admin/config`**: Update the app configuration (such as app name, version).

#### **User Routes:**
- **GET `/user/settings`**: Retrieve the user’s settings (e.g., notifications preferences).
- **PUT `/user/settings`**: Update the user’s settings (e.g., email, password).
- **GET `/user/profile`**: Retrieve the user’s profile information.
- **PUT `/user/avatar`**: Upload or change the user’s profile picture.
- **GET `/user/notifications`**: Retrieve a list of notifications for the user.
- **POST `/user/notifications/{notification_id}/mark-as-read`**: Mark a notification as read.
- **GET `/user/activity-log`**: Retrieve the user’s activity log with recent actions.
- **POST `/user/delete`**: Delete or deactivate the user account (requires confirmation).

#### **Payment Routes:**
- **POST `/payments/create-invoice`**: Create a payment invoice.
- **POST `/payments/confirmation`**: Confirm the payment and process the invoice.

### Setup and Installation:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/fastapi-template.git

2. Install dependencies:

    ```bash
    pip install -r requirements.txt


3. Run the FastAPI app:
    ```bash
    uvicorn main:app --reload


4. Visit the auto-generated documentation at http://127.0.0.1:8000/docs to explore the available endpoints.


### Authentication:

*   **JWT tokens** are used for user authentication. The `/auth/login` endpoint will return an access token and a refresh token. Use the access token to authenticate API requests.
    

### Admin Dashboard:

*   Admin users can log in through `/admin/login` and access the `/admin` routes to manage users, view system logs, manage roles and permissions, and configure the app settings.
    

### Payment Integration:

*   The template includes routes for creating invoices and confirming payments, which can be integrated with any external payment gateway.
    

### Project Structure:

*   **`routes/`**: Contains the FastAPI app and all routes.

*   **`app/`**: Contains non routes code like database, enums, logger etc.
    
*   **`app/middlewares/`**: Custom middleware for handling response formatting, error handling, etc.
    
*   **`app/settings.py`**: Configuration file for settings like database connections, app name, and version.

*   **`models/`**: Pydantic models for request/response validation.
    
    

### Contributing:

Feel free to open issues or submit pull requests for improvements, new features, or bug fixes.




### Contact

Telegram: [@runetech](https://t.me/runetech)