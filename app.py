import streamlit as st
import pandas as pd
from collections import defaultdict

# --- Configuración de la aplicación ---
st.set_page_config(
    page_title="Sistema de Votación de Menú",
    page_icon="🍴",
    layout="centered"
)

st.title("🍴 Sistema de Votación de Menú")

# --- Datos simulados (en memoria, se restablecen al reiniciar la app) ---
# Usamos st.session_state para mantener los datos durante la sesión del usuario
if 'menu_options' not in st.session_state:
    st.session_state.menu_options = {
        "Plato_1": {"nombre": "Lasaña de Carne", "descripcion": "Deliciosa lasaña con salsa boloñesa."},
        "Plato_2": {"nombre": "Ensalada César con Pollo", "descripcion": "Clásica ensalada con aderezo César y pollo a la parrilla."},
        "Plato_3": {"nombre": "Curry de Garbanzos (Vegano)", "descripcion": "Curry aromático con garbanzos y verduras de temporada."},
        "Plato_4": {"nombre": "Paella de Marisco", "descripcion": "Arroz con mariscos frescos y azafrán."},
        "Plato_5": {"nombre": "Tacos al Pastor", "descripcion": "Tradicionales tacos mexicanos con cerdo marinado y piña."}
    }

if 'votes' not in st.session_state:
    st.session_state.votes = defaultdict(lambda: defaultdict(int)) # {id_usuario: {id_plato: 1}}

# --- Funciones Auxiliares ---
def get_menu_df():
    """Convierte las opciones de menú en un DataFrame para visualización."""
    data = []
    for id_plato, info in st.session_state.menu_options.items():
        data.append({"ID Plato": id_plato, "Nombre": info["nombre"], "Descripción": info["descripcion"]})
    return pd.DataFrame(data)

def calculate_results():
    """Calcula los resultados de la votación."""
    plate_counts = defaultdict(int)
    for user_id, user_votes in st.session_state.votes.items():
        for plate_id, voted in user_votes.items():
            if voted: # Si el usuario ha votado por este plato
                plate_counts[plate_id] += 1
    
    results_data = []
    for plate_id, count in plate_counts.items():
        if plate_id in st.session_state.menu_options: # Asegurarse de que el plato existe
            results_data.append({
                "Plato": st.session_state.menu_options[plate_id]["nombre"],
                "Votos": count
            })
    return pd.DataFrame(results_data).sort_values(by="Votos", ascending=False)

# --- Navegación (Sidebar) ---
st.sidebar.header("Navegación")
page = st.sidebar.radio("Ir a:", ["Votar", "Ver Resultados"])

# --- Sección de Votación ---
if page == "Votar":
    st.header("🗳️ Vota por tu Plato Favorito")
    st.markdown("Selecciona una opción del menú para la próxima semana. Tu voto ayudará a la administración a planificar.")

    user_id = st.text_input("Ingresa tu ID de Empleado (ej. 'empleado123')", key="user_id_input")
    
    if not user_id:
        st.warning("Por favor, ingresa tu ID de Empleado para votar.")
    else:
        st.subheader("Opciones de Menú Disponibles")
        menu_df = get_menu_df()
        st.dataframe(menu_df, hide_index=True)

        selected_option_name = st.radio(
            "¿Qué plato te gustaría tener en el menú?",
            options=[info["nombre"] for info in st.session_state.menu_options.values()],
            key="menu_selection"
        )

        if st.button("Enviar Mi Voto"):
            # Encontrar el ID del plato seleccionado
            selected_option_id = None
            for id_plato, info in st.session_state.menu_options.items():
                if info["nombre"] == selected_option_name:
                    selected_option_id = id_plato
                    break
            
            if selected_option_id:
                # Marcar que este usuario votó por este plato
                st.session_state.votes[user_id][selected_option_id] = 1
                st.success(f"¡Gracias, {user_id}! Tu voto por '{selected_option_name}' ha sido registrado.")
                st.info("Nota: Este es un ejemplo simplificado. En una aplicación real, no podrías votar varias veces por el mismo plato.")
            else:
                st.error("Ha ocurrido un error al procesar tu selección. Por favor, inténtalo de nuevo.")

# --- Sección de Resultados ---
elif page == "Ver Resultados":
    st.header("📊 Resultados de la Votación")
    
    results_df = calculate_results()

    if results_df.empty:
        st.info("Aún no hay votos registrados. ¡Sé el primero en votar!")
    else:
        st.dataframe(results_df, hide_index=True)
        st.subheader("Distribución de Votos")
        st.bar_chart(results_df.set_index("Plato"))

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con Streamlit")
