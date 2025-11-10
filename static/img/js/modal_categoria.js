// static/js/modal_categoria.js
document.addEventListener("DOMContentLoaded", () => {

    // --- Helper: abrir/ocultar modal de forma segura ---
    function openModal(modal) { if (modal) modal.style.display = 'flex'; }
    function closeModal(modal) { if (modal) modal.style.display = 'none'; }

    // --- Modal Agregar ---
    const modalAgregar = document.getElementById("modalCategoria");
    const abrirAgregar = document.getElementById("abrirModal");
    const cerrarAgregar = document.getElementById("cerrarModal");
    const cerrarAgregar2 = document.getElementById("cerrarModal2");

    if (abrirAgregar && modalAgregar) {
        abrirAgregar.addEventListener('click', () => openModal(modalAgregar));
        if (cerrarAgregar) cerrarAgregar.addEventListener('click', () => closeModal(modalAgregar));
        if (cerrarAgregar2) cerrarAgregar2.addEventListener('click', () => closeModal(modalAgregar));
    }

    // --- Modal Editar ---
    const modalEditar = document.getElementById("modalEditar");
    const abrirEditar = document.getElementById("abrirModalEditar");
    const cerrarEditar = document.getElementById("cerrarModalEditar");
    const cerrarEditar2 = document.getElementById("cerrarModalEditar2");

    if (abrirEditar && modalEditar) {
        abrirEditar.addEventListener('click', () => openModal(modalEditar));
        if (cerrarEditar) cerrarEditar.addEventListener('click', () => closeModal(modalEditar));
        if (cerrarEditar2) cerrarEditar2.addEventListener('click', () => closeModal(modalEditar));
    }

    // --- Modal Eliminar ---
    const modalEliminar = document.getElementById("modalEliminarCategoria");
    const abrirEliminar = document.getElementById("abrirModalEliminar");
    const cerrarEliminar = document.getElementById("cerrarModalEliminar");
    const cerrarEliminar2 = document.getElementById("cerrarModalEliminar2");

    if (abrirEliminar && modalEliminar) {
        abrirEliminar.addEventListener('click', () => openModal(modalEliminar));
        if (cerrarEliminar) cerrarEliminar.addEventListener('click', () => closeModal(modalEliminar));
        if (cerrarEliminar2) cerrarEliminar2.addEventListener('click', () => closeModal(modalEliminar));
    }

    // --- Cerrar si clic fuera del modal ---
    window.addEventListener('click', (e) => {
        if (e.target === modalAgregar) closeModal(modalAgregar);
        if (e.target === modalEditar) closeModal(modalEditar);
        if (e.target === modalEliminar) closeModal(modalEliminar);
    });

    // --- Función para llenar el select de categorías ---
    function populateCategoriaSelect(seccionValue, targetSelect) {
        if (!targetSelect) return;
        targetSelect.innerHTML = '';

        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Selecciona una categoría principal --';
        targetSelect.appendChild(defaultOption);

        const data = window.categoriasData?.[seccionValue];
        if (!data || data.length === 0) {
            const noOpt = document.createElement('option');
            noOpt.textContent = '(No hay categorías disponibles)';
            noOpt.disabled = true;
            targetSelect.appendChild(noOpt);
            return;
        }

        // ✅ CORREGIDO: recorrer objetos con {id, nombre}
        data.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.nombre;
            targetSelect.appendChild(opt);
        });
    }

    // --- Conectar selects del modal Agregar ---
    try {
        const seccionAgregar = document.getElementById('seccion');
        const categoriaAgregar = document.getElementById('categoria');

        if (seccionAgregar && categoriaAgregar) {
            seccionAgregar.addEventListener('change', () => {
                const val = seccionAgregar.value;
                const cont = document.getElementById('categoria-container');
                if (!val) {
                    if (cont) cont.style.display = 'none';
                    return;
                }
                if (cont) cont.style.display = 'block';
                populateCategoriaSelect(val, categoriaAgregar);
            });

            // Si ya hay una sección seleccionada al cargar, la llena
            if (seccionAgregar.value)
                populateCategoriaSelect(seccionAgregar.value, categoriaAgregar);
        }
    } catch (e) {
        console.error('Error init agregar modal selects:', e);
    }

    // --- Conectar selects del modal Editar ---
    try {
        const seccionEditar = document.getElementById('editarSeccion') || document.getElementById('seccion_edit');
        const categoriaEditar = document.getElementById('editarCategoria') || document.getElementById('categoria_edit');
        const contEditar = document.getElementById('categoria-container-editar') || document.getElementById('categoria-container-edit');

        if (seccionEditar && categoriaEditar) {
            seccionEditar.addEventListener('change', () => {
                const val = seccionEditar.value;
                if (!val) {
                    if (contEditar) contEditar.style.display = 'none';
                    return;
                }
                if (contEditar) contEditar.style.display = 'block';
                populateCategoriaSelect(val, categoriaEditar);
            });

            // Si ya hay valor seleccionado
            if (seccionEditar.value)
                populateCategoriaSelect(seccionEditar.value, categoriaEditar);
        }
    } catch (e) {
        console.error('Error init editar modal selects:', e);
    }

});
