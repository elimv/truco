import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class TrucoGame:
    def __init__(self):
        self.conn = sqlite3.connect("truco_game.db")
        self.conn.row_factory = sqlite3.Row

    def add_user(self, nickname: str) -> bool:
        """Agregar un nuevo usuario"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (nickname) VALUES (?)", (nickname,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_users(self) -> List[Dict]:
        """Obtener todos los usuarios"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY nickname")
        return [dict(row) for row in cursor.fetchall()]

    def generate_match_name(self, player_ids: List[int]) -> str:
        """Generar nombre automático para la partida"""
        cursor = self.conn.cursor()

        # Obtener iniciales de los jugadores
        placeholders = ",".join(["?" for _ in player_ids])
        cursor.execute(
            f"SELECT nickname FROM users WHERE id IN ({placeholders})", player_ids
        )
        nicknames = [row[0] for row in cursor.fetchall()]
        initials = "".join([nick[0].upper() for nick in nicknames])

        # Obtener fecha actual
        today = datetime.now().strftime("%d%m")

        # Contar partidas del día
        today_start = datetime.now().strftime("%Y-%m-%d 00:00:00")
        cursor.execute(
            "SELECT COUNT(*) FROM matches WHERE created_at >= ?", (today_start,)
        )
        daily_counter = cursor.fetchone()[0] + 1

        return f"{today}-{initials}-{daily_counter:02d}"

    def create_match(
        self,
        players_count: int,
        pica_pica_end_points: int,
        player_ids: List[int],
        starting_dealer_id: int,
        team_ids: List[int] = None,
    ) -> int:
        """Crear una nueva partida"""
        cursor = self.conn.cursor()

        # Generar nombre automático
        match_name = self.generate_match_name(player_ids)

        # Crear partida
        cursor.execute(
            """
            INSERT INTO matches (name, players_count, pica_pica_end_points, starting_dealer_id)
            VALUES (?, ?, ?, ?)
        """,
            (match_name, players_count, pica_pica_end_points, starting_dealer_id),
        )

        match_id = cursor.lastrowid

        # Asignar equipos a la partida si se proporcionan
        if team_ids:
            self.assign_teams_to_match(match_id, team_ids)

        # Agregar jugadores con posiciones
        for i, player_id in enumerate(player_ids):
            cursor.execute(
                """
                INSERT INTO player_positions (match_id, player_id, position)
                VALUES (?, ?, ?)
            """,
                (match_id, player_id, i),
            )

        self.conn.commit()
        return match_id

    def get_match_teams(self, match_id: int) -> List[Dict]:
        """Obtener equipos de una partida"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT team_id FROM match_teams WHERE match_id = ?", (match_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_match_players(self, match_id: int) -> List[Dict]:
        """Obtener jugadores de una partida con sus posiciones y equipos"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT pp.player_id, pp.position, u.nickname
            FROM player_positions pp
            JOIN users u ON pp.player_id = u.id
            WHERE pp.match_id = ?
            ORDER BY pp.position
        """,
            (match_id,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_match_info(self, match_id: int) -> Dict:
        """Obtener información de la partida"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(f"No se encontró la partida con ID {match_id}")
        return dict(result)

    def get_teams(self, match_id: int) -> List[Dict]:
        """Obtener equipos de una partida"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM teams WHERE match_id = ?", (match_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_round(self, match_id: int, round_type: str, dealer_position: int) -> int:
        """Agregar una nueva ronda"""
        cursor = self.conn.cursor()

        # Obtener número de ronda actual
        cursor.execute(
            "SELECT MAX(round_number) FROM rounds WHERE match_id = ?", (match_id,)
        )
        result = cursor.fetchone()[0]
        round_number = (result or 0) + 1

        cursor.execute(
            """
            INSERT INTO rounds (match_id, round_number, round_type, dealer_position)
            VALUES (?, ?, ?, ?)
        """,
            (match_id, round_number, round_type, dealer_position),
        )

        self.conn.commit()
        return cursor.lastrowid

    def add_pica_pica_score(
        self,
        round_id: int,
        truco_winner_id: Optional[int],
        truco_points: int,
        envido_winner_id: Optional[int],
        envido_points: int,
        sub_round: int = 1,
    ):
        """Agregar puntaje para una ronda pica-pica"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO pica_pica_scores 
            (round_id, sub_round, truco_winner_id, truco_points, envido_winner_id, envido_points)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                round_id,
                sub_round,
                truco_winner_id,
                truco_points,
                envido_winner_id,
                envido_points,
            ),
        )
        self.conn.commit()

    def add_redondo_score(
        self,
        round_id: int,
        truco_winner_team_id: Optional[int],
        truco_points: int,
        envido_winner_team_id: Optional[int],
        envido_points: int,
    ):
        """Agregar puntajes para una ronda redonda"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            INSERT INTO redondo_scores (round_id, truco_winner_team_id, truco_points, envido_winner_team_id, envido_points)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                round_id,
                truco_winner_team_id,
                truco_points,
                envido_winner_team_id,
                envido_points,
            ),
        )

        self.conn.commit()

    def get_team_scores(self, match_id: int) -> Dict[int, int]:
        """Calcular puntajes actuales de los equipos"""
        cursor = self.conn.cursor()

        # Obtener equipos de la partida
        cursor.execute(
            """
            SELECT t.id, t.name
            FROM teams t
            JOIN match_teams mt ON t.id = mt.team_id
            WHERE mt.match_id = ?
            ORDER BY t.id
        """,
            (match_id,),
        )

        teams = cursor.fetchall()
        team_scores = {}

        # Inicializar puntajes para cada equipo
        for team in teams:
            team_scores[team[0]] = 0

        # Obtener puntajes de rondas de equipo (redondo)
        cursor.execute(
            """
            SELECT rs.truco_winner_team_id, rs.envido_winner_team_id, 
                   SUM(rs.truco_points) as truco_points, SUM(rs.envido_points) as envido_points
            FROM redondo_scores rs
            JOIN rounds r ON rs.round_id = r.id
            WHERE r.match_id = ? AND (rs.truco_winner_team_id IS NOT NULL OR rs.envido_winner_team_id IS NOT NULL)
            GROUP BY rs.truco_winner_team_id, rs.envido_winner_team_id
        """,
            (match_id,),
        )

        for row in cursor.fetchall():
            truco_winner_id = row[0]
            envido_winner_id = row[1]
            truco_points = row[2] or 0
            envido_points = row[3] or 0

            if truco_winner_id and truco_winner_id in team_scores:
                team_scores[truco_winner_id] += truco_points
            if envido_winner_id and envido_winner_id in team_scores:
                team_scores[envido_winner_id] += envido_points

        # Agregar puntajes de rondas pica-pica (puntajes de jugadores cuentan para equipos)
        cursor.execute(
            """
            SELECT t.id as team_id, SUM(ps.envido_points + ps.truco_points) as total_points
            FROM pica_pica_scores ps
            JOIN rounds r ON ps.round_id = r.id
            JOIN player_positions pp ON (ps.truco_winner_id = pp.player_id OR ps.envido_winner_id = pp.player_id) AND pp.match_id = r.match_id
            JOIN team_members tm ON pp.player_id = tm.player_id
            JOIN teams t ON tm.team_id = t.id
            JOIN match_teams mt ON t.id = mt.team_id AND mt.match_id = r.match_id
            WHERE r.match_id = ? AND (ps.truco_winner_id IS NOT NULL OR ps.envido_winner_id IS NOT NULL)
            GROUP BY t.id
        """,
            (match_id,),
        )

        for row in cursor.fetchall():
            team_id = row[0]
            if team_id in team_scores:
                team_scores[team_id] += row[1]

        return team_scores

    def get_match_rounds(self, match_id: int) -> List[Dict]:
        """Obtener todas las rondas de una partida con información detallada"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT r.*, u.nickname as dealer_name
            FROM rounds r
            JOIN player_positions pp ON r.dealer_position = pp.position AND pp.match_id = r.match_id
            JOIN users u ON pp.player_id = u.id
            WHERE r.match_id = ?
            ORDER BY r.round_number DESC
        """,
            (match_id,),
        )

        rounds = [dict(row) for row in cursor.fetchall()]

        # Obtener puntajes para cada ronda
        for round_data in rounds:
            if round_data["round_type"] == "redondo":
                cursor.execute(
                    """
                    SELECT rs.*, t.name as team_name
                    FROM redondo_scores rs
                    LEFT JOIN teams t ON rs.truco_winner_team_id = t.id OR rs.envido_winner_team_id = t.id
                    WHERE rs.round_id = ?
                    ORDER BY rs.id
                """,
                    (round_data["id"],),
                )
            else:  # pica-pica
                cursor.execute(
                    """
                    SELECT ps.*, u.nickname as player_name
                    FROM pica_pica_scores ps
                    LEFT JOIN users u ON ps.truco_winner_id = u.id OR ps.envido_winner_id = u.id
                    WHERE ps.round_id = ?
                    ORDER BY ps.sub_round, ps.id
                """,
                    (round_data["id"],),
                )
            round_data["scores"] = [dict(row) for row in cursor.fetchall()]

        return rounds

    def determine_round_type(self, match_id: int) -> str:
        """Determinar si la próxima ronda debe ser redonda o pica-pica basado en la lógica del juego"""
        match_info = self.get_match_info(match_id)

        # Pica-pica solo existe en juegos de 6 jugadores
        if match_info["players_count"] != 6:
            return "redondo"

        team_scores = self.get_team_scores(match_id)

        # La primera ronda siempre es redonda
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rounds WHERE match_id = ?", (match_id,))
        round_count = cursor.fetchone()[0]

        if round_count == 0:
            return "redondo"

        # Verificar tipo de última ronda
        cursor.execute(
            """
            SELECT round_type FROM rounds 
            WHERE match_id = ? 
            ORDER BY round_number DESC 
            LIMIT 1
        """,
            (match_id,),
        )
        last_round_type = cursor.fetchone()[0]

        # Después de pica-pica, la próxima ronda siempre es redonda
        if last_round_type == "pica-pica":
            return "redondo"

        # Verificar si pica-pica es elegible (solo para juegos de 6 jugadores)
        pica_pica_started = max(team_scores.values()) >= 5
        pica_pica_ended = (
            max(team_scores.values()) >= match_info["pica_pica_end_points"]
        )

        if (
            pica_pica_started
            and not pica_pica_ended
            and match_info["pica_pica_enabled"]
        ):
            return "pica-pica"
        else:
            return "redondo"

    def is_match_finished(self, match_id: int) -> bool:
        """Verificar si la partida ha terminado (algún equipo llegó a 30 puntos)"""
        team_scores = self.get_team_scores(match_id)
        return max(team_scores.values()) >= 30

    def format_round_summary(self, round_data: Dict) -> str:
        """Formatear un resumen de ronda para mostrar"""
        summary = (
            f"Ronda {round_data['round_number']} - {round_data['round_type'].title()}"
        )
        summary += f" (Pie: {round_data['dealer_name']})\n"

        if round_data["round_type"] == "redondo":
            # Agrupar puntajes por equipo
            team_scores = {}

            for score in round_data["scores"]:
                if score["truco_winner_team_id"]:
                    if score["truco_winner_team_id"] not in team_scores:
                        team_scores[score["truco_winner_team_id"]] = {
                            "truco": 0,
                            "envido": 0,
                        }
                    team_scores[score["truco_winner_team_id"]]["truco"] += score[
                        "truco_points"
                    ]

                if score["envido_winner_team_id"]:
                    if score["envido_winner_team_id"] not in team_scores:
                        team_scores[score["envido_winner_team_id"]] = {
                            "truco": 0,
                            "envido": 0,
                        }
                    team_scores[score["envido_winner_team_id"]]["envido"] += score[
                        "envido_points"
                    ]

            # Mostrar puntajes para todos los equipos
            for team_id in sorted(team_scores.keys()):
                truco = team_scores[team_id]["truco"]
                envido = team_scores[team_id]["envido"]
                summary += f"  Equipo {team_id}: "

                parts = []
                if truco > 0:
                    parts.append(f"Truco {truco}")
                if envido > 0:
                    parts.append(f"Envido {envido}")
                if not parts:
                    parts.append("0 puntos")

                summary += ", ".join(parts) + "\n"

        else:  # pica-pica
            sub_rounds = {}
            for score in round_data["scores"]:
                sub_round = score["sub_round"]
                if sub_round not in sub_rounds:
                    sub_rounds[sub_round] = []
                sub_rounds[sub_round].append(score)

            for sub_round in sorted(sub_rounds.keys()):
                summary += f"  Sub-ronda {sub_round}: "
                scores_text = []
                for score in sub_rounds[sub_round]:
                    total = score["truco_points"] + score["envido_points"]
                    if total > 0:
                        scores_text.append(f"{score['player_name']} {total}")
                if not scores_text:
                    scores_text.append("Sin puntos")
                summary += ", ".join(scores_text) + "\n"

        return summary.strip()

    def delete_round(self, round_id: int):
        """Eliminar una ronda y sus puntajes"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM redondo_scores WHERE round_id = ?", (round_id,))
        cursor.execute("DELETE FROM pica_pica_scores WHERE round_id = ?", (round_id,))
        cursor.execute("DELETE FROM rounds WHERE id = ?", (round_id,))
        self.conn.commit()

    def get_existing_teams_with_players(self) -> List[Dict]:
        """Obtener todos los equipos existentes con sus jugadores ordenados"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.name, GROUP_CONCAT(tm.player_id) as player_ids
            FROM teams t
            JOIN team_members tm ON t.id = tm.team_id
            GROUP BY t.id, t.name
            ORDER BY t.id
        """
        )
        teams = []
        for row in cursor.fetchall():
            team = {
                "id": row[0],
                "name": row[1],
                "player_ids": [int(pid) for pid in row[2].split(",")] if row[2] else [],
            }
            teams.append(team)
        return teams

    def find_existing_team(self, player_ids: List[int]) -> Optional[Dict]:
        """Buscar si existe un equipo con exactamente los mismos jugadores"""
        if not player_ids:
            return None

        # Ordenar los player_ids para comparación consistente
        sorted_player_ids = sorted(player_ids)

        existing_teams = self.get_existing_teams_with_players()

        for team in existing_teams:
            if sorted(team["player_ids"]) == sorted_player_ids:
                return team

        return None

    def create_team(self, name: str, player_ids: List[int]) -> int:
        """Crear un nuevo equipo con nombre y jugadores"""
        cursor = self.conn.cursor()

        # Crear el equipo
        cursor.execute("INSERT INTO teams (name) VALUES (?)", (name,))
        team_id = cursor.lastrowid

        # Agregar jugadores al equipo
        for player_id in player_ids:
            cursor.execute(
                "INSERT INTO team_members (team_id, player_id) VALUES (?, ?)",
                (team_id, player_id),
            )

        self.conn.commit()
        return team_id

    def get_or_create_team(self, name: str, player_ids: List[int]) -> int:
        """Obtener equipo existente o crear uno nuevo"""
        # Primero verificar si ya existe un equipo con estos jugadores
        existing_team = self.find_existing_team(player_ids)
        if existing_team:
            return existing_team["id"]

        # Si no existe, crear uno nuevo
        return self.create_team(name, player_ids)

    def assign_teams_to_match(self, match_id: int, team_ids: List[int]):
        """Asignar equipos a una partida"""
        cursor = self.conn.cursor()

        for team_id in team_ids:
            cursor.execute(
                "INSERT INTO match_teams (match_id, team_id) VALUES (?, ?)",
                (match_id, team_id),
            )

        self.conn.commit()

    def get_match_teams_with_players(self, match_id: int) -> List[Dict]:
        """Obtener equipos de una partida con información de jugadores"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.name, GROUP_CONCAT(u.nickname) as player_names
            FROM teams t
            JOIN match_teams mt ON t.id = mt.team_id
            JOIN team_members tm ON t.id = tm.team_id
            JOIN users u ON tm.player_id = u.id
            WHERE mt.match_id = ?
            GROUP BY t.id, t.name
            ORDER BY t.id
        """,
            (match_id,),
        )

        teams = []
        for row in cursor.fetchall():
            team = {
                "id": row[0],
                "name": row[1],
                "player_names": row[2].split(",") if row[2] else [],
            }
            teams.append(team)
        return teams

    def get_match_teams_with_player_ids(self, match_id: int) -> List[Dict]:
        """Obtener equipos de una partida con IDs de jugadores"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT t.id, t.name, GROUP_CONCAT(tm.player_id) as player_ids
            FROM teams t
            JOIN match_teams mt ON t.id = mt.team_id
            JOIN team_members tm ON t.id = tm.team_id
            WHERE mt.match_id = ?
            GROUP BY t.id, t.name
            ORDER BY t.id
        """,
            (match_id,),
        )

        teams = []
        for row in cursor.fetchall():
            team = {
                "id": row[0],
                "name": row[1],
                "player_ids": [int(pid) for pid in row[2].split(",")] if row[2] else [],
            }
            teams.append(team)
        return teams
