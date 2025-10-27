PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE carrito_compra (
  id_carrito INTEGER PRIMARY KEY AUTOINCREMENT,
  id_producto_fk INTEGER NOT NULL,
  cantidad INTEGER NOT NULL,
  FOREIGN KEY (id_producto_fk) REFERENCES producto (id_producto) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE categoria (
  id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
  id_inventario_fk INTEGER NOT NULL,
  color TEXT NOT NULL,
  azucar TEXT NOT NULL,
  gas_carbonico TEXT NOT NULL,
  crianza_barrica TEXT NOT NULL,
  FOREIGN KEY (id_inventario_fk) REFERENCES inventario (id_inventario) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE combo (
  id_combo INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_combo TEXT NOT NULL,
  unidades TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_categoria_fk INTEGER NOT NULL,
  FOREIGN KEY (id_categoria_fk) REFERENCES categoria (id_categoria) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE cupon (
  id_cupon INTEGER PRIMARY KEY AUTOINCREMENT,
  codigo TEXT NOT NULL,
  descuento REAL NOT NULL,
  fecha_expiracion DATE NOT NULL,
  activo TEXT DEFAULT NULL,
  id_factura_fk INTEGER NOT NULL,
  FOREIGN KEY (id_factura_fk) REFERENCES factura (id_factura) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE envio (
  id_envio INTEGER PRIMARY KEY AUTOINCREMENT,
  estado TEXT NOT NULL,
  fecha_envio DATETIME DEFAULT NULL
);

CREATE TABLE factura (
  id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
  metodo_pago TEXT NOT NULL,
  estado_pago TEXT NOT NULL
);

CREATE TABLE historial_compra (
  id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
  precio REAL NOT NULL,
  fecha DATETIME NOT NULL,
  FOREIGN KEY (id_historial) REFERENCES factura (id_factura) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE inventario (
  id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
  cantidad INTEGER NOT NULL,
  stock_min INTEGER NOT NULL,
  stock_max INTEGER NOT NULL
);

CREATE TABLE pedido (
  id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
  cantidad INTEGER NOT NULL,
  precio REAL NOT NULL,
  fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
  id_carrito_compra_fk INTEGER NOT NULL,
  FOREIGN KEY (id_carrito_compra_fk) REFERENCES carrito_compra (id_carrito) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE producto (
  id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
  nom_producto TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  precio_unid REAL NOT NULL,
  grado_alcohol REAL NOT NULL,
  tipo_fruto TEXT NOT NULL,
  pais_origen TEXT NOT NULL,
  fecha_ingreso DATETIME NOT NULL,
  id_categoria_fk INTEGER NOT NULL,
  FOREIGN KEY (id_categoria_fk) REFERENCES categoria (id_categoria) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE reseña (
  id_reseña INTEGER PRIMARY KEY AUTOINCREMENT,
  id_producto_fk INTEGER NOT NULL,
  calificacion INTEGER DEFAULT NULL CHECK (calificacion BETWEEN 1 AND 5),
  comentario TEXT DEFAULT NULL,
  fecha DATETIME NOT NULL,
  FOREIGN KEY (id_producto_fk) REFERENCES producto (id_producto) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE rol (
  id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
  tipo_rol TEXT NOT NULL,
  descripcion TEXT NOT NULL
);

CREATE TABLE soporte (
  id_soporte INTEGER PRIMARY KEY AUTOINCREMENT,
  id_usuario_fk INTEGER NOT NULL,
  mensaje TEXT NOT NULL,
  PQRS TEXT NOT NULL,
  estado TEXT DEFAULT 'Abierto',
  fecha DATETIME NOT NULL,
  FOREIGN KEY (id_usuario_fk) REFERENCES usuario (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE usuario (
  id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
  id_rol_fk INTEGER NOT NULL,
  nombre_completo TEXT NOT NULL,
  correo TEXT NOT NULL,
  contraseña TEXT NOT NULL,
  direccion TEXT NOT NULL,
  telefono TEXT NOT NULL,
  fecha_registro DATE NOT NULL,
  FOREIGN KEY (id_rol_fk) REFERENCES rol (id_rol) ON DELETE CASCADE ON UPDATE CASCADE
);

COMMIT;