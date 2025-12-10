import React from "react";
import "../../styles/catalogo/productos.css";

function ModalProducto({ producto, cerrar }) {
  if (!producto) return null;

  return (
    <div className="modal show" onClick={cerrar}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <span className="close" onClick={cerrar}>&times;</span>

        <img
          src={producto.imagen}
          className="modal-img"
          alt={producto.nombre}
        />

        <h2>{producto.nombre}</h2>
        <p className="precio">{producto.precio}</p>

        <button className="btn-carrito">
          Agregar al carrito
        </button>
      </div>
    </div>
  );
}

export default ModalProducto;
