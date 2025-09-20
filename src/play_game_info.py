import streamlit as st
from src.utils import draw_palitos


def get_last_round(game, match_id):
    cursor = game.conn.cursor()
    cursor.execute(
        "SELECT MAX(round_number) FROM rounds WHERE match_id = ?", (match_id,)
    )
    return cursor.fetchone()[0] or 0


def get_current_dealer(
    players: list, match_info: dict, last_round: int
) -> tuple[str, int]:
    starting_dealer_id = match_info["starting_dealer_id"]
    dealer_position = next(
        p["position"] for p in players if p["player_id"] == starting_dealer_id
    )
    current_dealer_position = (dealer_position + last_round) % match_info[
        "players_count"
    ]
    current_dealer_name = next(
        p["nickname"] for p in players if p["position"] == current_dealer_position
    )

    return current_dealer_name, current_dealer_position


def get_active_matches(game) -> list[tuple[int, str]]:
    cursor = game.conn.cursor()
    cursor.execute(
        """
        SELECT id, name FROM matches 
        WHERE status = 'en_progreso'
        ORDER BY created_at DESC
    """
    )
    return cursor.fetchall()


def select_active_match(game) -> int:
    active_matches = get_active_matches(game)
    if not active_matches:
        st.warning(
            "No se encontraron partidas activas. Cree una nueva partida " "primero."
        )
        return

    match_options = {
        f"{name} (ID: {match_id})": match_id for match_id, name in active_matches
    }
    selected_match = st.selectbox("Seleccionar partida", list(match_options.keys()))
    match_id = match_options[selected_match]

    return match_id


def show_match_points(team_scores: dict, teams: list[dict]) -> None:
    st.subheader("📊 Puntajes Actuales")
    if teams:
        cols = st.columns(len(teams))
        for i, team in enumerate(teams):
            with cols[i]:
                st.write(f"**{team['name']}**")
                player_names = ", ".join(team["player_names"])
                st.write(f"Jugadores: {player_names}")
                score = team_scores.get(team["id"], 0)
                st.write(f"Puntaje: {score}/30")
                st.markdown(draw_palitos(score), unsafe_allow_html=True)
    else:
        st.warning("No se encontraron equipos para esta partida")


def get_round_info(game, match_id, players, match_info) -> tuple[str, str, int]:
    last_round = get_last_round(game, match_id)
    current_dealer_name, current_dealer_position = get_current_dealer(
        players, match_info, last_round
    )

    round_type = game.determine_round_type(match_id)

    return round_type, current_dealer_name, current_dealer_position


def check_match_finished(game, match_id, team_scores):
    # Verificar si la partida ha terminado
    if game.is_match_finished(match_id):
        st.success("🏆 ¡Partida terminada!")

        # Find the winning team
        winning_team = None
        max_score = 0
        teams = game.get_match_teams_with_players(match_id)

        for team in teams:
            score = team_scores.get(team["id"], 0)
            if score >= 30 and score > max_score:
                max_score = score
                winning_team = team

        if winning_team:
            st.write(f"**Ganador: {winning_team['name']}**")
        else:
            st.write("**Ganador: Equipo desconocido**")

        if st.button("Marcar partida como terminada"):
            cursor = game.conn.cursor()
            cursor.execute(
                "UPDATE matches SET status = 'terminada' WHERE id = ?",
                (match_id,),
            )
            game.conn.commit()
            st.rerun()
        return True
    return False
