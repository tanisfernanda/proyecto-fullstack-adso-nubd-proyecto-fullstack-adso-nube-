/**
 * Lógica del Cliente Web (app.js)
 * Realiza peticiones asíncronas con Fetch a la API de FastAPI + MongoDB
 */

// URL Base del servidor Backend de la Actividad 5
const API_URL = "http://127.0.0.1:8000/tareas";

// Elementos del DOM
const formTarea = document.getElementById("form-tarea");
const inputTitulo = document.getElementById("titulo");
const inputDescripcion = document.getElementById("descripcion");
const contenedorTareas = document.getElementById("contenedor-tareas");
const loadingSpinner = document.getElementById("loading-spinner");
const errorMessage = document.getElementById("error-message");
const contadorTareas = document.getElementById("contador-tareas");

// Evento de inicio: Cargar tareas cuando el HTML esté listo
document.addEventListener("DOMContentLoaded", obtenerTareas);

// Evento de formulario: Enviar nueva tarea
formTarea.addEventListener("submit", crearTarea);

// ---------------------------------------------------
// 1. OBTENER TODAS LAS TAREAS (READ - GET /tareas)
// ---------------------------------------------------
async function obtenerTareas() {
    mostrarCargando(true);
    ocultarError();

    try {
        const respuesta = await fetch(API_URL);

        if (!respuesta.ok) {
            throw new Error(`Error en la petición: ${respuesta.status}`);
        }

        const tareas = await respuesta.json();
        renderizarTareas(tareas);

    } catch (error) {
        console.error("Error al obtener tareas:", error);
        mostrarError("No se pudo conectar con el servidor Backend.");
    } finally {
        mostrarCargando(false);
    }
}

// ---------------------------------------------------
// 2. CREAR UNA NUEVA TAREA (CREATE - POST /tareas)
// ---------------------------------------------------
async function crearTarea(e) {
    e.preventDefault();

    const nuevaTarea = {
        titulo: inputTitulo.value.trim(),
        descripcion: inputDescripcion.value.trim(),
        completada: false
    };

    try {
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevaTarea)
        });

        if (!respuesta.ok) {
            const dataError = await respuesta.json();
            throw new Error(dataError.detail || "Error al guardar la tarea");
        }

        // Limpiar formulario y recargar la lista
        formTarea.reset();
        await obtenerTareas();

    } catch (error) {
        alert(`Atención: ${error.message}`);
    }
}

// ---------------------------------------------------
// 3. CAMBIAR ESTADO A COMPLETADA (UPDATE - PUT /tareas/{id})
// ---------------------------------------------------
async function cambiarEstadoTarea(id, estadoActual) {
    try {
        const respuesta = await fetch(`${API_URL}/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                completada: !estadoActual
            })
        });

        if (!respuesta.ok) {
            throw new Error("Error al actualizar la tarea");
        }

        await obtenerTareas();

    } catch (error) {
        console.error("Error en PUT:", error);
        alert("No se pudo actualizar el estado de la tarea.");
    }
}

// ---------------------------------------------------
// 4. ELIMINAR TAREA (DELETE - DELETE /tareas/{id})
// ---------------------------------------------------
async function eliminarTarea(id) {
    if (!confirm("¿Está seguro de eliminar esta tarea permanentemente?")) return;

    try {
        const respuesta = await fetch(`${API_URL}/${id}`, {
            method: "DELETE"
        });

        if (!respuesta.ok) {
            throw new Error("Error al eliminar la tarea");
        }

        await obtenerTareas();

    } catch (error) {
        console.error("Error en DELETE:", error);
        alert("No se pudo eliminar la tarea.");
    }
}

// ---------------------------------------------------
// FUNCIONES AUXILIARES DE MANIPULACIÓN DEL DOM
// ---------------------------------------------------

function renderizarTareas(tareas) {
    contenedorTareas.innerHTML = "";
    contadorTareas.textContent = `${tareas.length} Tarea${tareas.length !== 1 ? 's' : ''}`;

    if (tareas.length === 0) {
        contenedorTareas.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); padding: 20px;">
                <i class="fa-solid fa-inbox fa-2x"></i>
                <p style="margin-top: 10px;">No hay tareas registradas actualmente en MongoDB.</p>
            </div>
        `;
        return;
    }

    tareas.forEach(tarea => {
        const div = document.createElement("div");
        div.className = `tarea-item ${tarea.completada ? 'completada' : ''}`;

        div.innerHTML = `
            <div class="tarea-info">
                <h3>${escapeHTML(tarea.titulo)}</h3>
                <p>${tarea.descripcion ? escapeHTML(tarea.descripcion) : '<em>Sin descripción</em>'}</p>
            </div>
            <div class="tarea-acciones">
                <button class="btn ${tarea.completada ? 'btn-primary' : 'btn-success'}" 
                        onclick="cambiarEstadoTarea('${tarea._id}', ${tarea.completada})">
                    <i class="fa-solid ${tarea.completada ? 'fa-rotate-left' : 'fa-check'}"></i>
                    ${tarea.completada ? 'Pendiente' : 'Completar'}
                </button>
                <button class="btn btn-danger" onclick="eliminarTarea('${tarea._id}')">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;

        contenedorTareas.appendChild(div);
    });
}

function mostrarCargando(mostrar) {
    if (mostrar) {
        loadingSpinner.classList.remove("hidden");
    } else {
        loadingSpinner.classList.add("hidden");
    }
}

function mostrarError(mensaje) {
    errorMessage.textContent = mensaje;
    errorMessage.classList.remove("hidden");
}

function ocultarError() {
    errorMessage.classList.add("hidden");
}

// Prevenir inyección XSS en el renderizado
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}
