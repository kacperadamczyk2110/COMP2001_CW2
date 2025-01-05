import requests
from sqlalchemy.exc import SQLAlchemyError
from database import engine, users_table

def authenticate_user(email, password):
    auth_api_url = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"
    response = requests.post(
        auth_api_url,
        json={"email": email, "password": password}
    )
    response_json = response.json()

    # Check if the response is a list containing 'Verified' and 'True'
    if isinstance(response_json, list) and 'Verified' in response_json and 'True' in response_json:
        try:
            with engine.connect() as connection:
                user = connection.execute(users_table.select().where(users_table.c.Email_address == email)).fetchone()
                if user:
                    user_details = {
                        "verified": True,
                        "Email": email,
                        "UserID": user[0]  # Assuming UserID is the first column
                    }
                    return user_details
                else:
                    raise ValueError("User not found in the database")
        except SQLAlchemyError as e:
            error_message = f"Database error: {str(e)}"
            print(error_message)
            raise Exception(error_message)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            print(error_message)
            raise Exception(error_message)

    return None

