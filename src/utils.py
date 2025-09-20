def draw_palitos(points: int) -> str:
    """Dibujar representación tradicional de palitos de los puntos usando SVG"""
    if points == 0:
        return ""

    # Predefined SVG elements for each stick count (traditional tally marks)
    stick_svgs = {
        1: '''<svg width="60" height="15" viewBox="0 0 60 15" style="display: inline-block; margin: 2px;">
            <line x1="10" y1="7" x2="50" y2="7" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        </svg>''',

        2: '''<svg width="60" height="25" viewBox="0 0 60 25" style="display: inline-block; margin: 2px;">
            <line x1="10" y1="6" x2="50" y2="6" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="19" x2="50" y2="19" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        </svg>''',

        3: '''<svg width="60" height="35" viewBox="0 0 60 35" style="display: inline-block; margin: 2px;">
            <line x1="10" y1="6" x2="50" y2="6" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="17" x2="50" y2="17" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="28" x2="50" y2="28" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        </svg>''',

        4: '''<svg width="60" height="45" viewBox="0 0 60 45" style="display: inline-block; margin: 2px;">
            <line x1="10" y1="6" x2="50" y2="6" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="16" x2="50" y2="16" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="26" x2="50" y2="26" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="36" x2="50" y2="36" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        </svg>''',

        5: '''<svg width="60" height="45" viewBox="0 0 60 45" style="display: inline-block; margin: 2px;">
            <line x1="10" y1="6" x2="50" y2="6" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="16" x2="50" y2="16" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="26" x2="50" y2="26" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="10" y1="36" x2="50" y2="36" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
            <line x1="5" y1="39" x2="55" y2="3" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        </svg>'''
    }

    # Generate matchstick representation
    result = '<div style="display: inline-block; margin: 4px; vertical-align: top;">'

    # Each group of 5 represents 5 points
    groups_of_5 = points // 5
    remainder = points % 5

    # Draw complete groups of 5
    for i in range(groups_of_5):
        result += '<div style="display: block; margin: 4px 0;">'
        result += stick_svgs[5]
        result += "</div>"

        # Add divider after every 3 groups (15 points)
        if (i + 1) % 3 == 0:
            result += '<div style="width: 100%; height: 2px; background: #FFFFFF; margin: 8px 0;"></div>'

    # Handle remainder (1-4 sticks)
    if remainder > 0:
        result += '<div style="display: block; margin: 4px 0;">'
        result += stick_svgs[remainder]
        result += "</div>"

    result += "</div>"

    return result


def calculate_falta_envido_points(team_scores, round_type):
    """Calcular puntos de Falta Envido según el tipo de ronda"""
    if round_type == "redondo":
        # Si ambos equipos están bajo 15 puntos, falta envido gana la partida
        max_score = max(team_scores.values())
        if max_score < 15:
            return 30  # Suficiente para ganar la partida
        else:
            # Puntos que le faltan al equipo con más puntos para ganar
            return 30 - max_score
    else:  # pica-pica
        return 6
