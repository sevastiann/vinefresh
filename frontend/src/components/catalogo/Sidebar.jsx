// src/components/catalogo/Sidebar.jsx
import React from "react";

function Sidebar() {
  return (
    <aside className="sidebar">
      <h3>Filtros (React)</h3>
      {/* Aquí luego trasladamos tus filtros de Django:
          - País
          - Color
          - Tipo de uva
          - Festividad
          - Premium / Regalo
          etc. */}
      <div className="filtro-busqueda">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          className="input-buscar"
        />
        <button className="btn-buscar">Buscar</button>
      </div>
    </aside>
  );
}

export default Sidebar;
