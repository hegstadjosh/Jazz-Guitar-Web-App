# Music Database Web App

This web application is a music database system with features for user authentication, song search, playlist management, and chord visualization. 

We lost access to the project's PSQL database; it won't function as intended until this is replaced. 

## Features

- User registration and login
- Song search functionality
- Viewing song details with chord diagrams
- Creating and managing playlists
- User profile with favorite artists
- Song recommendations based on user preferences

## Technologies Used

- Python
- Flask
- SQLAlchemy
- PostgreSQL
- HTML/CSS 

## Setup

1. Install required Python packages:
   ```
   pip install Flask SQLAlchemy psycopg2-binary
   ```

2. Set up your PostgreSQL database and update the `DATABASEURI` in `server.py` with your credentials.

3. Run the server:
   ```
   python server.py
   ```

4. Access the application at `http://localhost:4343` in your web browser.

## Main Components

- `server.py`: Main Flask application file
- `music_objects.py`: Chord, ChordShape, Scale classes
- `music_data.py`: Musical data in data structures
- `music_methods.py`: Functions for music data control 
- `templates/`: HTML templates for the web pages


## Note

This project was created as part of a class assignment for Introduction to Databases (COMS4111) with Kenneth Ross. It demonstrates basic web development concepts and database interactions using Flask and SQLAlchemy. "music_*" files from https://github.com/hegstadjosh/Guitar-Trainer.

