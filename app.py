from database import engine, users_table, trails_table, features_table, trail_feature_table
from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy.exc import SQLAlchemyError
from auth import authenticate_user
from flask_cors import CORS
import base64


app = Flask(__name__)
CORS(app)

# Swagger UI setup
#-------------------------
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Trail Service API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Status check endpoint
#-------------------------
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"message": "Server is connected"})

# Home page setup
#-------------------------
@app.route('/')
def home():
    debug_info = {
        "Database Server": 'DIST-6-505.uopnet.plymouth.ac.uk',
        "Database Name": 'COMP2001_KAdamczyk',
        "Username": 'KAdamczyk'
    }
    return render_template('index.html', debug_info=debug_info)


# Fetch all users
#-------------------------
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        with engine.connect() as connection:
            result = connection.execute(users_table.select())
            users = []
            for row in result:
                user_dict = {
                    'UserID': row[0],
                    'Email_address': row[1],
                    'Role': row[2]
                }
                users.append(user_dict)
        return jsonify(users)
    except SQLAlchemyError as e:
        error_message = f"Database error: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return jsonify({"error": "An unexpected error occurred"}), 500


# Fetch all trails
#-------------------------
@app.route('/api/trails', methods=['GET'])
def get_trails():
    try:
        trails = []
        with engine.connect() as connection:
            result = connection.execute(trails_table.select())
            for row in result:
                trail_dict = {
                    'TrailID': row[0],
                    'TrailName': row[1],
                    'TrailSummary': row[2],
                    'TrailDescription': row[3],
                    'Difficulty': row[4],
                    'Location': row[5],
                    'Length': row[6],
                    'ElevationGain': row[7],
                    'RouteType': row[8],
                    'OwnerID': row[9],
                    'Pt1_Lat': row[10],
                    'Pt1_Long': row[11],
                    'Pt1_Desc': row[12],
                    'Pt2_Lat': row[13],
                    'Pt2_Long': row[14],
                    'Pt2_Desc': row[15]
                }
                # Fetch trail features using a separate connection
                with engine.connect() as feature_conn:
                    trail_features = feature_conn.execute(trail_feature_table.select().where(trail_feature_table.c.TrailID == row[0])).fetchall()
                    features = []
                    for feature_row in trail_features:
                        feature = feature_conn.execute(features_table.select().where(features_table.c.TrailFeatureID == feature_row[1])).fetchone()
                        feature_dict = {
                            'TrailFeatureID': feature_row[1],
                            'TrailFeature': feature[1]
                        }
                        features.append(feature_dict)
                trail_dict['Features'] = features
                trails.append(trail_dict)
        return jsonify(trails)
    except Exception as e:
        error_message = f"Error fetching trails: {str(e)}"
        print(error_message)  # Print the error message to the console
        return jsonify({"error": error_message}), 500



# Login endpoint
#-------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = authenticate_user(email, password)
    if user:
        return jsonify(user)
    return jsonify({"error": "Invalid credentials"}), 401

def requires_auth(f):
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return jsonify({"error": "Authorization required"}), 403
        try:
            auth_type, credentials = auth.split()
            if auth_type.lower() != 'basic':
                raise ValueError("Invalid authorization type")
            email, password = base64.b64decode(credentials).decode('utf-8').split(":")
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid authorization format"}), 400
        user = authenticate_user(email, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        return f(user, *args, **kwargs)
    decorated_function.__name__ = f.__name__  # Preserve the original function name
    return decorated_function

# Creating a trail
#-------------------------
@app.route('/api/trails', methods=['POST'])
@requires_auth
def create_trail(user):
    try:
        trail = request.json
        required_fields = [
            'TrailName', 'TrailSummary', 'TrailDescription', 'Difficulty', 'Location',
            'Length', 'ElevationGain', 'RouteType', 'Pt1_Lat', 'Pt1_Long', 'Pt1_Desc',
            'Pt2_Lat', 'Pt2_Long', 'Pt2_Desc', 'Features'
        ]

        missing_fields = [field for field in required_fields if field not in trail]
        if missing_fields:
            return jsonify({"error": f"Missing required trail data: {', '.join(missing_fields)}"}), 400

        with engine.connect() as connection:
            insert_stmt = trails_table.insert().values(
                TrailName=trail['TrailName'],
                TrailSummary=trail['TrailSummary'],
                TrailDescription=trail['TrailDescription'],
                Difficulty=trail['Difficulty'],
                Location=trail['Location'],
                Length=trail['Length'],
                ElevationGain=trail['ElevationGain'],
                RouteType=trail['RouteType'],
                OwnerID=user['UserID'],
                Pt1_Lat=trail['Pt1_Lat'],
                Pt1_Long=trail['Pt1_Long'],
                Pt1_Desc=trail['Pt1_Desc'],
                Pt2_Lat=trail['Pt2_Lat'],
                Pt2_Long=trail['Pt2_Long'],
                Pt2_Desc=trail['Pt2_Desc']
            )
            result = connection.execute(insert_stmt)
            connection.commit()

            trail_id = result.inserted_primary_key[0]
            for feature in trail['Features']:
                feature_result = connection.execute(
                    features_table.select().where(features_table.c.TrailFeatureID == feature['TrailFeatureID']))
                if not feature_result.fetchone():
                    feature_insert_stmt = features_table.insert().values(
                        TrailFeature=feature['TrailFeature']
                    )
                    feature_insert_result = connection.execute(feature_insert_stmt)
                    feature_id = feature_insert_result.inserted_primary_key[0]
                else:
                    feature_id = feature['TrailFeatureID']

                connection.execute(trail_feature_table.insert().values(
                    TrailID=trail_id,
                    TrailFeatureID=feature_id
                ))
            connection.commit()

        return jsonify(trail), 201
    except Exception as e:
        error_message = f"Error creating trail: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

# Fetch a specific trail by ID
#------------------------------
@app.route('/api/trails/<int:trail_id>', methods=['GET'])
def get_trail_by_id(trail_id):
    try:
        with engine.connect() as connection:
            trail = connection.execute(trails_table.select().where(trails_table.c.TrailID == trail_id)).fetchone()
            if trail is None:
                return jsonify({"error": "Trail not found"}), 404

            trail_dict = {
                'TrailID': trail[0],
                'TrailName': trail[1],
                'TrailSummary': trail[2],
                'TrailDescription': trail[3],
                'Difficulty': trail[4],
                'Location': trail[5],
                'Length': trail[6],
                'ElevationGain': trail[7],
                'RouteType': trail[8],
                'OwnerID': trail[9],
                'Pt1_Lat': trail[10],
                'Pt1_Long': trail[11],
                'Pt1_Desc': trail[12],
                'Pt2_Lat': trail[13],
                'Pt2_Long': trail[14],
                'Pt2_Desc': trail[15]
            }
            # Fetch trail features
            trail_features = connection.execute(trail_feature_table.select().where(trail_feature_table.c.TrailID == trail_id)).fetchall()
            features = []
            for feature_row in trail_features:
                feature = connection.execute(features_table.select().where(features_table.c.TrailFeatureID == feature_row[1])).fetchone()
                feature_dict = {
                    'TrailFeatureID': feature_row[1],
                    'TrailFeature': feature[1]
                }
                features.append(feature_dict)
            trail_dict['Features'] = features

        return jsonify(trail_dict)
    except Exception as e:
        error_message = f"Error fetching trail by ID: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500

# Update a trail
#-------------------------
@app.route('/api/trails/<int:trail_id>', methods=['PUT'])
@requires_auth
def update_trail(trail_id):
    try:
        trail_data = request.json
        required_fields = [
            'TrailName', 'TrailSummary', 'TrailDescription', 'Difficulty', 'Location',
            'Length', 'ElevationGain', 'RouteType', 'Pt1_Lat', 'Pt1_Long', 'Pt1_Desc',
            'Pt2_Lat', 'Pt2_Long', 'Pt2_Desc'
        ]

        missing_fields = [field for field in required_fields if field not in trail_data]
        if missing_fields:
            return jsonify({"error": f"Missing required trail data: {', '.join(missing_fields)}"}), 400

        with engine.connect() as connection:
            update_stmt = trails_table.update().where(trails_table.c.TrailID == trail_id).values(
                TrailName=trail_data.get('TrailName'),
                TrailSummary=trail_data.get('TrailSummary'),
                TrailDescription=trail_data.get('TrailDescription'),
                Difficulty=trail_data.get('Difficulty'),
                Location=trail_data.get('Location'),
                Length=trail_data.get('Length'),
                ElevationGain=trail_data.get('ElevationGain'),
                RouteType=trail_data.get('RouteType'),
                Pt1_Lat=trail_data.get('Pt1_Lat'),
                Pt1_Long=trail_data.get('Pt1_Long'),
                Pt1_Desc=trail_data.get('Pt1_Desc'),
                Pt2_Lat=trail_data.get('Pt2_Lat'),
                Pt2_Long=trail_data.get('Pt2_Long'),
                Pt2_Desc=trail_data.get('Pt2_Desc')
            )
            connection.execute(update_stmt)
            connection.commit()
        return jsonify({"message": "Trail updated successfully"}), 200
    except Exception as e:
        error_message = f"Error updating trail: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500


# Delete a trail
#-------------------------
@app.route('/api/trails/<int:trail_id>', methods=['DELETE'])
@requires_auth
def delete_trail(trail_id):
    try:
        with engine.connect() as connection:

            # Delete associated records in the TRAIL_FEATURE table
            delete_features_stmt = trail_feature_table.delete().where(trail_feature_table.c.TrailID == trail_id)
            connection.execute(delete_features_stmt)
            connection.commit()

            # Delete the trail record in the TRAIL table
            delete_trail_stmt = trails_table.delete().where(trails_table.c.TrailID == trail_id)
            connection.execute(delete_trail_stmt)
            connection.commit()

        return jsonify({"message": "Trail deleted successfully"}), 200
    except Exception as e:
        error_message = f"Error deleting trail: {str(e)}"
        print(error_message)  # Print the error message to the console
        return jsonify({"error": error_message}), 500


# Run the program
#-------------------------
if __name__ == '__main__':
    app.run(debug=True)
