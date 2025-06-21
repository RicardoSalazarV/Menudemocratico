import streamlit as st
import pandas as pd
from collections import defaultdict
import uuid # Para generar IDs únicos para los platos

# --- Configuración de la aplicación ---
st.set_page_config(
    page_title="Sistema de Votación de Menú",
    page_icon="🍴",
    layout="centered"
)

st.title("🍴 Sistema de Votación de Menú")

# --- Datos simulados (en memoria, se restablecen al reiniciar la app) ---
# Usamos st.session_state para mantener los datos durante la sesión del usuario

# Inicialización de opciones de menú
if 'menu_options' not in st.session_state:
    st.session_state.menu_options = {
        str(uuid.uuid4()): {"nombre": "Lasaña de Carne", "descripcion": "Deliciosa lasaña con salsa boloñesa."},
        str(uuid.uuid4()): {"nombre": "Ensalada César con Pollo", "descripcion": "Clásica ensalada con aderezo César y pollo a la parrilla."},
        str(uuid.uuid4()): {"nombre": "Curry de Garbanzos (Vegano)", "descripcion": "Curry aromático con garbanzos y verduras de temporada."},
        str(uuid.uuid4()): {"nombre": "Paella de Marisco", "descripcion": "Arroz con mariscos frescos y azafrán."},
        str(uuid.uuid4()): {"nombre": "Tacos al Pastor", "descripcion": "Tradicionales tacos mexicanos con cerdo marinado y piña."}
    }

# Inicialización de votos
if 'votes' not in st.session_state:
    st.session_state.votes = defaultdict(lambda: defaultdict(int)) # {id_usuario: {id_plato: 1}}

# Simulación de sesión de administrador (muy básica, solo para demostración)
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- Funciones Auxiliares ---
def get_menu_df_for_display():
    """Convierte las opciones de menú en un DataFrame para visualización amigable."""
    data = []
    for id_plato, info in st.session_state.menu_options.items():
        data.append({"ID Único": id_plato, "Nombre": info["nombre"], "Descripción": info["descripcion"]})
    return pd.DataFrame(data)

def calculate_results():
    """Calcula los resultados de la votación."""
    plate_counts = defaultdict(int)
    for user_id, user_votes in st.session_state.votes.items():
        for plate_id, voted in user_votes.items():
            if voted: # Si el usuario ha votado por este plato (suponemos 1 significa votado)
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
page = st.sidebar.radio("Ir a:", ["Votar", "Ver Resultados", "Administración"])

# --- Sección de Votación ---
if page == "Votar":
    st.header("🗳️ Vota por tu Plato Favorito")
    st.markdown("Selecciona una opción del menú para la próxima semana. Tu voto ayudará a la administración a planificar.")

    user_id = st.text_input("Ingresa tu ID de Empleado (ej. 'empleado123')", key="user_id_input")
    
    if not user_id:
        st.warning("Por favor, ingresa tu ID de Empleado para votar.")
    else:
        st.subheader("Opciones de Menú Disponibles")
        menu_df = get_menu_df_for_display()
        if not menu_df.empty:
            st.dataframe(menu_df[['Nombre', 'Descripción']], hide_index=True) # Mostrar solo nombre y descripción
        else:
            st.info("No hay opciones de menú disponibles para votar.")


        # Opciones para el radio button deben ser solo los nombres
        menu_option_names = [info["nombre"] for info in st.session_state.menu_options.values()]
        
        if menu_option_names:
            selected_option_name = st.radio(
                "¿Qué plato te gustaría tener en el menú?",
                options=menu_option_names,
                key="menu_selection"
            )

            if st.button("Enviar Mi Voto"):
                selected_option_id = None
                for id_plato, info in st.session_state.menu_options.items():
                    if info["nombre"] == selected_option_name:
                        selected_option_id = id_plato
                        break
                
                if selected_option_id:
                    # Implementación de voto único por usuario por período (simplificado)
                    if selected_option_id in st.session_state.votes[user_id]:
                        st.warning(f"¡{user_id}, ya has votado por '{selected_option_name}' en esta sesión!")
                    else:
                        st.session_state.votes[user_id][selected_option_id] = 1
                        st.success(f"¡Gracias, {user_id}! Tu voto por '{selected_option_name}' ha sido registrado.")
                else:
                    st.error("Ha ocurrido un error al procesar tu selección. Por favor, inténtalo de nuevo.")
        else:
            st.info("No hay platos definidos para votar. Contacta al administrador.")


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

# --- Sección de Administración ---
elif page == "Administración":
    st.header("⚙️ Panel de Administración")
    
    if not st.session_state.admin_logged_in:
        password = st.text_input("Contraseña de Administrador", type="password")
        if st.button("Iniciar Sesión"):
            if password == "admin123": # Contraseña simple de demostración
                st.session_state.admin_logged_in = True
                st.success("Sesión de administrador iniciada correctamente.")
                st.experimental_rerun() # Volver a cargar para mostrar la interfaz
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.subheader("Gestión de Opciones de Menú")

        st.markdown("---")
        st.subheader("Agregar Nuevo Plato")
        with st.form("add_plate_form"):
            new_plate_name = st.text_input("Nombre del Nuevo Plato")
            new_plate_description = st.text_area("Descripción del Nuevo Plato")
            submit_add = st.form_submit_button("Agregar Plato")

            if submit_add:
                if new_plate_name and new_plate_description:
                    new_id = str(uuid.uuid4())
                    st.session_state.menu_options[new_id] = {
                        "nombre": new_plate_name,
                        "descripcion": new_plate_description
                    }
                    st.success(f"Plato '{new_plate_name}' agregado exitosamente.")
                    # Limpiar los campos del formulario si es necesario, o recargar
                    st.experimental_rerun() 
                else:
                    st.error("Por favor, completa todos los campos para agregar un plato.")

        st.markdown("---")
        st.subheader("Editar o Eliminar Platos Existentes")
        
        current_menu_df = get_menu_df_for_display()
        
        if not current_menu_df.empty:
            st.dataframe(current_menu_df, hide_index=True)

            # Usar un selectbox para elegir el plato a editar/eliminar
            plate_names_and_ids = {f"{row['Nombre']} ({row['ID Único'][-4:]})": row['ID Único'] 
                                   for index, row in current_menu_df.iterrows()}
            
            selected_plate_display = st.selectbox(
                "Selecciona un plato para editar o eliminar:",
                options=list(plate_names_and_ids.keys()),
                key="edit_plate_selection"
            )

            selected_plate_id_to_edit = plate_names_and_ids.get(selected_plate_display)
            
            if selected_plate_id_to_edit:
                selected_plate_info = st.session_state.menu_options[selected_plate_id_to_edit]

                with st.form("edit_delete_plate_form"):
                    st.write(f"Editando/Eliminando: **{selected_plate_info['nombre']}**")
                    edited_name = st.text_input("Nombre del Plato", value=selected_plate_info["nombre"])
                    edited_description = st.text_area("Descripción del Plato", value=selected_plate_info["descripcion"])

                    col1, col2 = st.columns(2)
                    with col1:
                        submit_edit = st.form_submit_button("Guardar Cambios")
                    with col2:
                        submit_delete = st.form_submit_button("Eliminar Plato")

                    if submit_edit:
                        if edited_name and edited_description:
                            st.session_state.menu_options[selected_plate_id_to_edit] = {
                                "nombre": edited_name,
                                "descripcion": edited_description
                            }
                            st.success(f"Plato '{edited_name}' actualizado exitosamente.")
                            st.experimental_rerun()
                        else:
                            st.error("Los campos de nombre y descripción no pueden estar vacíos.")
                    
                    if submit_delete:
                        # Confirmación antes de eliminar (opcional pero recomendado)
                        if st.warning(f"¿Estás seguro de que quieres eliminar '{selected_plate_info['nombre']}'?"):
                             if st.button("Confirmar Eliminación"): # Botón de confirmación real
                                 del st.session_state.menu_options[selected_plate_id_to_edit]
                                 # También limpiar votos relacionados para ese plato
                                 for user_id in st.session_state.votes:
                                     if selected_plate_id_to_edit in st.session_state.votes[user_id]:
                                         del st.session_state.votes[user_id][selected_plate_id_to_edit]
                                 st.success(f"Plato '{selected_plate_info['nombre']}' eliminado exitosamente.")
                                 st.experimental_rerun()
                        # Si no hay confirmación, el botón 'Eliminar Plato' no hace nada por sí solo
            else:
                 st.info("Selecciona un plato del menú desplegable para editar o eliminar.")
        else:
            st.info("No hay platos cargados en el menú para editar o eliminar. Agrega uno primero.")
        
        if st.button("Cerrar Sesión de Administrador"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con Streamlit")

