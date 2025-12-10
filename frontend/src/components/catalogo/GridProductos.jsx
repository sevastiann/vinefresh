import React, { useEffect, useState } from "react";
import ModalProducto from "./ModalProducto";

function GridProductos() {
  const [htmlGrid, setHtmlGrid] = useState("<p>Cargando productos...</p>");
  const [productoActivo, setProductoActivo] = useState(null);

  useEffect(() => {
    fetch("/catalogo/productos/")
      .then((res) => res.text())
      .then((html) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const grid = doc.querySelector(".productos-grid");

        if (grid) {
          setHtmlGrid(grid.innerHTML);
        } else {
          setHtmlGrid("<p>No se encontró el grid de productos.</p>");
        }
      })
      .catch(() => {
        setHtmlGrid("<p>Error cargando productos.</p>");
      });
  }, []);

  // Detectar clics en productos
  const handleClick = (e) => {
    const card = e.target.closest(".card-producto");
    if (!card) return;

    const nombre = card.querySelector("h4")?.textContent || "";
    const precio = card.querySelector(".precio")?.textContent || "";
    const imagen = card.querySelector("img")?.src || "";

    setProductoActivo({
      nombre,
      precio,
      imagen,
      descripcion: "",
    });
  };

  return (
    <>
      <main
        className="productos-grid"
        onClick={handleClick}
        dangerouslySetInnerHTML={{ __html: htmlGrid }}
      />

      <ModalProducto
        producto={productoActivo}
        cerrar={() => setProductoActivo(null)}
      />
    </>
  );
}

export default GridProductos;
