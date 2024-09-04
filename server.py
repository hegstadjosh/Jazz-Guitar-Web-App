
import os
import json
import pprint
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session
from werkzeug.security import check_password_hash, generate_password_hash

import music_methods as mm

tmpl_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.config.from_mapping(    
    SECRET_KEY='dev',
)

DATABASE_USERNAME = ""
DATABASE_PASSWRD = ""
DATABASE_HOST = ""
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/"


engine = create_engine(DATABASEURI)

conn = engine.connect()


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.before_request
def load_logged_in_user():
    user_id = session.get('id')

    if user_id is None:
        g.user = None
        g.playlists = None
    else:
        g.user = g.conn.execute(text("SELECT * FROM \"User\" WHERE user_id = :user_id"), {'user_id': user_id}).fetchone()
        g.playlists = g.conn.execute(text("SELECT * FROM playlist where user_id = :user_id"), {'user_id': user_id}).fetchall()




@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass

#
@app.route('/')
def index():       
    print(request.args)
    context = {'user': g.user, 'playlists': g.playlists}
    return render_template("index.html", **context)






"""

TODO: 
 1. survey to Create User profile with user info and provide recs
 2. create basic search engine 
 3. store songs in personal library 
 4. auto-generated chord diagrams
 5. tool to transpose to different keys

"""







@app.route('/songsearch', methods=['POST'])
def songsearch():
    name = request.form['name']
    print('name', name)
    name = name.lower().strip()
    params = {"new_name": name}

    try:
        songs = g.conn.execute(
            text('SELECT * FROM song WHERE LOWER(title) = :new_name'), params).fetchall()
        if name == "":
            songs = g.conn.execute(
                text('SELECT * FROM song'), params).fetchall()
        
        if g.user:
            playlists = g.conn.execute(text("SELECT * FROM playlist where user_id = :user_id"), {'user_id': session.get('id')}).fetchall()
            context = {'user': g.user, 'songs': songs, 'playlists': playlists }

        else:
            context = {'songs': songs}
        return render_template('index.html', **context)

    except Exception as e:
        print(f"An error occurred fetching songs: {e}")
        return redirect('/')

@app.route('/songview/<song_id>', methods=['GET'])
def songview(song_id): 
    
    try:
        transpose = int(request.args.get('transpose', 0))
        cursor = g.conn.execute(text("SELECT * FROM song WHERE song_id = :song_id"), {'song_id': song_id})
        song = cursor.fetchone()
        cursor = g.conn.execute(text("SELECT chord_name FROM chord NATURAL JOIN songchord WHERE song_id = :song_id"), {'song_id': song_id})
        chords = cursor.fetchall()
        transposed_chords = []

        for c in chords: 
            transposed_chords.append( mm.md.transpose_chord(c[0], transpose) )
        new_key = mm.md.transpose_chord(song[5], transpose)

        diagrams = mm.get_chord_diagrams(transposed_chords, '0-5')

        artist = g.conn.execute(text("SELECT * FROM Artist WHERE artist_id = :artist_id"), {'artist_id': song[1]}).fetchone()
        if song:
            print(song)
            context = {'song': song , 'chords': transposed_chords, 'diagrams': diagrams, 'transpose': transpose, 'key': new_key, 'artist': artist, 'description': song[7]}
            return render_template('songview.html', **context)
        else:
            return redirect('/')
    except Exception as e:
        print(f"An error occurred fetching the song: {e}")
        return redirect('/')


@app.route('/profile')
def profile():
    user_id = session.get('id')

    playlists = g.conn.execute(text("SELECT * FROM playlist where user_id = :user_id"), {'user_id': session.get('id')}).fetchall()
    playlist_songs = {}
    fav_artists_query = text("SELECT name FROM Artist a WHERE a.artist_id IN (SELECT artist_id FROM fav_artist WHERE user_id = :user_id)")
    fav_artists = g.conn.execute(fav_artists_query, {'user_id': user_id}).fetchall()

    for playlist in playlists:
        songs = g.conn.execute(text(
            "SELECT s.* FROM Song s JOIN contains c ON s.song_id = c.song_id WHERE c.name = :name"),
            {'name': playlist[0]}).fetchall()
        playlist_songs[playlist[0]] = songs

    context = {'user': g.user, 'fav_artists': fav_artists, 'playlists': playlists, 'playlist_songs': playlist_songs}
    return render_template('profile.html', **context)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/login', methods=['POST'])
def loginUser():
    if request.method == 'POST':
        name = request.form['uname']
        password = request.form['pwd']
        try:
            result = g.conn.execute(
                text("SELECT * FROM \"User\" WHERE name = :name"), {'name': name})
            print(result.keys())
            user = result.fetchone()
            print(user[0])
            print(user[5], password)

            if user is None:
                print('Incorrect username.')
            elif not check_password_hash(user[5], password):
                print('Incorrect password.')
            else:
                print(user)
                session.clear()
                session['id'] = user[0]
                return redirect('/')
        except Exception as e:
            print(f"An error occurred fetching user: {e}")

    return render_template('login.html')


@app.route('/add_favorite/<artist_id>', methods=['POST'])   
def add_favorite(artist_id):
    song_id = request.args.get('song_id')
    user_id = session.get('id')
    try:
        g.conn.execute(text("INSERT INTO fav_artist (user_id, artist_id) VALUES (:user_id, :artist_id)"), {'user_id': user_id, 'artist_id': artist_id})
        #g.conn.commit()
        print(f"inserted artist_id {artist_id} for user_id {user_id}")
        return redirect('/songview/' + song_id)
    except Exception as e:
        print(f"An error occurred adding the artist to favorites: {e}")
        return redirect('/songview/' + request.args.get('song_id'))

@app.route('/join', methods=['POST'])
def joinUser():
    params = {}
    params["name"] = request.form['uname']
    params["password"] = generate_password_hash(request.form['pwd'])
    params["age"] = request.form['age']
    params["key"] = json.dumps([request.form['key']])
    params["genre"] = json.dumps([request.form['genre']])

    try:
        g.conn.execute(text(
            "INSERT INTO \"User\" (name, password, age, favorite_keys, favorite_genres) VALUES (:name, :password, :age, :key, :genre)"), params)
        g.conn.commit()
        return redirect('/login')
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('join.html')


@app.route('/recs', methods=['POST'])
def recs():
    user_id = session.get('id')
    print('id', id)

    try:
        user_query = text("SELECT favorite_keys, favorite_genres FROM \"User\" WHERE user_id = :user_id")
        user_prefs = g.conn.execute(user_query, {'user_id': user_id}).fetchone()
        print("user_prefs", user_prefs[0][0], user_prefs[1][0])

        if user_prefs is None:
            print("User not found.")
            return redirect('/login')
        
        fav_artists_query = text("SELECT name FROM Artist a WHERE a.artist_id IN (SELECT artist_id FROM fav_artist WHERE user_id = :user_id)")
        fav_artists = g.conn.execute(fav_artists_query, {'user_id': user_id}).fetchall()

        songs_query = text("SELECT * FROM Song s WHERE artist_id IN (SELECT artist_id FROM fav_artist WHERE user_id = :user_id) OR ( key = :key AND rhythm = :genre)")
        songs = g.conn.execute(songs_query, {'user_id': user_id,'key': user_prefs[0][0], 'genre': user_prefs[1][0]}).fetchall()
        
        if not songs:
            songs_key = g.conn.execute(text("SELECT * FROM Song WHERE key = :key"), {'key': user_prefs[0][0]}).fetchall()
            songs_genre = g.conn.execute(text("SELECT * FROM Song WHERE rhythm = :genre"), {'genre': user_prefs[1][0]}).fetchall()
            songs = songs_key if songs_key else songs_genre 
        
        if not songs:
            songs = g.conn.execute(text("SELECT * FROM \"Song\" ORDER BY RANDOM() LIMIT 10")).fetchall()
        
        artists = []
        for song in songs:
            artist = g.conn.execute(text("SELECT * FROM Artist WHERE artist_id = :artist_id"), {'artist_id': song[1]}).fetchone()
            artists.append(artist)

        playlists = g.conn.execute(text("SELECT * FROM playlist where user_id = :user_id"), {'user_id': session.get('id')}).fetchall()
        playlist_songs = {}

        for playlist in playlists:
            mySongs = g.conn.execute(text(
                "SELECT s.* FROM Song s JOIN contains c ON s.song_id = c.song_id WHERE c.name = :name"),
                {'name': playlist[0]}).fetchall()
            playlist_songs[playlist[0]] = mySongs

        context = {'user': g.user, 'fav_artists':  fav_artists, 'playlists': playlists, 'playlist_songs': playlist_songs, 'songs': songs, 'artists': artists}
        
        return render_template('profile.html', **context)
    except Exception as e:
        print(f"An error occurred fetching songs: {e}")
        return redirect('/profile')



@app.route('/playlist', methods=['POST'])
def playlist():
    params = {}
    params["name"] = request.form['pname']
    params["user_id"] = session.get('id')
    params["description"] = request.form['description']
    print(params["name"], params["user_id"], params["description"])

    try:
        g.conn.execute(text(
            "INSERT INTO playlist (name, user_id, description) VALUES (:name, :user_id, :description)"), params)
        g.conn.commit()
        return redirect('/profile')
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('profile.html')


@app.route('/addSong', methods=['POST'])
def addSong():
    params = {}
    params["name"] = request.form['playlist']
    params["song_id"] = request.form['song_id']

    try:
        g.conn.execute(text(
            "INSERT INTO contains (name, song_id) VALUES (:name, :song_id)"), params)
        g.conn.commit()
        return redirect('/')
    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('index.html')





if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=4343, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

                python server.py

        Show the help text using:

                python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
