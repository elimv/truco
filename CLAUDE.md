# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Truco Argentino** (Argentine Truco card game) scoring application built with Streamlit and SQLite. The app manages players, matches, teams, and scoring for two game modes: "redondo" (team rounds) and "pica-pica" (individual player rounds for 6-player games).

## Commands

**Development:**
```bash
# Run the application
streamlit run main.py

# Install dependencies (using uv)
uv sync
```

**Database:**
- SQLite database: `truco_game.db` (auto-created on first run)
- Database initialization: automatically handled by `src/db_connection.py:init_database()`

## Architecture

**Entry Point:**
- `main.py` - Streamlit app with 4 tabs: Players, New Game, Active Games, Play Game

**Core Components:**
- `src/truco.py` - Main `TrucoGame` class with all business logic and database operations
- `src/db_connection.py` - Database schema initialization (9 tables)

**UI Modules:**
- `src/users.py` - Player management interface
- `src/new_game.py` - Game creation with team setup
- `src/active_games.py` - List and manage ongoing matches
- `src/play_game_info.py` - Match selection and status display
- `src/round_history.py` - Display game history
- `src/utils.py` - Utility functions (e.g., "falta envido" point calculations)

**Game Logic:**
- **Teams**: 2 teams per match, teams can be reused across matches
- **Round Types**:
  - "redondo" - team-based scoring
  - "pica-pica" - individual player scoring (6-player games only, activated when team reaches 5+ points)
- **Scoring**: Truco (1-4 points) and Envido (1-7 points, or calculated "falta envido")
- **Win Condition**: First team to 30 points

**Database Schema:**
- `users` - Player nicknames
- `teams` + `team_members` - Team composition
- `matches` + `match_teams` + `player_positions` - Game setup
- `rounds` - Round metadata (type, dealer)
- `redondo_scores` + `pica_pica_scores` - Scoring data

## Code Conventions

- SQLite with manual SQL queries (no ORM)
- Streamlit forms for user input with validation
- All database operations in `TrucoGame` class methods
- UI logic separated into individual modules by functionality