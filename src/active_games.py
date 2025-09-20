import streamlit as st
from src.truco import TrucoGame


def games_management(game: TrucoGame):
    st.header("🎮 Partidas Activas")
    cursor = game.conn.cursor()
    cursor.execute(
        """
        SELECT m.*, u.nickname as dealer_nickname
        FROM matches m
        LEFT JOIN users u ON m.starting_dealer_id = u.id
        WHERE m.status = 'en_progreso'
        ORDER BY m.created_at DESC
    """
    )

    matches = [dict(row) for row in cursor.fetchall()]

    if matches:
        for match in matches:
            with st.expander(f"{match['name']} - {match['players_count']} jugadores"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Creada:** {match['created_at']}")
                    st.write(f"**Jugadores:** {match['players_count']}")

                with col2:
                    if match["players_count"] == 6:
                        st.write(
                            f"**Pica-pica termina en:** "
                            f"{match['pica_pica_end_points']}"
                        )
                    else:
                        st.write("**Tipo de juego:** 4 jugadores (sin pica-pica)")
                    dealer = match["dealer_nickname"]
                    st.write(f"**Pie inicial:** {dealer}")

                with col3:
                    team_scores = game.get_team_scores(match["id"])
                    teams = game.get_match_teams_with_players(match["id"])

                    if teams:
                        for team in teams:
                            score = team_scores.get(team["id"], 0)
                            team_name = team["name"]
                            st.write(f"**{team_name}:** {score} puntos")
                    else:
                        st.write("**Sin equipos asignados**")

                # Mostrar jugadores por equipo
                teams_with_players = game.get_match_teams_with_players(match["id"])
                if teams_with_players:
                    for team in teams_with_players:
                        player_names = ", ".join(team["player_names"])
                        st.write(f"**{team['name']}:** {player_names}")
                else:
                    # Fallback: mostrar jugadores sin equipos
                    players = game.get_match_players(match["id"])
                    player_names = [p["nickname"] for p in players]
                    players_text = ", ".join(player_names)
                    st.write(f"**Jugadores:** {players_text}")

                # Add delete button
                st.divider()
                col_delete1, col_delete2, col_delete3 = st.columns([1, 1, 1])
                with col_delete2:
                    if st.button(
                        "🗑️ Eliminar Partida",
                        key=f"delete_match_{match['id']}",
                        type="secondary",
                        use_container_width=True
                    ):
                        # Show confirmation dialog
                        if f"confirm_delete_{match['id']}" not in st.session_state:
                            st.session_state[f"confirm_delete_{match['id']}"] = True
                            st.rerun()

                # Show confirmation if button was clicked
                if st.session_state.get(f"confirm_delete_{match['id']}", False):
                    st.warning("⚠️ **¿Estás seguro que quieres eliminar esta partida?**")
                    st.write("Esta acción no se puede deshacer. Se eliminarán todos los datos de la partida incluyendo rondas y puntajes.")

                    col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 1])

                    with col_confirm1:
                        if st.button("✅ Sí, eliminar", key=f"confirm_yes_{match['id']}", type="primary"):
                            try:
                                game.delete_match(match["id"])
                                st.success(f"Partida '{match['name']}' eliminada exitosamente")
                                # Clear confirmation state
                                if f"confirm_delete_{match['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_{match['id']}"]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar la partida: {str(e)}")

                    with col_confirm3:
                        if st.button("❌ Cancelar", key=f"confirm_no_{match['id']}"):
                            # Clear confirmation state
                            if f"confirm_delete_{match['id']}" in st.session_state:
                                del st.session_state[f"confirm_delete_{match['id']}"]
                            st.rerun()
    else:
        st.info("No se encontraron partidas activas.")
