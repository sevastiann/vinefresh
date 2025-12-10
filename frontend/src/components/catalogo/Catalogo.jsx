// src/components/catalogo/Catalogo.jsx
import React, { useEffect, useState } from "react";
import "../../styles/catalogo/productos.css";

function Catalogo() {
  const [htmlCatalogo, setHtmlCatalogo] = useState("<p>Cargando catálogo...</p>");

  // Detectar sección desde la URL (?seccion=vinos / ?seccion=combos)
  const params = new URLSearchParams(window.location.search);
  const seccion = params.get("seccion") || "vinos";

  /* ==========================
     1️⃣ CARGAR HTML DESDE DJANGO
  ========================== */
  useEffect(() => {
    fetch(`/catalogo/productos/?seccion=${seccion}`)
      .then((res) => res.text())
      .then((html) => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const layout = doc.querySelector(".layout-container");

        if (layout) {
          // ⬅ importante: usamos outerHTML para incluir el div .layout-container
          setHtmlCatalogo(layout.outerHTML);
        } else {
          setHtmlCatalogo("<p>No se encontró el catálogo.</p>");
        }
      })
      .catch((err) => {
        console.error("Error cargando catálogo:", err);
        setHtmlCatalogo("<p>Error cargando catálogo.</p>");
      });
  }, [seccion]);

  /* ==========================
     2️⃣ MOVER MODALES (evita que se descuadren)
  ========================== */
  useEffect(() => {
    if (!htmlCatalogo.includes("modal")) return;

    const timer = setTimeout(() => {
      const modales = document.querySelectorAll(".modal");
      const wrapper = document.querySelector(".layout-wrapper-react");

      if (wrapper && modales.length > 0) {
        modales.forEach((m) => wrapper.appendChild(m));
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [htmlCatalogo]);

  /* ==========================
     3️⃣ ACTIVAR FILTROS + MODALES
  ========================== */
  useEffect(() => {
    if (!htmlCatalogo.includes("productos-container")) return;

    const timer = setTimeout(() => {
      console.log("✔ Scripts de catálogo activados");

      const FILTRAR_URL =
        seccion === "combos"
          ? "/catalogo/filtrar_combos_cliente/"
          : "/catalogo/filtrar_productos/";

      // ------- FILTRAR PRODUCTOS -------
      function filtrarProductos() {
        const inputBuscar = document.querySelector(".input-buscar");
        const inputsPrecio = document.querySelectorAll(".input-precio");

        const buscar = inputBuscar?.value || "";
        const precioMin = inputsPrecio[0]?.value || "";
        const precioMax = inputsPrecio[1]?.value || "";

        const params = new URLSearchParams();
        params.append("buscar", buscar);
        params.append("precio_min", precioMin);
        params.append("precio_max", precioMax);

        const grupos = ["pais", "color", "alcohol", "uva", "vol", "fest", "prem", "reg"];

        grupos.forEach((grupo) => {
          const seleccionados = [
            ...document.querySelectorAll(`input[name="${grupo}"]:checked`),
          ].map((c) => c.value);

          if (seleccionados.length > 0) {
            params.append(grupo, seleccionados.join(","));
          }
        });

        fetch(FILTRAR_URL + "?" + params.toString())
          .then((r) => r.text())
          .then((html) => {
            const grid = document.querySelector("#productos-container .productos-grid");
            if (grid) grid.innerHTML = html;
          })
          .catch((err) => console.error("Error en filtrado:", err));
      }

      // ------- MODALES -------
      function clickHandler(e) {
        // Abrir modal
        if (e.target.classList.contains("btn-detalle")) {
          const id = e.target.dataset.modal;
          const modal = document.getElementById(id);
          if (modal) {
            modal.classList.add("show");
            document.body.style.overflow = "hidden";
          }
        }

        // Cerrar con X
        if (e.target.classList.contains("close")) {
          const modal = e.target.closest(".modal");
          if (modal) {
            modal.classList.remove("show");
            document.body.style.overflow = "";
          }
        }

        // Cerrar clickeando fuera
        if (e.target.classList.contains("modal")) {
          e.target.classList.remove("show");
          document.body.style.overflow = "";
        }
      }

      // ------- ENGANCHAR EVENTOS -------
      const inputBuscar = document.querySelector(".input-buscar");
      const btnBuscar = document.querySelector(".btn-buscar");
      const inputsPrecio = document.querySelectorAll(".input-precio");
      const checkboxes = document.querySelectorAll("input[type='checkbox']");

      if (inputBuscar) inputBuscar.addEventListener("input", filtrarProductos);
      if (btnBuscar) btnBuscar.addEventListener("click", filtrarProductos);
      inputsPrecio.forEach((inp) => inp.addEventListener("input", filtrarProductos));
      checkboxes.forEach((c) => c.addEventListener("change", filtrarProductos));

      document.addEventListener("click", clickHandler);

      // LIMPIEZA
      return () => {
        if (inputBuscar) inputBuscar.removeEventListener("input", filtrarProductos);
        if (btnBuscar) btnBuscar.removeEventListener("click", filtrarProductos);
        inputsPrecio.forEach((inp) => inp.removeEventListener("input", filtrarProductos));
        checkboxes.forEach((c) => c.removeEventListener("change", filtrarProductos));
        document.removeEventListener("click", clickHandler);
      };
    }, 400);

    return () => clearTimeout(timer);
  }, [htmlCatalogo, seccion]);

  /* ==========================
     4️⃣ RENDER FINAL
  ========================== */
  return (
    <div className="catalogo-fondo">
      <div
        className="layout-wrapper-react"
        dangerouslySetInnerHTML={{ __html: htmlCatalogo }}
      />
    </div>
  );
}

export default Catalogo;
