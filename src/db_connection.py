import sqlite3


# Configuración de la base de datos
def init_database():
    """Inicializar la base de datos SQLite con las tablas requeridas"""
    conn = sqlite3.connect("truco_game.db")
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL
        )
    """
    )

    # Tabla de partidas
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            players_count INTEGER NOT NULL,
            pica_pica_enabled INTEGER DEFAULT 1,
            pica_pica_end_points INTEGER NOT NULL,
            starting_dealer_id INTEGER,
            status TEXT DEFAULT 'en_progreso',
            FOREIGN KEY (starting_dealer_id) REFERENCES users (id)
        )
    """
    )

    # Tabla de jugadores por partida
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS match_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            team_id INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches (id),
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    """
    )

    # Tabla de posiciones de jugadores
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS player_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            player_id INTEGER,
            position INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches (id),
            FOREIGN KEY (player_id) REFERENCES users (id)
        )
    """
    )

    # Tabla de rondas
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            round_number INTEGER,
            round_type TEXT,
            dealer_position INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    """
    )

    # Tabla de equipos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # table de miembros de equipo
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            player_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (player_id) REFERENCES users (id)
        )
    """
    )

    # Tabla de puntajes por ronda
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS redondo_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            truco_winner_team_id INTEGER NULL,
            truco_points INTEGER DEFAULT 0,
            envido_winner_team_id INTEGER NULL,
            envido_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (round_id) REFERENCES rounds (id),
            FOREIGN KEY (truco_winner_team_id) REFERENCES teams (id),
            FOREIGN KEY (envido_winner_team_id) REFERENCES teams (id)
        )
    """
    )

    # tabla puntajes de pica-pica
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pica_pica_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_id INTEGER,
            sub_round INTEGER,
            truco_winner_id INTEGER,
            truco_points INTEGER DEFAULT 0,
            envido_winner_id INTEGER,
            envido_points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (round_id) REFERENCES rounds (id),
            FOREIGN KEY (truco_winner_id) REFERENCES users (id),
            FOREIGN KEY (envido_winner_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()
