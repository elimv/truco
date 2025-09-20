import streamlit as st
from src.truco import TrucoGame


def round_history(game: TrucoGame, match_id: int, players: list, team_scores: dict):
    # Historial de Rondas
    st.subheader("📜 Historial de Rondas")

    rounds_history = game.get_match_rounds(match_id)

    if rounds_history:
        # Get teams for this match
        teams = game.get_match_teams_with_players(match_id)

        # Show team scores summary
        if teams:
            st.write("**Resumen de Puntos por Equipo:**")
            cols = st.columns(len(teams))
            for i, team in enumerate(teams):
                with cols[i]:
                    score = team_scores.get(team["id"], 0)
                    st.metric(team["name"], f"{score} puntos")

        st.write("---")

        for round_data in rounds_history:
            round_title = (
                f"Ronda {round_data['round_number']} - "
                f"{round_data['round_type'].title()} "
                f"(Pie: {round_data['dealer_name']})"
            )
            with st.expander(round_title):
                col_summary, col_edit = st.columns([4, 1])

                with col_summary:
                    summary = game.format_round_summary(round_data)
                    st.text(summary)

                with col_edit:
                    if st.button(f"✏️ Editar", key=f"edit_{round_data['id']}"):
                        st.session_state[f"editing_{round_data['id']}"] = True
                        st.rerun()

                    if st.button(f"🗑️ Eliminar", key=f"delete_{round_data['id']}"):
                        game.delete_round(round_data["id"])
                        st.success("Ronda eliminada")
                        st.rerun()

                # Formulario de edición
                if st.session_state.get(f"editing_{round_data['id']}", False):
                    st.write("**Editando Ronda:**")

                    if round_data["round_type"] == "redondo":
                        with st.form(f"edit_redondo_{round_data['id']}"):
                            # Obtener valores actuales
                            current_truco_team = None
                            current_truco_points = 0
                            current_envido_team = None
                            current_envido_points = 0

                            for score in round_data["scores"]:
                                if score["truco_winner_team_id"]:
                                    current_truco_team = score["truco_winner_team_id"]
                                    current_truco_points = score["truco_points"]
                                if score["envido_winner_team_id"]:
                                    current_envido_team = score["envido_winner_team_id"]
                                    current_envido_points = score["envido_points"]

                            col1, col2 = st.columns(2)

                            with col1:
                                st.write("**Truco**")
                                truco_options = [None] + [team["id"] for team in teams]

                                truco_default = None
                                if current_truco_team:
                                    truco_default = current_truco_team

                                new_truco_winner = st.selectbox(
                                    "Ganador del Truco",
                                    options=truco_options,
                                    index=truco_options.index(truco_default),
                                    format_func=lambda x: (
                                        "Ninguno"
                                        if x is None
                                        else next(
                                            team["name"]
                                            for team in teams
                                            if team["id"] == x
                                        )
                                    ),
                                    key=f"edit_truco_winner_{round_data['id']}",
                                )
                                new_truco_points = st.selectbox(
                                    "Puntos de Truco",
                                    [1, 2, 3, 4],
                                    index=(
                                        [1, 2, 3, 4].index(current_truco_points)
                                        if current_truco_points > 0
                                        else 0
                                    ),
                                    key=f"edit_truco_points_{round_data['id']}",
                                )

                            with col2:
                                st.write("**Envido**")
                                envido_options = [None] + [team["id"] for team in teams]

                                envido_default = None
                                if current_envido_team:
                                    envido_default = current_envido_team

                                new_envido_winner = st.selectbox(
                                    "Ganador del Envido",
                                    options=envido_options,
                                    index=envido_options.index(envido_default),
                                    format_func=lambda x: (
                                        "Ninguno"
                                        if x is None
                                        else next(
                                            team["name"]
                                            for team in teams
                                            if team["id"] == x
                                        )
                                    ),
                                    key=f"edit_envido_winner_{round_data['id']}",
                                )
                                new_envido_points = st.selectbox(
                                    "Puntos de Envido",
                                    [1, 2, 4, 5, 6],
                                    index=(
                                        [1, 2, 4, 5, 6].index(current_envido_points)
                                        if current_envido_points > 0
                                        else 0
                                    ),
                                    key=f"edit_envido_points_{round_data['id']}",
                                )

                            col_save, col_cancel = st.columns(2)

                            with col_save:
                                if st.form_submit_button("💾 Guardar Cambios"):
                                    if (
                                        new_truco_winner is None
                                        and new_envido_winner is None
                                    ):
                                        st.error(
                                            "Al menos un equipo debe ganar Truco o Envido"
                                        )
                                    else:
                                        # Eliminar puntajes existentes
                                        cursor = game.conn.cursor()
                                        cursor.execute(
                                            "DELETE FROM redondo_scores WHERE round_id = ?",
                                            (round_data["id"],),
                                        )

                                        # Agregar nuevos puntajes
                                        new_truco_team = (
                                            new_truco_winner
                                            if new_truco_winner != "Ninguno"
                                            else None
                                        )
                                        new_envido_team = (
                                            new_envido_winner
                                            if new_envido_winner != "Ninguno"
                                            else None
                                        )

                                        game.add_redondo_score(
                                            round_data["id"],
                                            new_truco_team,
                                            new_truco_points,
                                            new_envido_team,
                                            new_envido_points,
                                        )

                                        st.session_state[
                                            f"editing_{round_data['id']}"
                                        ] = False
                                        st.success("Ronda actualizada!")
                                        st.rerun()

                            with col_cancel:
                                if st.form_submit_button("❌ Cancelar"):
                                    st.session_state[f"editing_{round_data['id']}"] = (
                                        False
                                    )
                                    st.rerun()

                    else:  # pica-pica editing
                        st.info(
                            "La edición de rondas pica-pica estará disponible en una "
                            "futura actualización."
                        )
                        if st.button("❌ Cerrar", key=f"close_edit_{round_data['id']}"):
                            st.session_state[f"editing_{round_data['id']}"] = False
                            st.rerun()
    else:
        st.info("No se han jugado rondas aún.")
