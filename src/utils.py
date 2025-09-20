def draw_palitos(points: int) -> str:
    """Dibujar representación tradicional de palitos de los puntos usando CSS"""
    if points == 0:
        return ""

    # CSS styles for matchstick representation
    css_styles = """
    <style>
    .matchstick-container {
        display: inline-block;
        margin: 4px;
        vertical-align: top;
    }
    .matchstick-group {
        display: block;
        margin: 8px 2px;
        vertical-align: top;
        position: relative;
    }
    .matchstick-square {
        width: 40px;
        height: 40px;
        border: 3px solid #FFD700;
        position: relative;
        display: inline-block;
        margin: 1px;
    }
    .matchstick-square.diagonal::before {
        content: '';
        position: absolute;
        background: #FFD700;
        width: 3px;
        height: 56px;
        top: -8px;
        left: 18px;
        transform: rotate(45deg);
    }
    .matchstick-horizontal {
        width: 40px;
        height: 3px;
        background: #FFD700;
        display: inline-block;
        margin: 1px;
        position: relative;
    }
    .divider-line {
        width: 120%;
        height: 2px;
        background: #FFFFFF;
        margin: 15px -10%;
        position: relative;
    }
    </style>
    """

    # Generate matchstick representation
    result = css_styles + '<div class="matchstick-container">'

    # Each group of 5 represents 5 points (square with one diagonal)
    groups_of_5 = points // 5
    remainder = points % 5

    # Draw complete groups of 5 (square with one diagonal stick)
    for i in range(groups_of_5):
        result += '<div class="matchstick-group">'
        result += '<div class="matchstick-square diagonal"></div>'
        result += "</div>"

        # Add divider after every 3 groups (15 points)
        if (i + 1) % 3 == 0:
            result += '<div class="divider-line"></div>'

    # Handle remainder (1-4 sticks)
    if remainder > 0:
        result += '<div class="matchstick-group">'
        if remainder == 1:
            result += '<div class="matchstick-horizontal"></div>'
        elif remainder == 2:
            result += (
                '<div class="matchstick-horizontal"></div>'
                '<div class="matchstick-horizontal"></div>'
            )
        elif remainder == 3:
            result += (
                '<div class="matchstick-horizontal"></div>'
                '<div class="matchstick-horizontal"></div>'
                '<div class="matchstick-horizontal"></div>'
            )
        elif remainder == 4:
            result += '<div class="matchstick-square"></div>'
        result += "</div>"

    result += "</div>"

    return result


def calculate_falta_envido_points(team_scores, round_type):
    """Calcular puntos de Falta Envido según el tipo de ronda"""
    if round_type == "redondo":
        # Puntos que le faltan al equipo con más puntos para ganar
        max_score = max(team_scores.values())
        return 30 - max_score
    else:  # pica-pica
        return 6
