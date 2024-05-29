import streamlit as st
import psycopg2

st.title("Establezca su Ocupación")

# Inicializar el estado de la sesión
if 'estado' not in st.session_state:
    st.session_state['estado'] = 'No Autorizado'
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None


# Función para establecer la conexión a la base de datos
def get_db_connection():
    try:
        user = 'postgres.xqfolwxwquynnugqmrnw'
        password = 'Meditrack2024'
        host = 'aws-0-us-west-1.pooler.supabase.com'
        port = '5432'
        dbname = 'postgres'
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

# Función para verificar si el ID existe en la tabla 'empleado'
def check_id_in_empleado(id_to_check):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Empleado, nombre, apellido 
            FROM meditrack.empleado WHERE ID_Empleado = %s
        """
        cur.execute(query, (id_to_check,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al ejecutar la consulta en empleado: {e}")
        return None

# Función para verificar si el ID existe en la tabla 'doctores'
def check_id_in_doctores(id_to_check):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Doctor, nombre, apellido 
            FROM meditrack.doctores WHERE ID_Doctor = %s
        """
        cur.execute(query, (id_to_check,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al ejecutar la consulta en doctores: {e}")
        return None


# Función para añadir una nueva prescripción
def add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, id_doctor):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            INSERT INTO meditrack.prescripcion (ID_Prescripcion, nombre_medicamento, horario_administracion, dosis_gr, ID_Pacientes, ID_Doctor)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, id_doctor))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Prescripción añadida correctamente")
    except Exception as e:
        st.error(f"Error al añadir prescripción: {e}")

#Funcion para eliminar una prescripción
def delete_prescripcion(id_prescripcion):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            DELETE FROM meditrack.prescripcion
            WHERE ID_Prescripcion = %s
        """
        cur.execute(query, (id_prescripcion,))
        conn.commit()
        cur.close()
        conn.close()
        st.success("Prescripción eliminada correctamente")
    except Exception as e:
        st.error(f"Error al eliminar la prescripción: {e}")

# Función para obtener las prescripciones de un paciente específico
def get_prescripciones_de_paciente(id_paciente):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Prescripcion, nombre_medicamento, horario_administracion, dosis_gr, ID_Doctor
            FROM meditrack.prescripcion
            WHERE ID_Pacientes = %s
        """
        cur.execute(query, (id_paciente,))
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener las prescripciones del paciente: {e}")
        return None

# Función para obtener la información de un paciente
def get_paciente_info(id_paciente):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Pacientes, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social
            FROM meditrack.pacientes
            WHERE ID_Pacientes = %s
        """
        cur.execute(query, (id_paciente,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener información del paciente: {e}")
        return None

# Función para actualizar el estado de una prescripción en administra
def update_administracion(id_empleado, selected_prescripciones):
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cur = conn.cursor()
        for prescripcion_id, estado in selected_prescripciones.items():
            query_insert = """
                INSERT INTO meditrack.administra (ID_Empleado, ID_Prescripcion, administrado)
                VALUES (%s, %s, %s)
                ON CONFLICT (ID_Empleado, ID_Prescripcion)
                DO UPDATE SET administrado = EXCLUDED.administrado
            """
            cur.execute(query_insert, (id_empleado, prescripcion_id, estado))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el estado de administración: {e}")
        return False

# Función para conseguir las prescripciones del paciente según su ID
def get_prescripciones_paciente(id_paciente):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT p.ID_Prescripcion, p.nombre_medicamento, p.horario_administracion, p.dosis_gr, COALESCE(a.administrado, FALSE) as administrado
            FROM meditrack.prescripcion p
            LEFT JOIN meditrack.administra a ON p.ID_Prescripcion = a.ID_Prescripcion AND a.ID_Empleado = %s
            WHERE p.ID_Pacientes = %s
        """
        cur.execute(query, (st.session_state['user_id'], id_paciente))
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener las prescripciones del paciente: {e}")
        return None

# Función para administrar la página de administrar medicamentos
def admin_medicamentos_page():
    st.header("Administración de Medicamentos")

    # Inicializar session_state variables
    if 'paciente_encontrado' not in st.session_state:
        st.session_state['paciente_encontrado'] = False
    if 'selected_prescripciones' not in st.session_state:
        st.session_state['selected_prescripciones'] = {}

    # Input para ingresar el ID del paciente
    id_paciente = st.text_input("ID del Paciente:", key="admin_paciente_id")

    # Inicializar prescripciones
    prescripciones = []

    # Botón para buscar las prescripciones del paciente
    if st.button("Buscar Prescripciones", key="btn_buscar_prescripciones"):
        if id_paciente:
            prescripciones = get_prescripciones_paciente(id_paciente)
            if prescripciones:
                st.session_state['paciente_encontrado'] = True
                st.session_state['selected_prescripciones'] = {prescripcion[0]: prescripcion[4] for prescripcion in prescripciones}
                st.success("Prescripciones encontradas:")
            else:
                st.warning("No se encontraron prescripciones para el paciente.")
                st.session_state['paciente_encontrado'] = False
        else:
            st.error("Por favor, ingrese el ID del paciente.")

    # Mostrar las prescripciones si el paciente ha sido encontrado
    if st.session_state['paciente_encontrado']:
        prescripciones = get_prescripciones_paciente(id_paciente)
        if prescripciones:
            for prescripcion in prescripciones:
                prescripcion_info = f"{prescripcion[1]} - Horario: {prescripcion[2]} - Dosis: {prescripcion[3]} mg"
                st.session_state['selected_prescripciones'][prescripcion[0]] = st.checkbox(
                    prescripcion_info,
                    value=st.session_state['selected_prescripciones'][prescripcion[0]],
                    key=f"chk_prescripcion_{prescripcion[0]}"
                )

    # Botón para guardar los cambios
    if st.button("Guardar Cambios", key="btn_guardar_cambios"):
        if update_administracion(st.session_state['user_id'], st.session_state['selected_prescripciones']):
            st.success("Cambios guardados correctamente.")
        else:
            st.error("Error al guardar los cambios.")
        st.session_state['paciente_encontrado'] = False
        st.session_state['selected_prescripciones'] = {}



# Función para obtener la información de un paciente
def get_paciente_info(id_paciente):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT ID_Pacientes, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social
            FROM meditrack.pacientes
            WHERE ID_Pacientes = %s
        """
        cur.execute(query, (id_paciente,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener información del paciente: {e}")
        return None

# Función para actualizar la información de un paciente
def update_paciente_info(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social):
    try:
        conn = get_db_connection()
        if not conn:
            return False
        cur = conn.cursor()
        query = """
            UPDATE pacientes
            SET nombre = %s, apellido = %s, habitacion = %s, alergias = %s, contacto_telefonico = %s, diagnostico = %s, obra_social = %s
            WHERE ID_Pacientes = %s
        """
        cur.execute(query, (nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social, id_paciente))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la información del paciente: {e}")
        return False

# Función para la página de perfil de pacientes
def perfil_pacientes_page():
    st.header("Perfil de Pacientes")
    id_paciente = st.text_input("ID del Paciente:", key="perfil_paciente_id")

    if st.button("Buscar Paciente", key="btn_buscar_paciente"):
        if id_paciente:
            paciente_info = get_paciente_info(id_paciente)
            if paciente_info:
                st.success("Información del paciente encontrada:")
                with st.form(key="form_paciente"):
                    nombre = st.text_input("Nombre", value=paciente_info[1])
                    apellido = st.text_input("Apellido", value=paciente_info[2])
                    habitacion = st.text_input("Habitación", value=paciente_info[3])
                    alergias = st.text_area("Alergias", value=paciente_info[4])
                    contacto_telefonico = st.text_input("Contacto Telefónico", value=paciente_info[5])
                    diagnostico = st.text_area("Diagnóstico", value=paciente_info[6])
                    obra_social = st.text_input("Obra Social", value=paciente_info[7])
                    submit_button = st.form_submit_button(label="Actualizar Información")

                    if submit_button:
                        success = update_paciente_info(id_paciente, nombre, apellido, habitacion, alergias, contacto_telefonico, diagnostico, obra_social)
                        if success:
                            st.success("Información del paciente actualizada correctamente.")
                        else:
                            st.error("Error al actualizar la información del paciente.")
            else:
                st.warning("No se encontró información para el paciente.")
        else:
            st.error("Por favor, ingrese el ID del paciente.")

# Función para obtener el horario de trabajo y el área de un empleado
def get_horario_area(id_empleado):
    try:
        conn = get_db_connection()
        if not conn:
            return None
        cur = conn.cursor()
        query = """
            SELECT horario_entrada, horario_salida, sector_geriatrico
            FROM meditrack.empleado
            WHERE ID_Empleado = %s
        """
        cur.execute(query, (id_empleado,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener el horario y área del empleado: {e}")
        return None

# Función para la página de doctores con pestañas
def doctor_page():
    st.title("Página de Doctor")
    tab1, tab2, tab3 = st.tabs(["Ver Paciente", "Añadir Prescripción", "Prescripciones Asignadas"])

    with tab1:
        st.header("Ver Paciente")
        id_paciente = st.text_input("ID del Paciente:", key="view_paciente_id")
        if st.button("Ver Información del Paciente", key="btn_view_paciente"):
            if id_paciente:
                paciente_info = get_paciente_info(id_paciente)
                if paciente_info:
                    st.write(f"ID: {paciente_info[0]}")
                    st.write(f"Nombre: {paciente_info[1]}")
                    st.write(f"Apellido: {paciente_info[2]}")
                    st.write(f"Habitación: {paciente_info[3]}")
                    st.write(f"Alergias: {paciente_info[4]}")
                    st.write(f"Contacto Telefónico: {paciente_info[5]}")
                    st.write(f"Diagnóstico: {paciente_info[6]}")
                    st.write(f"Obra Social: {paciente_info[7]}")
                else:
                    st.error("No se encontró información para el ID de paciente ingresado.")
            else:
                st.error("Por favor, ingrese un ID de paciente.")

    with tab2:
        st.header("Prescripción")
        id_prescripcion = st.text_input("ID de la Prescripción:", key="add_prescripcion_id")
        nombre_medicamento = st.text_input("Nombre del Medicamento:", key="add_prescripcion_nombre_medicamento")
        horario_administracion = st.time_input("Horario de Administración:", key="add_prescripcion_horario")
        dosis_gr = st.number_input("Dosis (gramos):", min_value=0.0, step=0.1, key="add_prescripcion_dosis")
        id_paciente = st.text_input("ID del Paciente:", key="add_prescripcion_paciente_id")
        if st.button("Añadir Prescripción", key="btn_add_prescripcion"):
            if id_prescripcion and nombre_medicamento and horario_administracion and dosis_gr and id_paciente:
                add_prescripcion(id_prescripcion, nombre_medicamento, horario_administracion, dosis_gr, id_paciente, st.session_state['user_id'])
            else:
                st.error("Por favor, complete todos los campos.")

    with tab3:
        st.header("Prescripciones Asignadas")
        id_prescripcion_eliminar = st.text_input("ID de la Prescripción a Eliminar:", key="delete_prescripcion_id")
        if st.button("Eliminar Prescripción", key="btn_delete_prescripcion"):
            if id_prescripcion_eliminar:
                delete_prescripcion(id_prescripcion_eliminar)
            else:
                st.error("Por favor, ingrese el ID de la prescripción a eliminar.")
        id_paciente = st.text_input("ID del Paciente:", key="view_prescripciones_paciente_id")
        if st.button("Ver Prescripciones", key="btn_view_prescripciones"):
            if id_paciente:
                prescripciones = get_prescripciones_de_paciente(id_paciente)
                if prescripciones:
                    for prescripcion in prescripciones:
                        st.write(f"ID de la Prescripción: {prescripcion[0]}")
                        st.write(f"Nombre del Medicamento: {prescripcion[1]}")
                        st.write(f"Horario de Administración: {prescripcion[2]}")
                        st.write(f"Dosis (gramos): {prescripcion[3]}")
                        st.write(f"ID del Doctor: {prescripcion[4]}")
                        st.write("---")
                else:
                    st.error("No se encontraron prescripciones para ese paciente.")
            else:
                st.error("Por favor, ingrese el ID del paciente.")
        

# Función para la página de empleados con pestañas
def empleado_page():
    st.title("Página de Empleado")
    tab1, tab2, tab3 = st.tabs(["Administración de Medicamentos", "Horarios de Trabajo", "Información del Paciente"])

    with tab1:
        admin_medicamentos_page()

    with tab2:
        st.header("Horarios de Trabajo")
        horario_area = get_horario_area(st.session_state['user_id'])
        if horario_area:
            st.write(f"Horario de Entrada: {horario_area[0]}")
            st.write(f"Horario de Salida: {horario_area[1]}")
            st.write(f"Área: {horario_area[2]}")
        else:
            st.info("No se encontraron datos de horario y área.")

    with tab3:
        perfil_pacientes_page()

# Main application logic
if st.session_state['estado'] == 'Autorizado':
    # Verifica si el usuario ya ha ingresado su ID
    if 'user_id' not in st.session_state or not st.session_state['user_id']:
        id_input = st.text_input("Ingrese su ID:", key="login_id")
        if st.button("Ingresar", key="login_button"):
            if not id_input:
                st.error("Por favor, ingrese un ID válido.")
            else:
                empleado_details = check_id_in_empleado(id_input)
                doctor_details = check_id_in_doctores(id_input)
                if empleado_details:
                    st.session_state['estado'] = 'Autorizado'
                    st.session_state['user_role'] = 'Empleado'
                    st.session_state['user_id'] = id_input
                    st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
                    st.experimental_rerun()
                elif doctor_details:
                    st.session_state['estado'] = 'Autorizado'
                    st.session_state['user_role'] = 'Doctor'
                    st.session_state['user_id'] = id_input
                    st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
                    st.experimental_rerun()
                else:
                    st.error("El ID no existe en la base de datos.")
    else:
        # Muestra un mensaje de bienvenida si ya ha iniciado sesión
        st.success(f"Bienvenido {st.session_state['user_role']} ID: {st.session_state['user_id']}")
        if st.session_state['user_role'] == 'Empleado':
            empleado_page()
        elif st.session_state['user_role'] == 'Doctor':
            doctor_page()

else:
    st.error("Debes iniciar sesión primero.")
