import mysql.connector as sql
import pandas as pd
import traceback
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from layout import Ui_MainWindow

# Connection details
hostname = 'Jan-PC'
port = 3306  # Default MySQL port
database = 'practice'
username = input('UN: ')
password = input('PW: ')


class SQLConnector:
    def __init__(self):
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
        self.sql_connector = SQLConnector()

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
