from flask import Flask, redirect, request, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = "your_secret_key"
#app.config['SESSION_COOKIE_NAME'] = 'spotipy-session'

# Spotify API credentials
SPOTIPY_CLIENT_ID = '377e5bb50c4d43d0938abbafb4d6829d'
SPOTIPY_CLIENT_SECRET = '5687d169707347599c8722ce0198598c'
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# Scopes for accessing user data
SCOPE = "user-read-recently-played,user-read-private,user-top-read,playlist-modify-public,playlist-modify-private"

@app.route('/')
def index():
    return 'Hello, world!'

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET,
                            redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE)
    #session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('user_data'))

@app.route('/user_data')
def user_data():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    access_token = token_info['access_token']
    sp = Spotify(auth=access_token)
    user_data = sp.current_user()
    return f"User data: {user_data}"

if __name__ == '__main__':
    app.run(debug=True)