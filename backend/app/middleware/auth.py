from functools import wraps
from flask import request, jsonify, current_app
# import jwt # PyJWT or supabase-py can be used. For now, we will assume generic validation or just check presence.
# Real implementation would verify the JWT signature using Supabase's secret.

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # TODO: Validate token with Supabase or locally verify signature
        # try:
        #     data = jwt.decode(token, current_app.config['SUPABASE_KEY'], algorithms=["HS256"])
        # except:
        #     return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    
    return decorated
