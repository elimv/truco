import streamlit as st
import math
import random
from src.truco import TrucoGame


def validate_minimum_players(game: TrucoGame) -> bool:
    """Validar que hay suficientes jugadores para crear una partida"""
    users = game.get_users()
    if len(users) < 2:
        st.warning("Necesita al menos 2 jugadores para crear una partida.")
        return False
    return True


def randomly_select_starting_dealer(team1_players: list, team2_players: list, players_per_team: int) -> str:
    """Seleccionar aleatoriamente el pie inicial"""
    if players_per_team == 1:
        # Para 1v1, seleccionar aleatoriamente entre los dos jugadores
        all_players = team1_players + team2_players
        return random.choice(all_players)
    else:
        # Para juegos de equipos, primero seleccionar equipo aleatorio, luego jugador aleatorio
        selected_team = random.choice([team1_players, team2_players])
        return random.choice(selected_team)


def get_game_configuration() -> tuple[int, int]:
    """Obtener configuración básica del juego"""
    players_count = st.radio("Número de jugadores", [2, 4, 6], horizontal=True)

    if players_count == 6:
        st.info("🔥 Juego de 6 jugadores")
        pica_pica_end_points = st.radio(
            "Pica-pica termina en", [20, 25], horizontal=True
        )
    elif players_count == 4:
        st.info("🎯 Juego de 4 jugadores")
        pica_pica_end_points = 30
    else:  # players_count == 2
        st.info("⚡ Juego 1v1")
        pica_pica_end_points = 30

    return players_count, pica_pica_end_points


def get_1v1_configuration(users: list) -> tuple:
    """Configuración simplificada para juegos 1v1"""
    user_options = {f"{user['nickname']}": user["id"] for user in users}
    user_names = list(user_options.keys())

    st.write("**Seleccionar Jugadores:**")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Jugador 1:**")
        player1 = st.selectbox(
            "Jugador 1",
            options=user_names,
            key="player1_select",
            label_visibility="collapsed"
        )

    with col2:
        st.write("**Jugador 2:**")
        available_players = [p for p in user_names if p != player1]
        player2 = st.selectbox(
            "Jugador 2",
            options=available_players,
            key="player2_select",
            label_visibility="collapsed"
        )

    return (
        player1,  # team1_name (will be auto-generated)
        [player1] if player1 else [],  # team1_players
        player2,  # team2_name (will be auto-generated)
        [player2] if player2 else [],  # team2_players
        user_options,
    )


def get_team_configuration(
    game: TrucoGame, users: list, players_per_team: int
) -> tuple:
    """Obtener configuración de equipos"""
    user_options = {f"{user['nickname']}": user["id"] for user in users}
    user_names = list(user_options.keys())

    # Obtener equipos existentes con nombres de jugadores
    existing_teams_raw = game.get_existing_teams_with_players()
    existing_teams = []

    for team in existing_teams_raw:
        # Solo incluir equipos que tengan el número correcto de jugadores
        if len(team["player_ids"]) != players_per_team:
            continue

        # Obtener nombres de jugadores para este equipo
        player_names = []
        for player_id in team["player_ids"]:
            for user in users:
                if user["id"] == player_id:
                    player_names.append(user["nickname"])
                    break

        team_with_names = {
            "id": team["id"],
            "name": team["name"],
            "player_names": player_names,
            "player_ids": team["player_ids"],
        }
        existing_teams.append(team_with_names)

    # Equipo 1
    if players_per_team == 1:
        st.write("**Jugador 1:**")
        team1_option = st.radio(
            "Opción para Jugador 1:",
            ["Crear nuevo equipo", "Seleccionar equipo existente"],
            horizontal=True,
            key="team1_option",
        )
    else:
        st.write("**Equipo 1:**")
        team1_option = st.radio(
            "Opción para Equipo 1:",
            ["Crear nuevo equipo", "Seleccionar equipo existente"],
            horizontal=True,
            key="team1_option",
        )

    if team1_option == "Crear nuevo equipo":
        if players_per_team == 1:
            team1_name = st.text_input(
                "Nombre del Jugador 1:", value="Jugador 1", key="team1_name"
            )
            team1_players = st.multiselect(
                "Seleccionar jugador",
                options=user_names,
                max_selections=1,
                key="team1_players",
            )
        else:
            team1_name = st.text_input(
                "Nombre del Equipo 1:", value="Equipo 1", key="team1_name"
            )
            team1_players = st.multiselect(
                f"Seleccionar {players_per_team} jugadores para Equipo 1",
                options=user_names,
                max_selections=players_per_team,
                key="team1_players",
            )
    else:
        # Mostrar equipos existentes
        if existing_teams:
            team_options = [
                f"{team['name']} ({', '.join(team['player_names'])})"
                for team in existing_teams
            ]
            selected_team1 = st.selectbox("Seleccionar equipo existente:", team_options, key="team1_select")

            # Encontrar el equipo seleccionado
            selected_team1_data = None
            for team in existing_teams:
                if (
                    f"{team['name']} ({', '.join(team['player_names'])})"
                    == selected_team1
                ):
                    selected_team1_data = team
                    break

            if selected_team1_data:
                team1_name = selected_team1_data["name"]
                team1_players = selected_team1_data["player_names"]
                st.info(
                    f"Equipo seleccionado: {team1_name} con {len(team1_players)} jugadores"
                )
            else:
                team1_name = "Equipo 1"
                team1_players = []
        else:
            if players_per_team == 1:
                st.warning("No hay equipos existentes con 1 jugador. Creando nuevo equipo.")
                team1_name = st.text_input(
                    "Nombre del Jugador 1:", value="Jugador 1", key="team1_name"
                )
                team1_players = st.multiselect(
                    "Seleccionar jugador",
                    options=user_names,
                    max_selections=1,
                    key="team1_players",
                )
            else:
                st.warning(f"No hay equipos existentes con {players_per_team} jugadores. Creando nuevo equipo.")
                team1_name = st.text_input(
                    "Nombre del Equipo 1:", value="Equipo 1", key="team1_name"
                )
                team1_players = st.multiselect(
                    f"Seleccionar {players_per_team} jugadores para Equipo 1",
                    options=user_names,
                    max_selections=players_per_team,
                    key="team1_players",
                )

    # Equipo 2
    if players_per_team == 1:
        st.write("**Jugador 2:**")
        team2_option = st.radio(
            "Opción para Jugador 2:",
            ["Crear nuevo equipo", "Seleccionar equipo existente"],
            horizontal=True,
            key="team2_option",
        )
    else:
        st.write("**Equipo 2:**")
        team2_option = st.radio(
            "Opción para Equipo 2:",
            ["Crear nuevo equipo", "Seleccionar equipo existente"],
            horizontal=True,
            key="team2_option",
        )

    if team2_option == "Crear nuevo equipo":
        if players_per_team == 1:
            team2_name = st.text_input(
                "Nombre del Jugador 2:", value="Jugador 2", key="team2_name"
            )
            # Filtrar jugadores disponibles
            available_players = [p for p in user_names if p not in team1_players]
            team2_players = st.multiselect(
                "Seleccionar jugador",
                options=available_players,
                max_selections=1,
                key="team2_players",
            )
        else:
            team2_name = st.text_input(
                "Nombre del Equipo 2:", value="Equipo 2", key="team2_name"
            )
            # Filtrar jugadores disponibles
            available_players = [p for p in user_names if p not in team1_players]
            team2_players = st.multiselect(
                f"Seleccionar {players_per_team} jugadores para Equipo 2",
                options=available_players,
                max_selections=players_per_team,
                key="team2_players",
            )
    else:
        # Mostrar equipos existentes
        if existing_teams:
            # Filtrar equipos que no tengan jugadores ya seleccionados en team1
            available_teams = []
            for team in existing_teams:
                # Verificar si algún jugador del equipo ya está en team1
                if not any(player in team1_players for player in team['player_names']):
                    available_teams.append(team)

            if available_teams:
                team_options = [
                    f"{team['name']} ({', '.join(team['player_names'])})"
                    for team in available_teams
                ]
                selected_team2 = st.selectbox("Seleccionar equipo existente:", team_options, key="team2_select")
            else:
                st.warning("No hay equipos existentes disponibles (todos tienen jugadores ya seleccionados en Equipo 1)")
                selected_team2 = None

            # Encontrar el equipo seleccionado
            selected_team2_data = None
            if selected_team2:
                for team in available_teams:
                    if (
                        f"{team['name']} ({', '.join(team['player_names'])})"
                        == selected_team2
                    ):
                        selected_team2_data = team
                        break

            if selected_team2_data:
                team2_name = selected_team2_data["name"]
                team2_players = selected_team2_data["player_names"]
                st.info(
                    f"Equipo seleccionado: {team2_name} con {len(team2_players)} jugadores"
                )
            else:
                team2_name = "Equipo 2"
                team2_players = []
        else:
            if players_per_team == 1:
                st.warning("No hay equipos existentes con 1 jugador. Creando nuevo equipo.")
                team2_name = st.text_input(
                    "Nombre del Jugador 2:", value="Jugador 2", key="team2_name"
                )
                # Filtrar jugadores disponibles
                available_players = [p for p in user_names if p not in team1_players]
                team2_players = st.multiselect(
                    "Seleccionar jugador",
                    options=available_players,
                    max_selections=1,
                    key="team2_players",
                )
            else:
                st.warning(f"No hay equipos existentes con {players_per_team} jugadores. Creando nuevo equipo.")
                team2_name = st.text_input(
                    "Nombre del Equipo 2:", value="Equipo 2", key="team2_name"
                )
                # Filtrar jugadores disponibles
                available_players = [p for p in user_names if p not in team1_players]
                team2_players = st.multiselect(
                    f"Seleccionar {players_per_team} jugadores para Equipo 2",
                    options=available_players,
                    max_selections=players_per_team,
                    key="team2_players",
                )

    return (
        team1_name,
        team1_players,
        team2_name,
        team2_players,
        user_options,
    )


def validate_team_selection(
    team1_players: list, team2_players: list, players_per_team: int
) -> bool:
    """Validar que se han seleccionado los jugadores correctos"""
    # Verificar número correcto de jugadores
    if not (
        len(team1_players) == players_per_team
        and len(team2_players) == players_per_team
    ):
        st.error(
            f"Por favor seleccione exactamente {players_per_team} "
            "jugadores para cada equipo"
        )
        return False

    # Verificar que no hay jugadores duplicados entre equipos
    team1_set = set(team1_players)
    team2_set = set(team2_players)
    overlapping_players = team1_set.intersection(team2_set)

    if overlapping_players:
        st.error(
            f"Los siguientes jugadores están en ambos equipos: {', '.join(overlapping_players)}. "
            "Cada jugador solo puede estar en un equipo."
        )
        return False

    return True


def create_or_get_teams(
    game: TrucoGame,
    team1_name: str,
    team1_player_ids: list,
    team2_name: str,
    team2_player_ids: list,
) -> tuple[int, int]:
    """Crear o obtener equipos existentes"""
    team_ids = []

    # Equipo 1
    existing_team1 = game.find_existing_team(team1_player_ids)
    if existing_team1:
        st.info(f"✅ Equipo existente: **{existing_team1['name']}**")
        team1_id = existing_team1["id"]
    else:
        team1_id = game.get_or_create_team(team1_name, team1_player_ids)
        team_ids.append(team1_id)

    # Equipo 2
    existing_team2 = game.find_existing_team(team2_player_ids)
    if existing_team2:
        st.info(f"✅ Equipo existente: **{existing_team2['name']}**")
        team2_id = existing_team2["id"]
    else:
        team2_id = game.get_or_create_team(team2_name, team2_player_ids)
        team_ids.append(team2_id)

    return team1_id, team2_id


def generate_player_order_css(team1_players: list, team2_players: list) -> str:
    """Generar CSS para mostrar el orden de jugadores en círculo"""
    total_players = len(team1_players) + len(team2_players)

    # Crear orden de jugadores: equipo1[0], equipo2[0], equipo1[1], equipo2[1], etc.
    player_order = []
    for i in range(len(team1_players)):
        player_order.append(team1_players[i])
        player_order.append(team2_players[i])

    # Generar HTML con CSS inline para mejor compatibilidad
    html = f"""
    <div style="
        width: 400px; 
        height: 400px; 
        position: relative; 
        margin: 20px auto; 
        border: 2px solid #FFD700; 
        border-radius: 50%; 
        background: rgba(255, 215, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
    ">
    """

    # Calcular posiciones en círculo (counter-clockwise)
    radius = 150
    center_x, center_y = 200, 200

    for i, player in enumerate(player_order):
        # Calcular ángulo (counter-clockwise, empezando desde arriba)
        angle = (i * 360 / total_players - 90) * (3.14159 / 180)

        # Calcular posición
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)

        # Determinar color del equipo
        bg_color = "#FF6B6B" if player in team1_players else "#4ECDC4"
        border_color = "#FF4444" if player in team1_players else "#44CCCC"

        html += f"""
        <div style="
            position: absolute;
            left: {x-30}px;
            top: {y-30}px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: {bg_color};
            border: 3px solid {border_color};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: white;
            text-align: center;
            word-wrap: break-word;
        ">
            {player}
        </div>
        <div style="
            position: absolute;
            left: {x-10}px;
            top: {y+35}px;
            font-size: 10px;
            color: #FFD700;
            font-weight: bold;
        ">
            Pos {i}
        </div>
        """

    html += "</div>"
    return html


def arrange_player_positions(team1_player_ids: list, team2_player_ids: list) -> list:
    """Organizar posiciones de jugadores alternando equipos"""
    players_per_team = len(team1_player_ids)
    player_ids_with_positions = []

    for i in range(players_per_team):
        # Agregar jugador del equipo 1
        player_ids_with_positions.append(team1_player_ids[i])
        # Agregar jugador del equipo 2
        player_ids_with_positions.append(team2_player_ids[i])

    return player_ids_with_positions


def show_match_creation_success(game: TrucoGame, match_id: int, players_count: int):
    """Mostrar información de éxito al crear la partida"""
    st.success(f"Partida creada con ID: {match_id}")

    if players_count == 2:
        # Para 1v1, mostrar mensaje simplificado
        st.info("🥊 Partida 1v1 lista para jugar!")
    else:
        # Mostrar información de los equipos para juegos normales
        st.info("🏆 Equipos configurados:")
        teams_info = game.get_match_teams_with_players(match_id)
        for team in teams_info:
            player_names = ", ".join(team["player_names"])
            st.write(f"• **{team['name']}**: {player_names}")

    st.info("¡Ve a 'Jugar Partida' para empezar a jugar!")


def new_game(game: TrucoGame):
    """Función principal para crear una nueva partida con proceso de 3 pasos"""
    st.header("🆕 Crear Nueva Partida")

    # Validar jugadores mínimos
    if not validate_minimum_players(game):
        return

    # Obtener configuración del juego
    players_count, pica_pica_end_points = get_game_configuration()
    players_per_team = players_count // 2

    # Paso 1: Configuración de equipos
    if players_per_team == 1:
        st.subheader("📋 Paso 1: Seleccionar Jugadores")
    else:
        st.subheader("📋 Paso 1: Configurar Equipos")

    users = game.get_users()

    if players_per_team == 1:
        # Configuración simplificada para 1v1
        team_config = get_1v1_configuration(users)
    else:
        # Configuración normal para equipos
        team_config = get_team_configuration(game, users, players_per_team)

    team1_name, team1_players, team2_name, team2_players, user_options = team_config

    if not validate_team_selection(team1_players, team2_players, players_per_team):
        return

    # Convertir nombres a IDs
    team1_player_ids = [user_options[player] for player in team1_players]
    team2_player_ids = [user_options[player] for player in team2_players]

    # Para 1v1, auto-generar nombres de equipo y crear equipos automáticamente
    if players_per_team == 1:
        team1_name = f"Team_{team1_players[0]}"
        team2_name = f"Team_{team2_players[0]}"
        # Crear equipos automáticamente sin mostrar info al usuario
        team1_id = game.get_or_create_team(team1_name, team1_player_ids)
        team2_id = game.get_or_create_team(team2_name, team2_player_ids)
    else:
        # Crear o obtener equipos normalmente
        team1_id, team2_id = create_or_get_teams(
            game, team1_name, team1_player_ids, team2_name, team2_player_ids
        )

    if players_per_team == 1:
        st.success("✅ Jugadores seleccionados correctamente")
        # Mostrar resumen simplificado para 1v1
        st.write("**Enfrentamiento:**")
        st.write(f"🥊 {team1_players[0]} vs {team2_players[0]}")
    else:
        st.success("✅ Equipos configurados correctamente")
        # Mostrar resumen de equipos
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**{team1_name}:**")
            for player in team1_players:
                st.write(f"• {player}")

        with col2:
            st.write(f"**{team2_name}:**")
            for player in team2_players:
                st.write(f"• {player}")

    # Botón de confirmación
    if st.button("✅ Confirmar y Crear Partida"):
        all_selected_players = team1_players + team2_players

        # Seleccionar pie inicial aleatoriamente
        starting_dealer = randomly_select_starting_dealer(team1_players, team2_players, players_per_team)
        starting_dealer_id = user_options[starting_dealer]

        # Mostrar quién fue seleccionado como pie inicial
        st.info(f"🎲 Pie inicial seleccionado aleatoriamente: **{starting_dealer}**")

        # Organizar posiciones de jugadores
        player_ids_with_positions = arrange_player_positions(
            team1_player_ids, team2_player_ids
        )

        # Crear partida
        match_id = game.create_match(
            players_count,
            pica_pica_end_points,
            player_ids_with_positions,
            starting_dealer_id,
            [team1_id, team2_id],
        )

        show_match_creation_success(game, match_id, players_count)
