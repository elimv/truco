import streamlit as st
from src.truco import TrucoGame
import pandas as pd


def users_management(game: TrucoGame):
    st.header("👥 Gestión de Jugadores")
    # Agregar nuevo jugador
    with st.form("add_user"):
        nickname = st.text_input("Apodo del jugador")
        if st.form_submit_button("Agregar Jugador"):
            if nickname:
                if game.add_user(nickname):
                    st.success(f"Jugador '{nickname}' agregado exitosamente!")
                    st.rerun()
                else:
                    st.error("El apodo ya existe!")
            else:
                st.error("Por favor ingrese un apodo")

    # Mostrar jugadores
    users = game.get_users()
    if users:
        st.subheader("Jugadores Registrados")
        df = pd.DataFrame(users)
        df.columns = ["ID", "Apodo"]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay jugadores registrados aún.")
