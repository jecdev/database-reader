import mysql.connector as sql
import pandas as pd
import traceback
import sys
from PyQt5.QtWidgets import *
from layout import Ui_MainWindow


class ConnectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Connection")

        # Layouts
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # Input fields
        self.hostname_input = QLineEdit()
        self.hostname_input.setText("JAN-PC")

        self.port_input = QLineEdit()
        self.port_input.setText("3306")

        self.database_input = QLineEdit()
        self.database_input.setText("practice")

        self.username_input = QLineEdit()
        self.username_input.setText("jdacayan")

        self.password_input = QLineEdit()
        self.password_input.setText("")  # Set default password (empty)

        self.password_input.setEchoMode(QLineEdit.Password)

        # Add fields to the form layout
        self.form_layout.addRow("Hostname:", self.hostname_input)
        self.form_layout.addRow("Port:", self.port_input)
        self.form_layout.addRow("Database:", self.database_input)
        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)

        # Dialog buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        #Clear
        self.clear_button = QPushButton("Clear")
        self.buttons.addButton(self.clear_button, QDialogButtonBox.ResetRole)
        self.clear_button.clicked.connect(self.clear_inputs)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Add the form layout and buttons to the main layout
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def clear_inputs(self):
        """Clears all input fields."""
        self.hostname_input.clear()
        self.port_input.clear()
        self.database_input.clear()
        self.username_input.clear()
        self.password_input.clear()

    def getInputs(self):
        hostname = self.hostname_input.text()
        port = self.port_input.text()
        database = self.database_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        return hostname, port, database, username, password


class SQLConnector:
    def __init__(self, hostname, port, database, username, password):
        self.connection = sql.connect(
            host=hostname,
            port=port,
            user=username,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def execute(self, query):
        if any(keyword in query.upper() for keyword in ["INSERT", "DELETE", "UPDATE"]):
            self.cursor.execute(query)
            return None, query
        else:
            df = pd.read_sql(query, self.connection)
            return df, query


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        connection_dialog = ConnectionDialog()
        if connection_dialog.exec_() == QDialog.Accepted:
            hostname, port, database, username, password = connection_dialog.getInputs()
            self.sql_connector = SQLConnector(hostname, port, database, username, password)
        else:
            sys.exit(0)

        # Connect button to the query execution
        self.pushButton.clicked.connect(self.execute_query)
        self.commitButton.clicked.connect(self.commit_query)

    def commit_query(self):
        try:
            self.sql_connector.connection.commit()
            self.statusbar.showMessage("Commit successful.")
        except Exception as e:
            self.statusbar.showMessage(f"Commit error: {e}")
            print(e)

    def execute_query(self):
        query = self.lineEdit.toPlainText()  # Use toPlainText for QTextEdit
        try:
            output, executed_query = self.sql_connector.execute(query)
            self.statusbar.showMessage(f"Executed query: {executed_query}")
            if output is None:
                self.statusbar.showMessage("Database updated. Showing results.. Click Commit to save changes.")
                output = self.sql_connector.execute("SELECT * FROM details")[0]
                self.display_results(output)
            else:
                self.display_results(output)
        except Exception as e:
            self.statusbar.showMessage(f"An error occurred: {e}")
            traceback.print_exc()

    def display_results(self, df):
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)
        print(df)
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(df.iloc[i, j])))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
