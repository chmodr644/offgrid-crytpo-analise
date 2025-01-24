import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QDateEdit, QMessageBox)
from PyQt5.QtCore import QDate
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Banco de dados SQLite
DB_NAME = "carteira.db"

# Configurando o banco de dados
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS carteira (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        moeda TEXT,
                        valor_unit REAL,
                        quantidade REAL,
                        data TEXT)''')
    conn.commit()
    conn.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carteira")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        init_db()
        self.load_table_data()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()

        # Formulário de entrada
        form_layout = QHBoxLayout()
        self.moeda_input = QLineEdit()
        self.moeda_input.setPlaceholderText("Moeda")
        self.valor_input = QLineEdit()
        self.valor_input.setPlaceholderText("Valor Unit.")
        self.quantidade_input = QLineEdit()
        self.quantidade_input.setPlaceholderText("Quantidade")
        self.data_input = QDateEdit()
        self.data_input.setCalendarPopup(True)
        self.data_input.setDate(QDate.currentDate())
        self.add_button = QPushButton("Adicionar")
        self.add_button.clicked.connect(self.add_entry)

        form_layout.addWidget(self.moeda_input)
        form_layout.addWidget(self.valor_input)
        form_layout.addWidget(self.quantidade_input)
        form_layout.addWidget(self.data_input)
        form_layout.addWidget(self.add_button)

        # Tabela de exibição
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Moeda", "Valor Unit.", "Quantidade", "Data"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self.update_chart)

        # Botão de exclusão
        self.delete_button = QPushButton("Excluir Selecionado")
        self.delete_button.clicked.connect(self.delete_entry)

        # Gráfico
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Adicionar widgets ao layout principal
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.delete_button)
        main_layout.addWidget(self.canvas)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def add_entry(self):
        moeda = self.moeda_input.text().strip()
        try:
            valor_unit = float(self.valor_input.text().strip())
            quantidade = float(self.quantidade_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valor unitário e quantidade devem ser numéricos.")
            return
        data = self.data_input.date().toString("yyyy-MM-dd")

        if not moeda:
            QMessageBox.warning(self, "Erro", "O campo moeda não pode estar vazio.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carteira (moeda, valor_unit, quantidade, data) VALUES (?, ?, ?, ?)",
                       (moeda, valor_unit, quantidade, data))
        conn.commit()
        conn.close()

        self.load_table_data()
        self.clear_form()

    def load_table_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carteira")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, data in enumerate(row):
                self.table.setItem(row_position, col, QTableWidgetItem(str(data)))

    def delete_entry(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Erro", "Nenhuma linha selecionada.")
            return

        entry_id = int(self.table.item(selected_row, 0).text())
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carteira WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

        self.load_table_data()
        self.ax.clear()
        self.canvas.draw()

    def update_chart(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return

        moeda = self.table.item(selected_row, 1).text()
        valor_unit = float(self.table.item(selected_row, 2).text())
        quantidade = float(self.table.item(selected_row, 3).text())
        valor_total = valor_unit * quantidade

        self.ax.clear()
        self.ax.bar(["Valor Total (R$)"], [valor_total], color=['blue'])
        self.ax.set_title(f"Valor Total em Reais de {moeda}")
        self.canvas.draw()

    def clear_form(self):
        self.moeda_input.clear()
        self.valor_input.clear()
        self.quantidade_input.clear()
        self.data_input.setDate(QDate.currentDate())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
