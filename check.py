import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt, QSize


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('PyQt QTreeWidget')
        self.setGeometry(100, 100, 400, 200)

        # tree
        tree = QTreeWidget(self)
        tree.setColumnCount(3)
        tree.setHeaderLabels(['Departments', 'Employees'])

        tree.header().resizeSection(2, 80)

        departments = ['Sales', 'Marketing', 'HR']
        employees = {
            'Sales': ['John', 'Jane', 'Peter'],
            'Marketing': ['Alice', 'Bob'],
            'HR': ['David'],
        }

        # addition data to the tree
        for department in departments:
            department_item = QTreeWidgetItem(tree)
            department_item.setText(0, department)
            # set the child
            for employee in employees[department]:
                employee_item = QTreeWidgetItem(tree)
                employee_item.setText(1, employee)

                department_item.addChild(employee_item)

        # place the tree on the main window
        self.setCentralWidget(tree)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
