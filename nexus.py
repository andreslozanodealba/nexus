import datetime
import json
import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Directorio estándar y seguro en el perfil del usuario para almacenar configuraciones y datos
USER_DATA_DIR = os.path.expanduser("~/.nexus_gestion")
os.makedirs(USER_DATA_DIR, exist_ok=True)

DB_USERS_CONFIG = os.path.join(USER_DATA_DIR, "bdd_usuarios_sistema.json")
DB_PRODUCTOS = os.path.join(USER_DATA_DIR, "bdd_productos_global.json")
ADMIN_MASTER_USER = "admin"
ADMIN_MASTER_PASS = "0218"

STYLESHEET_CYBER_MEDICO = """
    QMainWindow, QDialog {
        background-color: #0b0c16;
    }
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #e0f2fe;
    }
    QFrame#sidebar {
        background-color: #1e3a8a;
        border-right: 1px solid #1f2041;
    }
    QLabel {
        color: #e0f2fe;
        font-size: 13px;
    }
    QLineEdit, QComboBox, QTextEdit {
        background-color: #07080f;
        color: #e0f2fe;
        border: 1px solid #1f2041;
        border-radius: 2px;
        padding: 4px 6px;
        font-size: 12px;
    }
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
        border: 1px solid #00f0ff;
    }
    QPushButton {
        background-color: #1e3a8a;
        color: #e0f2fe;
        border: 1px solid #3b82f6;
        border-radius: 2px;
        padding: 4px 8px;
        font-weight: 600;
        font-size: 11px;
    }
    QPushButton:hover {
        background-color: #1d4ed8;
        border: 1px solid #00f0ff;
        color: #00f0ff;
    }
    QTableWidget {
        background-color: #07080f;
        color: #e0f2fe;
        gridline-color: #1f2041;
        border: 1px solid #1f2041;
        selection-background-color: #1a1b35;
        selection-color: #00f0ff;
    }
    QHeaderView::section {
        background-color: #0f1021;
        color: #e0f2fe;
        font-weight: bold;
        padding: 4px;
        border: 1px solid #1f2041;
    }
"""


def cargar_usuarios_sistema():
  if os.path.exists(DB_USERS_CONFIG):
    try:
      with open(DB_USERS_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  data = {
      "usuarios": [
          {"usuario": "admin", "password": ADMIN_MASTER_PASS, "rol": "admin"},
          {"usuario": "admin2", "password": ADMIN_MASTER_PASS, "rol": "admin"},
          {"usuario": "admin3", "password": ADMIN_MASTER_PASS, "rol": "admin"},
          {"usuario": "empleado1", "password": "123", "rol": "empleado"},
          {"usuario": "empleado2", "password": "123", "rol": "empleado"},
      ]
  }
  guardar_usuarios_sistema(data)
  return data


def guardar_usuarios_sistema(data):
  with open(DB_USERS_CONFIG, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


def cargar_productos_global():
  if os.path.exists(DB_PRODUCTOS):
    try:
      with open(DB_PRODUCTOS, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  data = {"inventario": []}
  guardar_productos_global(data)
  return data


def guardar_productos_global(data):
  with open(DB_PRODUCTOS, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


def cargar_db_usuario(username):
  archivo = os.path.join(USER_DATA_DIR, f"bdd_user_{username}.json")
  if os.path.exists(archivo):
    try:
      with open(archivo, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  data = {"clientes": [], "facturas": []}
  guardar_db_usuario(username, data)
  return data


def guardar_db_usuario(username, data):
  archivo = os.path.join(USER_DATA_DIR, f"bdd_user_{username}.json")
  with open(archivo, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)


class InitialRoleDialog(QDialog):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("NEXUS // Selección de Rol")
    self.setFixedSize(380, 220)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)
    self.role_selected = None

    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)

    title = QLabel("SELECCIONE SU ROL")
    title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    btn_admin = QPushButton("🔑 Administrador (Control Total)")
    btn_admin.setFixedHeight(40)
    btn_admin.clicked.connect(lambda: self.seleccionar("admin"))
    layout.addWidget(btn_admin)

    btn_user = QPushButton("👤 Usuario / Empleado")
    btn_user.setFixedHeight(40)
    btn_user.clicked.connect(lambda: self.seleccionar("empleado"))
    layout.addWidget(btn_user)

  def seleccionar(self, rol):
    self.role_selected = rol
    self.accept()


class LoginDialog(QDialog):

  def __init__(self, role):
    super().__init__()
    self.role = role
    self.setWindowTitle(
        f"Autenticación - {'Administrador' if role=='admin' else 'Empleado'}"
    )
    self.setFixedSize(340, 260)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)
    self.authenticated = False
    self.current_user_name = ""
    self.current_user_role = role

    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(8)

    title = QLabel(
        f"ACCESO DE {'ADMIN' if role=='admin' else 'EMPLEADO'}"
    )
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)

    layout.addWidget(QLabel("Usuario:"))
    self.input_user = QLineEdit()
    layout.addWidget(self.input_user)

    layout.addWidget(QLabel("Contraseña:"))
    self.input_pass = QLineEdit()
    self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
    layout.addWidget(self.input_pass)

    layout.addSpacing(5)
    btn_login = QPushButton("Conectar")
    btn_login.setFixedHeight(32)
    btn_login.clicked.connect(self.verificar)
    layout.addWidget(btn_login)

    if role == "empleado":
      btn_reg = QPushButton("Registrarse como Empleado")
      btn_reg.setFixedHeight(30)
      btn_reg.clicked.connect(self.registrar_nuevo_empleado)
      layout.addWidget(btn_reg)

  def verificar(self):
    u = self.input_user.text().strip()
    p = self.input_pass.text().strip()
    sys_data = cargar_usuarios_sistema()

    match = False
    user_role_found = ""
    for usr in sys_data.get("usuarios", []):
      if usr["usuario"] == u and usr["password"] == p:
        match = True
        user_role_found = usr.get("rol", "empleado")
        break

    if match:
      if self.role == "admin" and user_role_found != "admin":
        QMessageBox.warning(
            self, "Error", "Este usuario no tiene permisos de Administrador."
        )
        return
      self.authenticated = True
      self.current_user_name = u
      self.current_user_role = user_role_found
      self.accept()
    else:
      QMessageBox.warning(self, "Error", "Credenciales incorrectas.")

  def registrar_nuevo_empleado(self):
    u = self.input_user.text().strip()
    p = self.input_pass.text().strip()
    if not u or not p:
      QMessageBox.warning(
          self, "Aviso", "Ingrese usuario y contraseña para registrarse."
      )
      return
    sys_data = cargar_usuarios_sistema()
    for usr in sys_data.get("usuarios", []):
      if usr["usuario"] == u:
        QMessageBox.warning(self, "Error", "El usuario ya existe.")
        return
    sys_data["usuarios"].append({"usuario": u, "password": p, "rol": "empleado"})
    guardar_usuarios_sistema(sys_data)
    cargar_db_usuario(u)
    QMessageBox.information(
        self, "Éxito", f"Empleado '{u}' registrado correctamente."
    )


class CambiarPasswordDialog(QDialog):

  def __init__(self, username, parent=None):
    super().__init__(parent)
    self.username = username
    self.setWindowTitle("Cambiar Contraseña")
    self.setFixedSize(340, 200)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(20, 20, 20, 20)

    title = QLabel(f"CAMBIAR CONTRASEÑA: {username}")
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    form = QFormLayout()
    self.inp_nueva = QLineEdit()
    self.inp_nueva.setEchoMode(QLineEdit.EchoMode.Password)
    form.addRow(QLabel("Nueva Contraseña:"), self.inp_nueva)
    layout.addLayout(form)

    btn_guardar = QPushButton("Actualizar Contraseña")
    btn_guardar.clicked.connect(self.guardar)
    layout.addWidget(btn_guardar)

  def guardar(self):
    nueva = self.inp_nueva.text().strip()
    if not nueva:
      QMessageBox.warning(self, "Aviso", "La contraseña no puede estar vacía.")
      return
    sys_data = cargar_usuarios_sistema()
    for usr in sys_data.get("usuarios", []):
      if usr["usuario"] == self.username:
        usr["password"] = nueva
        break
    guardar_usuarios_sistema(sys_data)
    QMessageBox.information(self, "Éxito", "Contraseña actualizada con éxito.")
    self.accept()


class VerBDDexternaDialog(QDialog):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Visor de Registros del Sistema")
    self.setFixedSize(650, 450)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(8)

    title = QLabel("SELECCIONE USUARIO A INSPECCIONAR")
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    top_row = QHBoxLayout()
    self.combo_users = QComboBox()
    sys_data = cargar_usuarios_sistema()
    for u in sys_data.get("usuarios", []):
      self.combo_users.addItem(u["usuario"])
    top_row.addWidget(self.combo_users)

    btn_cargar = QPushButton("Cargar Datos")
    btn_cargar.clicked.connect(self.cargar_datos)
    top_row.addWidget(btn_cargar)
    layout.addLayout(top_row)

    self.tabla_ver = QTableWidget()
    self.tabla_ver.setColumnCount(5)
    self.tabla_ver.setHorizontalHeaderLabels(
        ["ID", "Tipo", "Detalle 1", "Detalle 2", "Detalle 3"]
    )
    header = self.tabla_ver.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(self.tabla_ver)

  def cargar_datos(self):
    usr = self.combo_users.currentText()
    db = cargar_db_usuario(usr)
    self.tabla_ver.setRowCount(0)
    row = 0
    for c in db.get("clientes", []):
      self.tabla_ver.insertRow(row)
      self.tabla_ver.setItem(row, 0, QTableWidgetItem(str(c.get("id", ""))))
      self.tabla_ver.setItem(row, 1, QTableWidgetItem("Cliente"))
      self.tabla_ver.setItem(row, 2, QTableWidgetItem(c.get("nombre", "")))
      self.tabla_ver.setItem(row, 3, QTableWidgetItem(c.get("telefono", "")))
      self.tabla_ver.setItem(row, 4, QTableWidgetItem(c.get("email", "")))
      row += 1
    for f in db.get("facturas", []):
      self.tabla_ver.insertRow(row)
      self.tabla_ver.setItem(row, 0, QTableWidgetItem(str(f.get("id", ""))))
      self.tabla_ver.setItem(row, 1, QTableWidgetItem("Factura"))
      self.tabla_ver.setItem(row, 2, QTableWidgetItem(f.get("cliente", "")))
      self.tabla_ver.setItem(row, 3, QTableWidgetItem(f.get("fecha", "")))
      self.tabla_ver.setItem(row, 4, QTableWidgetItem(f.get("total", "")))
      row += 1


class VerFacturaTxtDialog(QDialog):

  def __init__(self, fac_id, username="", parent=None):
    super().__init__(parent)
    self.fac_id = fac_id
    self.username = username
    self.setWindowTitle(f"Factura Comercial: {fac_id}")
    self.setFixedSize(540, 500)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 15)
    layout.setSpacing(10)

    title = QLabel(f"RECIBO DE FACTURA DIGITAL ({fac_id})")
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    self.txt_view = QTextEdit()
    self.txt_view.setReadOnly(True)
    self.txt_view.setFont(QFont("Courier New", 10))
    layout.addWidget(self.txt_view)

    self.cargar_formato_factura()

    btn_layout = QHBoxLayout()
    btn_exportar = QPushButton("💾 Exportar / Guardar TXT")
    btn_exportar.clicked.connect(self.exportar_factura)
    btn_layout.addWidget(btn_exportar)

    btn_exportar_pdf = QPushButton("📄 Exportar a PDF")
    btn_exportar_pdf.clicked.connect(self.exportar_pdf)
    btn_layout.addWidget(btn_exportar_pdf)

    btn_cerrar = QPushButton("Cerrar")
    btn_cerrar.clicked.connect(self.accept)
    btn_layout.addWidget(btn_cerrar)

    layout.addLayout(btn_layout)

  def cargar_formato_factura(self):
    filename = os.path.join(USER_DATA_DIR, f"factura_{self.fac_id}.xml")
    cliente = "Cliente General"
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = "0.00"
    detalles_items = ""

    if self.username:
      db = cargar_db_usuario(self.username)
      for f in db.get("facturas", []):
        if str(f.get("id")) == str(self.fac_id):
          cliente = f.get("cliente", cliente)
          fecha = f.get("fecha", fecha)
          total = f.get("total", total).replace("$", "")
          items = f.get("items", [])
          for it in items:
            p_nom = it.get("nombre", "Producto")
            p_cant = it.get("cantidad", 1)
            p_prec = float(it.get("precio", 0))
            sub_t = p_cant * p_prec
            detalles_items += f" {p_nom:<35} {p_cant:<5} ${sub_t:,.2f}\n"
          break

    if not detalles_items:
      detalles_items = f" {'Consulta / Servicio General':<35} {1:<5} ${total}\n"

    if os.path.exists(filename):
      try:
        with open(filename, "r", encoding="utf-8") as f:
          factura_estilizada = f"""==================================================
           NEXUS - COMPROBANTE DE FACTURA
==================================================
 N° de Factura : {self.fac_id}
 Emitida por   : {self.username.upper() if self.username else 'SISTEMA'}
 Fecha/Hora    : {fecha}
 Cliente       : {cliente}
--------------------------------------------------
 DESCRIPCIÓN                         CANT  VALOR
--------------------------------------------------
{detalles_items}--------------------------------------------------
 TOTAL A PAGAR                        ${total}
==================================================
 ¡Gracias por su compra!
 Comprobante generado por Nexus.
=================================================="""
          self.txt_view.setPlainText(factura_estilizada)
          return
      except:
        pass

    self.txt_view.setPlainText(
        f"No se pudo cargar el archivo correspondiente a la factura"
        f" {self.fac_id}."
    )

  def exportar_factura(self):
    archivo_guardar, _ = QFileDialog.getSaveFileName(
        self,
        "Exportar Factura",
        f"Factura_{self.fac_id}.txt",
        "Archivos de Texto (*.txt);;Todos los archivos (*.*)",
    )
    if archivo_guardar:
      try:
        with open(archivo_guardar, "w", encoding="utf-8") as f_out:
          f_out.write(self.txt_view.toPlainText())
        QMessageBox.information(
            self,
            "Éxito",
            f"Factura exportada correctamente en:\n{archivo_guardar}",
        )
      except Exception as e:
        QMessageBox.warning(
            self, "Error", f"No se pudo guardar el archivo: {e}"
        )

  def exportar_pdf(self):
    archivo_guardar, _ = QFileDialog.getSaveFileName(
        self,
        "Exportar Factura a PDF",
        f"Factura_{self.fac_id}.pdf",
        "Archivos PDF (*.pdf);;Todos los archivos (*.*)",
    )
    if archivo_guardar:
      try:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(archivo_guardar)

        document = QTextDocument()
        texto_plano = self.txt_view.toPlainText()
        html_content = f"""
        <html>
        <head>
        <style>
            body {{
                background-color: #0b0c16;
                color: #e0f2fe;
                font-family: 'Courier New', monospace;
                padding: 20px;
            }}
            .factura-box {{
                background-color: #07080f;
                border: 2px solid #3b82f6;
                padding: 20px;
                border-radius: 4px;
            }}
            pre {{
                color: #e0f2fe;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }}
        </style>
        </head>
        <body>
        <div class="factura-box">
            <pre>{texto_plano}</pre>
        </div>
        </body>
        </html>
        """
        document.setHtml(html_content)
        document.print_(printer)
        QMessageBox.information(
            self,
            "Éxito",
            f"Factura exportada a PDF con estilos correctamente en:\n{archivo_guardar}",
        )
      except Exception as e:
        QMessageBox.warning(
            self, "Error", f"No se pudo exportar el PDF: {e}"
        )


class RegistrarClienteModal(QDialog):

  def __init__(self, username, cliente_data=None, parent=None):
    super().__init__(parent)
    self.username = username
    self.cliente_data = cliente_data
    self.setWindowTitle(
        "Modificar Cliente" if cliente_data else "Registrar Cliente"
    )
    self.setFixedSize(360, 320)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 15)

    title = QLabel(
        "EDITAR CLIENTE" if cliente_data else "NUEVO CLIENTE"
    )
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    form = QFormLayout()
    self.inp_nombre = QLineEdit()
    self.inp_email = QLineEdit()
    self.inp_tel = QLineEdit()
    self.inp_dir = QLineEdit()

    if cliente_data:
      self.inp_nombre.setText(cliente_data.get("nombre", ""))
      self.inp_email.setText(cliente_data.get("email", ""))
      self.inp_tel.setText(cliente_data.get("telefono", ""))
      self.inp_dir.setText(cliente_data.get("direccion", ""))

    form.addRow(QLabel("Nombre:"), self.inp_nombre)
    form.addRow(QLabel("Email:"), self.inp_email)
    form.addRow(QLabel("Teléfono:"), self.inp_tel)
    form.addRow(QLabel("Dirección:"), self.inp_dir)
    layout.addLayout(form)

    btn_guardar = QPushButton("Guardar Cambios" if cliente_data else "Guardar")
    btn_guardar.clicked.connect(self.guardar)
    layout.addWidget(btn_guardar)

  def guardar(self):
    nombre = self.inp_nombre.text().strip()
    if not nombre:
      QMessageBox.warning(self, "Aviso", "El nombre es obligatorio.")
      return
    db = cargar_db_usuario(self.username)
    if self.cliente_data:
      for c in db.get("clientes", []):
        if c.get("id") == self.cliente_data.get("id"):
          c["nombre"] = nombre
          c["email"] = self.inp_email.text().strip()
          c["telefono"] = self.inp_tel.text().strip()
          c["direccion"] = self.inp_dir.text().strip()
          break
    else:
      new_id = (
          str(
              max(
                  [int(c.get("id", 0)) for c in db.get("clientes", [])]
                  + [0]
              )
              + 1
          )
          if db.get("clientes")
          else "1"
      )
      nuevo = {
          "id": new_id,
          "nombre": nombre,
          "email": self.inp_email.text().strip(),
          "telefono": self.inp_tel.text().strip(),
          "direccion": self.inp_dir.text().strip(),
          "estado": "Activo",
          "fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
      }
      db["clientes"].append(nuevo)
    guardar_db_usuario(self.username, db)
    QMessageBox.information(
        self, "Éxito", "Operación realizada correctamente."
    )
    self.accept()


class RegistrarProductoModal(QDialog):

  def __init__(self, prod_data=None, parent=None):
    super().__init__(parent)
    self.prod_data = prod_data
    self.setWindowTitle(
        "Modificar Producto" if prod_data else "Registrar Producto"
    )
    self.setFixedSize(360, 320)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 15)

    title = QLabel(
        "EDITAR PRODUCTO (GLOBAL)"
        if prod_data
        else "NUEVO PRODUCTO (GLOBAL)"
    )
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    form = QFormLayout()
    self.inp_nombre = QLineEdit()
    self.inp_codigo = QLineEdit()
    self.inp_desc = QLineEdit()
    self.inp_precio = QLineEdit()
    self.inp_cat = QLineEdit()

    if prod_data:
      self.inp_nombre.setText(prod_data.get("nombre", ""))
      self.inp_codigo.setText(prod_data.get("codigo", ""))
      self.inp_desc.setText(prod_data.get("descripcion", ""))
      self.inp_precio.setText(prod_data.get("precio", ""))
      self.inp_cat.setText(prod_data.get("categoria", ""))

    form.addRow(QLabel("Nombre:"), self.inp_nombre)
    form.addRow(QLabel("Código:"), self.inp_codigo)
    form.addRow(QLabel("Descripción:"), self.inp_desc)
    form.addRow(QLabel("Precio ($):"), self.inp_precio)
    form.addRow(QLabel("Categoría:"), self.inp_cat)
    layout.addLayout(form)

    btn_guardar = QPushButton("Guardar Cambios" if prod_data else "Guardar")
    btn_guardar.clicked.connect(self.guardar)
    layout.addWidget(btn_guardar)

  def guardar(self):
    nombre = self.inp_nombre.text().strip()
    precio = self.inp_precio.text().strip()
    if not nombre or not precio:
      QMessageBox.warning(self, "Aviso", "Nombre y precio son obligatorios.")
      return
    db = cargar_productos_global()
    if self.prod_data:
      for p in db.get("inventario", []):
        if p.get("id") == self.prod_data.get("id"):
          p["nombre"] = nombre
          p["codigo"] = self.inp_codigo.text().strip()
          p["descripcion"] = self.inp_desc.text().strip()
          p["precio"] = precio
          p["categoria"] = self.inp_cat.text().strip()
          break
    else:
      new_id = (
          str(
              max(
                  [int(p.get("id", 0)) for p in db.get("inventario", [])]
                  + [0]
              )
              + 1
          )
          if db.get("inventario")
          else "1"
      )
      nuevo = {
          "id": new_id,
          "nombre": nombre,
          "codigo": self.inp_codigo.text().strip(),
          "descripcion": self.inp_desc.text().strip(),
          "precio": precio,
          "categoria": self.inp_cat.text().strip(),
          "estado": "activo",
      }
      db["inventario"].append(nuevo)
    guardar_productos_global(db)
    QMessageBox.information(
        self, "Éxito", "Inventario global actualizado correctamente."
    )
    self.accept()


class GenerarFacturaModal(QDialog):

  def __init__(self, username, parent=None):
    super().__init__(parent)
    self.username = username
    self.setWindowTitle("Generar Factura XML")
    self.setFixedSize(500, 450)
    self.setStyleSheet(STYLESHEET_CYBER_MEDICO)

    layout = QVBoxLayout(self)
    layout.setContentsMargins(15, 15, 15, 15)

    title = QLabel("NUEVA FACTURA (XML)")
    title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    layout.addWidget(title)

    form = QFormLayout()
    self.inp_id = QLineEdit(
        f"FAC-{datetime.datetime.now().strftime('%H%M%S')}"
    )
    
    self.combo_cliente = QComboBox()
    db_usr = cargar_db_usuario(username)
    for c in db_usr.get("clientes", []):
      self.combo_cliente.addItem(c.get("nombre", ""))

    self.combo_producto = QComboBox()
    self.prod_map = []
    db_prod = cargar_productos_global()
    for p in db_prod.get("inventario", []):
      p_nom = p.get("nombre", "")
      p_prec = p.get("precio", "0")
      self.combo_producto.addItem(f"{p_nom} - ${p_prec}")
      self.prod_map.append(p)

    self.inp_cantidad = QLineEdit("1")

    form.addRow(QLabel("ID Factura:"), self.inp_id)
    form.addRow(QLabel("Cliente:"), self.combo_cliente)
    form.addRow(QLabel("Producto:"), self.combo_producto)
    form.addRow(QLabel("Cantidad:"), self.inp_cantidad)
    layout.addLayout(form)

    btn_add_prod = QPushButton("➕ Agregar Producto a la Factura")
    btn_add_prod.clicked.connect(self.agregar_item_factura)
    layout.addWidget(btn_add_prod)

    self.tabla_items = QTableWidget()
    self.tabla_items.setColumnCount(4)
    self.tabla_items.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio Unit.", "Subtotal"])
    self.tabla_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(self.tabla_items)

    self.items_seleccionados = []

    btn_guardar = QPushButton("Guardar Factura XML")
    btn_guardar.clicked.connect(self.guardar)
    layout.addWidget(btn_guardar)

  def agregar_item_factura(self):
    idx = self.combo_producto.currentIndex()
    if idx < 0 or idx >= len(self.prod_map):
      return
    prod = self.prod_map[idx]
    try:
      cant = int(self.inp_cantidad.text().strip())
      if cant <= 0:
        raise ValueError()
    except:
      QMessageBox.warning(self, "Aviso", "Cantidad inválida.")
      return

    try:
      precio = float(str(prod.get("precio", "0")).replace(",", ""))
    except:
      precio = 0.0

    subtotal = cant * precio
    self.items_seleccionados.append({
        "nombre": prod.get("nombre", ""),
        "cantidad": cant,
        "precio": precio,
        "subtotal": subtotal
    })

    r = self.tabla_items.rowCount()
    self.tabla_items.insertRow(r)
    self.tabla_items.setItem(r, 0, QTableWidgetItem(prod.get("nombre", "")))
    self.tabla_items.setItem(r, 1, QTableWidgetItem(str(cant)))
    self.tabla_items.setItem(r, 2, QTableWidgetItem(f"${precio:,.2f}"))
    self.tabla_items.setItem(r, 3, QTableWidgetItem(f"${subtotal:,.2f}"))

  def guardar(self):
    fac_id = self.inp_id.text().strip()
    cliente = self.combo_cliente.currentText().strip()
    if not fac_id or not cliente:
      QMessageBox.warning(self, "Aviso", "ID y cliente son obligatorios.")
      return
    if not self.items_seleccionados:
      QMessageBox.warning(self, "Aviso", "Debe agregar al menos un producto.")
      return

    total_val = sum(item["subtotal"] for item in self.items_seleccionados)
    total_str = f"{total_val:,.2f}"

    db = cargar_db_usuario(self.username)

    for f in db.get("facturas", []):
      if str(f.get("id")) == str(fac_id):
        QMessageBox.warning(
            self,
            "Error",
            f"Ya existe una factura con el ID '{fac_id}'.",
        )
        return

    filename = os.path.join(USER_DATA_DIR, f"factura_{fac_id}.xml")
    if os.path.exists(filename):
      QMessageBox.warning(
          self,
          "Error",
          f"Ya existe un archivo físico '{filename}' en la carpeta de datos del usuario.",
      )
      return

    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    items_xml_str = ""
    for it in self.items_seleccionados:
      items_xml_str += f"    <Item>\n        <Nombre>{it['nombre']}</Nombre>\n        <Cantidad>{it['cantidad']}</Cantidad>\n        <PrecioUnitario>{it['precio']}</PrecioUnitario>\n        <Subtotal>{it['subtotal']}</Subtotal>\n    </Item>\n"

    contenido_xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<Factura>\n"
        f"    <IdFactura>{fac_id}</IdFactura>\n"
        f"    <UsuarioSistema>{self.username}</UsuarioSistema>\n"
        f"    <Cliente>{cliente}</Cliente>\n"
        f"    <FechaEmision>{fecha_actual}</FechaEmision>\n"
        f"    <Items>\n{items_xml_str}    </Items>\n"
        f"    <Total monto='{total_str}'>${total_str}</Total>\n"
        f"</Factura>\n"
    )
    try:
      with open(filename, "w", encoding="utf-8") as f_out:
        f_out.write(contenido_xml)
    except Exception as e:
      QMessageBox.warning(
          self, "Error", f"No se pudo guardar el archivo XML físico: {e}"
      )
      return

    nueva = {
        "id": fac_id,
        "cliente": cliente,
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
        "total": f"${total_str}",
        "items": self.items_seleccionados
    }
    db["facturas"].append(nueva)
    guardar_db_usuario(self.username, db)
    QMessageBox.information(
        self,
        "Éxito",
        f"Factura guardada y archivo XML '{filename}' creado con éxito.",
    )
    self.accept()


class NexusApp(QMainWindow):

  def __init__(self, role="admin", username="admin"):
    super().__init__()
    self.role = role
    self.username = username
    self.setWindowTitle(
        f"NEXUS // ROL: {role.upper()} - USUARIO: {username}"
    )
    self.resize(1100, 650)
    self.setMinimumSize(850, 500)
    self.switch_to_login = False
    self.sidebar_visible = True
    self.init_ui()

  def init_ui(self):
    main_w = QWidget()
    main_w.setStyleSheet(STYLESHEET_CYBER_MEDICO)
    root_lay = QHBoxLayout(main_w)
    root_lay.setContentsMargins(0, 0, 0, 0)
    root_lay.setSpacing(0)

    self.sidebar = QFrame()
    self.sidebar.setObjectName("sidebar")
    self.sidebar.setFixedWidth(210)
    side_lay = QVBoxLayout(self.sidebar)
    side_lay.setContentsMargins(10, 15, 10, 15)
    side_lay.setSpacing(8)

    lbl_menu = QLabel("NEXUS MENÚ")
    lbl_menu.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    side_lay.addWidget(lbl_menu)

    side_lay.addSpacing(10)

    self.btn_cli_nav = QPushButton("👥 Clientes")
    self.btn_cli_nav.clicked.connect(lambda: self.stack.setCurrentIndex(0))
    side_lay.addWidget(self.btn_cli_nav)

    self.btn_inv_nav = QPushButton("📦 Inventario")
    self.btn_inv_nav.clicked.connect(lambda: self.stack.setCurrentIndex(1))
    side_lay.addWidget(self.btn_inv_nav)

    self.btn_fac_nav = QPushButton("💳 Facturación")
    self.btn_fac_nav.clicked.connect(lambda: self.stack.setCurrentIndex(2))
    side_lay.addWidget(self.btn_fac_nav)

    side_lay.addSpacing(5)

    btn_pass = QPushButton("🔑 Cambiar Clave")
    btn_pass.clicked.connect(self.abrir_cambiar_pass)
    side_lay.addWidget(btn_pass)

    if self.role == "admin":
      btn_ver_db = QPushButton("📂 Ver Registros")
      btn_ver_db.clicked.connect(lambda: VerBDDexternaDialog(self).exec())
      side_lay.addWidget(btn_ver_db)

    side_lay.addStretch()

    btn_logout = QPushButton("🔒 Cerrar Sesión")
    btn_logout.clicked.connect(self.cerrar_sesion)
    side_lay.addWidget(btn_logout)

    root_lay.addWidget(self.sidebar)

    content_frame = QWidget()
    content_lay = QVBoxLayout(content_frame)
    content_lay.setContentsMargins(0, 0, 0, 0)
    content_lay.setSpacing(0)

    top_bar = QFrame()
    top_bar.setFixedHeight(40)
    top_bar.setStyleSheet(
        "background-color: #0f1021; border-bottom: 1px solid #1f2041;"
    )
    tb_lay = QHBoxLayout(top_bar)
    tb_lay.setContentsMargins(10, 0, 10, 0)

    self.btn_toggle = QPushButton("☰ Menú")
    self.btn_toggle.setFixedWidth(70)
    self.btn_toggle.clicked.connect(self.toggle_sidebar)
    tb_lay.addWidget(self.btn_toggle)
    tb_lay.addSpacing(10)

    lbl_title_top = QLabel(
        f"NEXUS  SESIÓN ACTIVA: {self.username.upper()} ({self.role.upper()})"
    )
    tb_lay.addWidget(lbl_title_top)
    content_lay.addWidget(top_bar)

    self.stack = QStackedWidget()
    self.stack.setStyleSheet(
        "QStackedWidget { background-color: #0b0c16; border: none; }"
    )
    self.stack.addWidget(self.crear_vista_clientes())
    self.stack.addWidget(self.crear_vista_inventario())
    self.stack.addWidget(self.crear_vista_facturacion())
    content_lay.addWidget(self.stack)

    footer = QFrame()
    footer.setFixedHeight(24)
    footer.setStyleSheet(
        "background-color: #0f1021; border-top: 1px solid #1f2041;"
    )
    f_lay = QHBoxLayout(footer)
    f_lay.setContentsMargins(10, 0, 10, 0)
    lbl_foot = QLabel("NEXUS // SISTEMA MULTI-USUARIO")
    lbl_foot.setStyleSheet("font-size: 9px; color: #8a99ad;")
    f_lay.addWidget(lbl_foot)
    content_lay.addWidget(footer)

    root_lay.addWidget(content_frame)
    self.setCentralWidget(main_w)

  def toggle_sidebar(self):
    self.sidebar_visible = not self.sidebar_visible
    self.sidebar.setVisible(self.sidebar_visible)

  def cerrar_sesion(self):
    self.switch_to_login = True
    self.close()

  def abrir_cambiar_pass(self):
    CambiarPasswordDialog(self.username, self).exec()

  def configurar_tabla(self, tabla, indice):
    header = tabla.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    if indice in [1, 3]:
      tabla.setStyleSheet(
          "QTableWidget { background-color: #0c0e1a; color: #e0f2fe;"
          " alternate-background-color: #11152d; gridline-color: #1f2041;"
          " border: 1px solid #1f2041; selection-background-color: #1a1b35;"
          " selection-color: #00f0ff; }"
      )
    else:
      tabla.setStyleSheet(
          "QTableWidget { background-color: #07080f; color: #e0f2fe;"
          " alternate-background-color: #0b0c16; gridline-color: #1f2041;"
          " border: 1px solid #1f2041; selection-background-color: #1a1b35;"
          " selection-color: #00f0ff; }"
      )
    tabla.setAlternatingRowColors(True)

  def crear_vista_clientes(self):
    w = QWidget()
    w.setStyleSheet("background-color: #0b0c16;")
    main_lay = QVBoxLayout(w)
    main_lay.setContentsMargins(8, 8, 8, 8)

    card = QFrame()
    card.setStyleSheet(
        "QFrame { background-color: #0b0c16; border: 1px solid #1f2041;"
        " border-radius: 6px; }"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(10, 10, 10, 10)
    lay.setSpacing(6)

    top_row = QHBoxLayout()
    lbl_sec = QLabel(f"GESTIÓN DE CLIENTES  {self.username.upper()}")
    lbl_sec.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    top_row.addWidget(lbl_sec)
    top_row.addStretch()

    self.search_cli = QLineEdit()
    self.search_cli.setPlaceholderText("🔍 Buscar por ID o Nombre...")
    self.search_cli.setFixedWidth(200)
    self.search_cli.textChanged.connect(self.poblar_tabla_clientes)
    top_row.addWidget(self.search_cli)

    btn_reg = QPushButton("Registrar Cliente 👤+")
    btn_reg.clicked.connect(self.abrir_modal_cliente)
    top_row.addWidget(btn_reg)
    lay.addLayout(top_row)

    self.t_cli = QTableWidget()
    self.t_cli.setColumnCount(8)
    self.t_cli.setHorizontalHeaderLabels([
        "ID",
        "Nombre",
        "Email",
        "Teléfono",
        "Dirección",
        "Estado",
        "Fecha",
        "Acciones",
    ])
    self.configurar_tabla(self.t_cli, 1)
    self.poblar_tabla_clientes()
    lay.addWidget(self.t_cli)

    main_lay.addWidget(card)
    return w

  def abrir_modal_cliente(self):
    dlg = RegistrarClienteModal(self.username, None, self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
      self.poblar_tabla_clientes()

  def modificar_cliente(self, cliente_id):
    db = cargar_db_usuario(self.username)
    cli_obj = None
    for c in db.get("clientes", []):
      if str(c.get("id")) == str(cliente_id):
        cli_obj = c
        break
    if cli_obj:
      dlg = RegistrarClienteModal(self.username, cli_obj, self)
      if dlg.exec() == QDialog.DialogCode.Accepted:
        self.poblar_tabla_clientes()

  def borrar_cliente(self, cliente_id):
    resp = QMessageBox.question(
        self,
        "Confirmar",
        "¿Está seguro de eliminar este cliente?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if resp == QMessageBox.StandardButton.Yes:
      db = cargar_db_usuario(self.username)
      db["clientes"] = [
          c for c in db.get("clientes", []) if str(c.get("id")) != str(cliente_id)
      ]
      guardar_db_usuario(self.username, db)
      self.poblar_tabla_clientes()

  def poblar_tabla_clientes(self):
    db = cargar_db_usuario(self.username)
    filtro = (
        self.search_cli.text().strip().lower()
        if hasattr(self, "search_cli")
        else ""
    )
    self.t_cli.setRowCount(0)
    for r, c in enumerate(db.get("clientes", [])):
      cid = str(c.get("id", ""))
      nombre = c.get("nombre", "")
      if filtro and (
          filtro not in cid.lower() and filtro not in nombre.lower()
      ):
        continue

      row = self.t_cli.rowCount()
      self.t_cli.insertRow(row)
      self.t_cli.setItem(row, 0, QTableWidgetItem(cid))
      self.t_cli.setItem(row, 1, QTableWidgetItem(nombre))
      self.t_cli.setItem(row, 2, QTableWidgetItem(c.get("email", "")))
      self.t_cli.setItem(row, 3, QTableWidgetItem(c.get("telefono", "")))
      self.t_cli.setItem(row, 4, QTableWidgetItem(c.get("direccion", "")))
      self.t_cli.setItem(row, 5, QTableWidgetItem(c.get("estado", "")))
      self.t_cli.setItem(row, 6, QTableWidgetItem(c.get("fecha", "")))

      btn_w = QWidget()
      blayout = QHBoxLayout(btn_w)
      blayout.setContentsMargins(1, 1, 1, 1)
      blayout.setSpacing(3)
      btn_mod = QPushButton("Modificar")
      btn_del = QPushButton("Borrar")
      btn_mod.clicked.connect(lambda _, x=cid: self.modificar_cliente(x))
      btn_del.clicked.connect(lambda _, x=cid: self.borrar_cliente(x))
      blayout.addWidget(btn_mod)
      blayout.addWidget(btn_del)
      self.t_cli.setCellWidget(row, 7, btn_w)

  def crear_vista_inventario(self):
    w = QWidget()
    w.setStyleSheet("background-color: #0b0c16;")
    main_lay = QVBoxLayout(w)
    main_lay.setContentsMargins(8, 8, 8, 8)

    card = QFrame()
    card.setStyleSheet(
        "QFrame { background-color: #0b0c16; border: 1px solid #1f2041;"
        " border-radius: 6px; }"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(10, 10, 10, 10)
    lay.setSpacing(6)

    top_row = QHBoxLayout()
    lbl_sec = QLabel("INVENTARIO GENERAL")
    lbl_sec.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    top_row.addWidget(lbl_sec)
    top_row.addStretch()

    self.search_inv = QLineEdit()
    self.search_inv.setPlaceholderText("🔍 Buscar por ID o Nombre...")
    self.search_inv.setFixedWidth(200)
    self.search_inv.textChanged.connect(self.poblar_tabla_inventario)
    top_row.addWidget(self.search_inv)

    btn_reg = QPushButton("Registrar Producto 📦+")
    btn_reg.clicked.connect(self.abrir_modal_producto)
    top_row.addWidget(btn_reg)
    lay.addLayout(top_row)

    self.t_inv = QTableWidget()
    self.t_inv.setColumnCount(8)
    self.t_inv.setHorizontalHeaderLabels([
        "ID",
        "Nombre",
        "Código",
        "Descripción",
        "Precio",
        "Categoría",
        "Estado",
        "Acciones",
    ])
    self.configurar_tabla(self.t_inv, 2)
    self.poblar_tabla_inventario()
    lay.addWidget(self.t_inv)

    main_lay.addWidget(card)
    return w

  def abrir_modal_producto(self):
    dlg = RegistrarProductoModal(None, self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
      self.poblar_tabla_inventario()

  def modificar_producto(self, prod_id):
    db = cargar_productos_global()
    p_obj = None
    for p in db.get("inventario", []):
      if str(p.get("id")) == str(prod_id):
        p_obj = p
        break
    if p_obj:
      dlg = RegistrarProductoModal(p_obj, self)
      if dlg.exec() == QDialog.DialogCode.Accepted:
        self.poblar_tabla_inventario()

  def borrar_producto(self, prod_id):
    resp = QMessageBox.question(
        self,
        "Confirmar",
        "¿Está seguro de eliminar este producto del inventario?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if resp == QMessageBox.StandardButton.Yes:
      db = cargar_productos_global()
      db["inventario"] = [
          p
          for p in db.get("inventario", [])
          if str(p.get("id")) != str(prod_id)
      ]
      guardar_productos_global(db)
      self.poblar_tabla_inventario()

  def poblar_tabla_inventario(self):
    db = cargar_productos_global()
    filtro = (
        self.search_inv.text().strip().lower()
        if hasattr(self, "search_inv")
        else ""
    )
    self.t_inv.setRowCount(0)
    for r, p in enumerate(db.get("inventario", [])):
      pid = str(p.get("id", ""))
      nombre = p.get("nombre", "")
      if filtro and (
          filtro not in pid.lower() and filtro not in nombre.lower()
      ):
        continue

      row = self.t_inv.rowCount()
      self.t_inv.insertRow(row)
      self.t_inv.setItem(row, 0, QTableWidgetItem(pid))
      self.t_inv.setItem(row, 1, QTableWidgetItem(nombre))
      self.t_inv.setItem(row, 2, QTableWidgetItem(p.get("codigo", "")))
      self.t_inv.setItem(row, 3, QTableWidgetItem(p.get("descripcion", "")))
      self.t_inv.setItem(row, 4, QTableWidgetItem(f"${p.get('precio', '')}"))
      self.t_inv.setItem(row, 5, QTableWidgetItem(p.get("categoria", "")))
      self.t_inv.setItem(row, 6, QTableWidgetItem(p.get("estado", "")))

      btn_w = QWidget()
      blayout = QHBoxLayout(btn_w)
      blayout.setContentsMargins(1, 1, 1, 1)
      blayout.setSpacing(3)
      btn_mod = QPushButton("Modificar")
      btn_del = QPushButton("Borrar")
      btn_mod.clicked.connect(lambda _, x=pid: self.modificar_producto(x))
      btn_del.clicked.connect(lambda _, x=pid: self.borrar_producto(x))
      blayout.addWidget(btn_mod)
      blayout.addWidget(btn_del)
      self.t_inv.setCellWidget(row, 7, btn_w)

  def crear_vista_facturacion(self):
    w = QWidget()
    w.setStyleSheet("background-color: #0b0c16;")
    main_lay = QVBoxLayout(w)
    main_lay.setContentsMargins(8, 8, 8, 8)

    card = QFrame()
    card.setStyleSheet(
        "QFrame { background-color: #0b0c16; border: 1px solid #1f2041;"
        " border-radius: 6px; }"
    )
    lay = QVBoxLayout(card)
    lay.setContentsMargins(10, 10, 10, 10)
    lay.setSpacing(6)

    top_row = QHBoxLayout()
    lbl_sec = QLabel(f"FACTURACIÓN  {self.username.upper()}")
    lbl_sec.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    top_row.addWidget(lbl_sec)
    top_row.addStretch()

    self.search_fac = QLineEdit()
    self.search_fac.setPlaceholderText("🔍 Buscar por ID o Cliente...")
    self.search_fac.setFixedWidth(200)
    self.search_fac.textChanged.connect(self.poblar_tabla_facturacion)
    top_row.addWidget(self.search_fac)

    btn_fac = QPushButton("Generar Factura XML 💳")
    btn_fac.clicked.connect(self.abrir_modal_factura)
    top_row.addWidget(btn_fac)
    lay.addLayout(top_row)

    self.t_fac = QTableWidget()
    self.t_fac.setColumnCount(5)
    self.t_fac.setHorizontalHeaderLabels(
        ["ID Factura", "Cliente", "Fecha", "Total", "Acciones"]
    )
    self.configurar_tabla(self.t_fac, 3)
    self.poblar_tabla_facturacion()
    lay.addWidget(self.t_fac)

    main_lay.addWidget(card)
    return w

  def abrir_modal_factura(self):
    dlg = GenerarFacturaModal(self.username, self)
    if dlg.exec() == QDialog.DialogCode.Accepted:
      self.poblar_tabla_facturacion()

  def ver_factura_archivo(self, fac_id):
    VerFacturaTxtDialog(fac_id, self.username, self).exec()

  def borrar_factura(self, fac_id):
    resp = QMessageBox.question(
        self,
        "Confirmar",
        "¿Está seguro de eliminar esta factura?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if resp == QMessageBox.StandardButton.Yes:
      db = cargar_db_usuario(self.username)
      db["facturas"] = [
          f for f in db.get("facturas", []) if str(f.get("id")) != str(fac_id)
      ]
      guardar_db_usuario(self.username, db)
      filename = os.path.join(USER_DATA_DIR, f"factura_{fac_id}.xml")
      if os.path.exists(filename):
        try:
          os.remove(filename)
        except:
          pass
      self.poblar_tabla_facturacion()

  def poblar_tabla_facturacion(self):
    db = cargar_db_usuario(self.username)
    filtro = (
        self.search_fac.text().strip().lower()
        if hasattr(self, "search_fac")
        else ""
    )
    self.t_fac.setRowCount(0)
    for r, f in enumerate(db.get("facturas", [])):
      fid = str(f.get("id", ""))
      cliente = f.get("cliente", "")
      if filtro and (
          filtro not in fid.lower() and filtro not in cliente.lower()
      ):
        continue

      row = self.t_fac.rowCount()
      self.t_fac.insertRow(row)
      self.t_fac.setItem(row, 0, QTableWidgetItem(fid))
      self.t_fac.setItem(row, 1, QTableWidgetItem(cliente))
      self.t_fac.setItem(row, 2, QTableWidgetItem(f.get("fecha", "")))
      self.t_fac.setItem(row, 3, QTableWidgetItem(f.get("total", "")))

      btn_w = QWidget()
      blayout = QHBoxLayout(btn_w)
      blayout.setContentsMargins(1, 1, 1, 1)
      blayout.setSpacing(3)
      btn_ver = QPushButton("Ver Factura")
      btn_del = QPushButton("Borrar")
      btn_ver.clicked.connect(lambda _, x=fid: self.ver_factura_archivo(x))
      btn_del.clicked.connect(lambda _, x=fid: self.borrar_factura(x))
      blayout.addWidget(btn_ver)
      blayout.addWidget(btn_del)
      self.t_fac.setCellWidget(row, 4, btn_w)


if __name__ == "__main__":
  app = QApplication(sys.argv)
  while True:
    role_dlg = InitialRoleGrid() if 'InitialRoleGrid' in globals() else InitialRoleDialog()
    if role_dlg.exec() == QDialog.DialogCode.Accepted and role_dlg.role_selected:
      rol = role_dlg.role_selected
      login_dlg = LoginDialog(rol)
      if (
          login_dlg.exec() == QDialog.DialogCode.Accepted
          and login_dlg.authenticated
      ):
        main_window = NexusApp(
            role=login_dlg.current_user_role, username=login_dlg.current_user_name
        )
        main_window.show()
        app.exec()
        if main_window.switch_to_login:
          continue
        else:
          break
      else:
        continue
    else:
      break
  sys.exit(0)
