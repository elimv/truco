import streamlit as st
from src.db_connection import init_database
from src.truco import TrucoGame
from src.utils import calculate_falta_envido_points
from src.new_game import new_game
from src.users import users_management
from src.active_games import games_management
from src.round_history import round_history
from src.play_game_info import (
    show_match_points,
    select_active_match,
    check_match_finished,
    get_round_info,
)


def main():
    st.set_page_config(page_title="Marcador de Truco Argentino", layout="wide")

    # Inicializar base de datos
    init_database()
    game = TrucoGame()

    st.title("🎯 Marcador de Truco Argentino")

    # Navegación por pestañas
    tab1, tab2, tab3, tab4 = st.tabs(
        ["👥 Jugadores", "🆕 Nueva Partida", "🎮 Partidas Activas", "🎲 Jugar Partida"]
    )

    with tab1:
        users_management(game)

    with tab2:
        new_game(game)

    with tab3:
        games_management(game)

    with tab4:
        st.header("🎲 Jugar Partida")
        match_id = select_active_match(game)

        if match_id is None:
            st.stop()

        team_scores = game.get_team_scores(match_id)
        players = game.get_match_players(match_id)
        teams_with_names = game.get_match_teams_with_players(match_id)
        teams_with_ids = game.get_match_teams_with_player_ids(match_id)

        # Ensure we have exactly 2 teams
        if len(teams_with_names) != 2:
            st.error("Error: Se esperaban exactamente 2 equipos")
            st.stop()

        team1_id = teams_with_names[0]["id"]
        team2_id = teams_with_names[1]["id"]

        # Check if it's a 1v1 match (each team has only 1 player)
        is_1v1_match = (len(teams_with_names[0]["player_names"]) == 1 and
                       len(teams_with_names[1]["player_names"]) == 1)

        show_match_points(team_scores, teams_with_names)

        match_info = game.get_match_info(match_id)
        round_type, current_dealer_name, current_dealer_position = get_round_info(
            game, match_id, players, match_info
        )
        is_finished = check_match_finished(game, match_id, team_scores)

        # Don't show round forms if game is finished
        if is_finished:
            st.stop()

        if round_type == "redondo":
            st.info(f"🎯 **Ronda Redonda** - Pie: {current_dealer_name}")

            falta_envido_points = calculate_falta_envido_points(team_scores, "redondo")

            with st.form("redondo_round"):
                st.write("**Puntajes de Ronda Redonda**")
                col_truco, col_envido = st.columns(2)

                with col_truco:
                    st.write("**Truco**")

                    # Toggle para ganador del truco (solo 2 estados: Team 1 o Team 2)
                    truco_team_toggle = st.radio(
                        "Ganador del Truco:",
                        options=[team1_id, team2_id],
                        format_func=lambda x: next(
                            (t["player_names"][0] if is_1v1_match else t["name"])
                            for t in teams_with_names if t["id"] == x
                        ),
                        index=None,
                        horizontal=True,
                        key="truco_team_toggle",
                    )

                    # Input para puntos de truco
                    truco_points = st.radio(
                        "Puntos de Truco:",
                        options=[1, 2, 3, 4],
                        horizontal=True,
                        key="truco_points_input",
                    )

                with col_envido:
                    st.write("**Envido**")

                    falta_envido_toggle = st.toggle(
                        label=f"Falta Envido x {falta_envido_points}",
                        value=False,
                        key="envido_toggle",
                    )

                    # Toggle para ganador del envido (3 estados)
                    envido_team_toggle = st.radio(
                        "Ganador del Envido:",
                        options=["No se cantó", team1_id, team2_id],
                        format_func=lambda x: (
                            next((t["player_names"][0] if is_1v1_match else t["name"])
                                 for t in teams_with_names if t["id"] == x)
                            if x != "No se cantó"
                            else "No se cantó"
                        ),
                        horizontal=True,
                        key="envido_team_toggle",
                    )

                    envido_points = st.radio(
                        "Puntos de Envido:",
                        [1, 2, 4, 5, 7],
                        index=None,
                        horizontal=True,
                        key="envido_points_input",
                    )

                    # Input para puntos de envido (solo si hay ganador)
                    if falta_envido_toggle:
                        final_envido_points = falta_envido_points
                    else:
                        final_envido_points = envido_points

                if st.form_submit_button("Agregar Ronda Redonda"):
                    # Validar que al menos truco tenga ganador
                    if not truco_team_toggle:
                        st.error("Al menos un equipo debe ganar Truco o Envido")
                    else:
                        try:
                            round_id = game.add_round(
                                match_id, "redondo", current_dealer_position
                            )

                            # Determinar equipos ganadores
                            envido_winner = (
                                envido_team_toggle
                                if envido_team_toggle != "No se cantó"
                                else None
                            )

                            game.add_redondo_score(
                                round_id,
                                truco_team_toggle,
                                truco_points,
                                envido_winner,
                                final_envido_points,
                            )

                            st.success("¡Ronda agregada!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        else:  # pica-pica
            st.info(f"🔥 **Ronda Pica-Pica** - Pie: {current_dealer_name}")

            # Determinar emparejamientos de jugadores
            sub_rounds = match_info["players_count"] // 2
            st.write(f"Esta ronda tendrá {sub_rounds} sub-rondas")

            first_player_pos = (current_dealer_position + 1) % match_info[
                "players_count"
            ]

            with st.form("pica_pica_round"):
                scores_data = []
                falta_envido_points = calculate_falta_envido_points(
                    team_scores, "pica-pica"
                )

                for sub_round in range(sub_rounds):
                    st.write(f"**Sub-ronda {sub_round + 1}**")

                    player1_pos = (first_player_pos + sub_round) % 6
                    player2_pos = (player1_pos + 3) % 6

                    player1 = next(p for p in players if p["position"] == player1_pos)
                    player2 = next(p for p in players if p["position"] == player2_pos)

                    # Get team information for players
                    player1_team = None
                    player2_team = None
                    for team in teams_with_ids:
                        if player1["player_id"] in team["player_ids"]:
                            player1_team = team["name"]
                        if player2["player_id"] in team["player_ids"]:
                            player2_team = team["name"]

                    # Mostrar enfrentamiento
                    if is_1v1_match:
                        st.write(
                            f"**{player1['nickname']} vs {player2['nickname']}**"
                        )
                    else:
                        st.write(
                            f"**{player1['nickname']} ({player1_team}) vs "
                            f"{player2['nickname']} ({player2_team})**"
                        )

                    col_truco, col_envido = st.columns(2)

                    with col_truco:
                        st.write("**Truco**")

                        # Toggle para ganador del truco (2 estados: player1, player2)
                        truco_winner_key = f"truco_winner_{sub_round}"
                        truco_winner = st.radio(
                            "Ganador:",
                            options=[player1["player_id"], player2["player_id"]],
                            format_func=lambda x: next(
                                p["nickname"] for p in players if p["player_id"] == x
                            ),
                            index=None,
                            horizontal=True,
                            key=truco_winner_key,
                        )

                        # Input para puntos de truco
                        truco_points_sub = st.radio(
                            "Puntos:",
                            [1, 2, 3, 4],
                            key=f"truco_points_{sub_round}",
                            horizontal=True,
                        )

                    with col_envido:
                        st.write("**Envido**")

                        falta_envido_toggle = st.toggle(
                            label=f"Falta Envido x {falta_envido_points}",
                            value=False,
                            key=f"falta_envido_toggle_{sub_round}",
                        )

                        # Toggle para ganador del envido (3 estados: No se cantó, player1, player2)
                        envido_winner_key = f"envido_winner_{sub_round}"
                        envido_winner = st.radio(
                            "Ganador:",
                            options=[
                                "No se cantó",
                                player1["player_id"],
                                player2["player_id"],
                            ],
                            format_func=lambda x: (
                                next(
                                    p["nickname"]
                                    for p in players
                                    if p["player_id"] == x
                                )
                                if x != "No se cantó"
                                else "No se cantó"
                            ),
                            horizontal=True,
                            key=envido_winner_key,
                        )

                        envido_points_sub = st.radio(
                            "Puntos:",
                            [1, 2, 4, 5, 7],
                            index=None,
                            horizontal=True,
                            key=f"envido_points_{sub_round}",
                        )

                    # Determinar qué jugador ganó y sus puntos
                    player1_points = 0
                    player2_points = 0

                    # Add truco points
                    if truco_winner == player1["player_id"]:
                        player1_points += truco_points_sub
                    elif truco_winner == player2["player_id"]:
                        player2_points += truco_points_sub

                    # Add envido points
                    if envido_winner != "No se cantó":
                        envido_pts = falta_envido_points if falta_envido_toggle else envido_points_sub
                        if envido_winner == player1["player_id"]:
                            player1_points += envido_pts
                        elif envido_winner == player2["player_id"]:
                            player2_points += envido_pts

                    winning_player = (
                        player1 if player1_points > player2_points else player2
                    )

                    scores_data.append(
                        {
                            "sub_round": sub_round + 1,
                            "player1": player1,
                            "player2": player2,
                            "winning_player": winning_player,
                            "truco_points": truco_points_sub if truco_winner else 0,
                            "envido_points": (
                                (falta_envido_points if falta_envido_toggle else envido_points_sub)
                                if envido_winner != "No se cantó" else 0
                            ),
                            "total_points": player1_points + player2_points,
                        }
                    )

                if st.form_submit_button("Agregar Ronda Pica-Pica"):
                    # Validar que al menos un jugador haya anotado en cada sub-ronda
                    valid = True
                    for score in scores_data:
                        if score["truco_points"] == 0:
                            st.error(
                                f"Sub-ronda {score['sub_round']}: Faltan puntos de Truco"
                            )
                            valid = False

                    if valid:
                        try:
                            round_id = game.add_round(
                                match_id, "pica-pica", current_dealer_position
                            )

                            for score in scores_data:
                                # Get the actual truco and envido winners from the sub-round data
                                truco_winner_id = None
                                envido_winner_id = None

                                # Find truco winner
                                truco_winner_key = f"truco_winner_{score['sub_round'] - 1}"
                                if truco_winner_key in st.session_state:
                                    truco_winner_id = st.session_state[truco_winner_key]

                                # Find envido winner
                                envido_winner_key = f"envido_winner_{score['sub_round'] - 1}"
                                if envido_winner_key in st.session_state:
                                    envido_winner = st.session_state[envido_winner_key]
                                    if envido_winner != "No se cantó":
                                        envido_winner_id = envido_winner

                                # Only add score if there are actual points to record
                                if score["truco_points"] > 0 or score["envido_points"] > 0:
                                    game.add_pica_pica_score(
                                        round_id,
                                        truco_winner_id,
                                        score["truco_points"],
                                        envido_winner_id,
                                        score["envido_points"],
                                        score["sub_round"],
                                    )

                            st.success("¡Ronda pica-pica agregada!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        round_history(game, match_id, players, team_scores)


if __name__ == "__main__":
    main()
