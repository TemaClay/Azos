import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout,
    QLineEdit, QLabel, QCheckBox, QTabWidget, QDialog, QFormLayout, QComboBox, QStyledItemDelegate, QDateEdit  
)
from PyQt5.QtCore import QDate

from urllib.parse import urlencode

API_URL = 'http://127.0.0.1:8000/api/equipment/'
TOKEN_URL = 'http://127.0.0.1:8000/token/'



class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, items_dict, parent=None):
        super().__init__(parent)
        self.items_dict = items_dict  # {"Название": id}

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(list(self.items_dict.keys()))
        return editor

    def setEditorData(self, editor, index):
        value = index.data()
        i = editor.findText(value)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value)



class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.resize(300, 120)

        layout = QFormLayout(self)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Логин:", self.username_input)
        layout.addRow("Пароль:", self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.try_login)
        layout.addWidget(self.login_button)

        self.token = None

        

    def try_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        try:
            response = requests.post(TOKEN_URL, data={
                'username': "koptelov", #username
                'password': "K66aercher" #password
            })
            response.raise_for_status()
            tokens = response.json()
            self.token = tokens.get('access')
            self.accept()  # Закрыть диалог с успехом
        except requests.exceptions.RequestException:
            QMessageBox.critical(self, "Ошибка входа", "Неверный логин или пароль")



class SendEquipmentTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.equipment_input = QComboBox()
        self.equipment_dict = {}
        self.destination = QLineEdit()
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate())

        self.application_number = QLineEdit()
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())

        self.receiver = QLineEdit()

        layout.addRow("Оборудование", self.equipment_input)
        layout.addRow("Место назначения", self.destination)
        layout.addRow("Дата начала", self.start_date)
        layout.addRow("Номер заявки", self.application_number)
        layout.addRow("Дата окончания", self.end_date)
        layout.addRow("Ответственный", self.receiver)

        self.load_equipment()


        send_button = QPushButton("Отправить")
        send_button.clicked.connect(self.send_equipment)
        layout.addWidget(send_button)

        self.setLayout(layout)


    def load_equipment(self):
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            # Получаем список оборудования с сервера
            response = requests.get('http://127.0.0.1:8000/api/equipment/', headers=headers)
            response.raise_for_status()
            equipment_list = response.json()

            # Очищаем текущий список в QComboBox
            self.equipment_input.clear()
            self.equipment_dict = {}

            # Проходим по списку и добавляем в QComboBox только доступное оборудование
            for eq in equipment_list:
                status = eq.get("status", {}).get("id")
                if status == 1:  # Только оборудование с доступным статусом (status_id = 1)
                    name = eq.get("name")
                    eq_id = eq.get("id")
                    display_name = f"{eq.get('inventory_number', '')} — {name}"
                    self.equipment_input.addItem(display_name, userData=eq_id)
                    self.equipment_dict[display_name] = eq_id
        except requests.RequestException as e:
            # Ошибка загрузки данных
            QMessageBox.critical(self, "Ошибка загрузки оборудования", str(e))



    def send_equipment(self):
        url = "http://localhost:8000/api/log/"
        headers = {
            'Authorization': f'Bearer {self.parent.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "equipment": self.equipment_input.currentData(),  # Получаем ID оборудования
            "destination": self.destination.text(),
            "start_date_of_using": self.start_date.date().toString("yyyy-MM-dd"),
            "application_number": self.application_number.text(),
            "end_date_of_using": self.end_date.date().toString("yyyy-MM-dd"),
            "name_of_receiver": self.receiver.text()
        }

        try:
            # Отправка данных на сервер
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Если статус код не 200, выбрасывается исключение

            # Оповещение об успешной отправке
            QMessageBox.information(self, "Успех", "Оборудование успешно добавлено в журнал перемещений.")

            # Очистка полей
            self.clear_fields()

            # Перезагружаем оборудование после отправки
            self.load_equipment()  # Обновление списка оборудования, чтобы оно исчезло из списка.

        except requests.exceptions.RequestException as e:
            # Обработка ошибок при отправке
            if response is not None and response.content:
                try:
                    error_message = response.json()
                except Exception:
                    error_message = response.text
            else:
                error_message = str(e)

            # Оповещение об ошибке
            QMessageBox.warning(self, "Ошибка", f"Ошибка добавления:\n{error_message}")



    def clear_fields(self):
        self.equipment_input.setCurrentIndex(0)
        self.destination.clear()
        self.start_date.setDate(QDate.currentDate())
        self.application_number.clear()
        self.end_date.setDate(QDate.currentDate())
        self.receiver.clear()





class ReturnEquipmentTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        # Создаем выпадающий список для выбора оборудования
        self.return_equipment_input = QComboBox()

        # Загружаем оборудование для возврата
        self.load_equipment_for_return()

        # Кнопка для возврата оборудования
        return_button = QPushButton("Принять оборудование")
        return_button.clicked.connect(self.return_equipment)

        # Добавляем виджеты на форму
        layout.addRow("Оборудование для возврата", self.return_equipment_input)
        layout.addWidget(return_button)

        self.setLayout(layout)

    def load_equipment_for_return(self):
        # Загружаем список оборудования с API
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            response = requests.get('http://127.0.0.1:8000/api/equipment/', headers=headers)
            response.raise_for_status()
            equipment_list = response.json()

            # Очищаем старые данные
            self.return_equipment_input.clear()
            self.return_equipment_dict = {}

            # Загружаем оборудование с нужным статусом
            for eq in equipment_list:
                status_id = eq.get("status", {}).get("id")
                if status_id in [2, 3]:  # фильтруем оборудование со статусами 2 и 3
                    name = eq.get("name")
                    eq_id = eq.get("id")
                    self.return_equipment_input.addItem(f"{name} (Инв. номер: {eq.get('inventory_number')})", userData=eq_id)
                    self.return_equipment_dict[name] = eq_id
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка загрузки оборудования для возврата", str(e))

    def return_equipment(self):
        # Получаем ID выбранного оборудования
        selected_equipment_id = self.return_equipment_input.currentData()
        # Получаем все логи для этого оборудования через API
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            # Запрос на получение всех логов для оборудования
            response = requests.get(f'http://127.0.0.1:8000/api/log/', headers=headers)
            response.raise_for_status()
            logs = response.json()

            # Находим последний лог для выбранного оборудования
            latest_log = None
            for log in logs:
                if log['equipment'] == selected_equipment_id:
                    if latest_log is None or log['start_date_of_using'] > latest_log['start_date_of_using']:
                        latest_log = log

            if latest_log is None:
                # Если нет записей в журнале для этого оборудования
                QMessageBox.warning(self, "Ошибка", "Для этого оборудования нет записей.")
                return

            # Обновляем статус оборудования через API
            update_data = {
                'status_id': 1  # Статус "возвращено"
            }
            equipment_update_response = requests.patch(
                f'http://127.0.0.1:8000/api/equipment/{selected_equipment_id}/', 
                json=update_data, 
                headers=headers
            )
            equipment_update_response.raise_for_status()

            # Обновляем дату окончания использования в log через API
            log_update_data = {
                'end_date_of_using': QDate.currentDate().toString("yyyy-MM-dd")
            }
            log_update_response = requests.patch(
                f'http://127.0.0.1:8000/api/log/{latest_log["id"]}/',
                json=log_update_data,
                headers=headers
            )
            log_update_response.raise_for_status()

            QMessageBox.information(self, "Успех", "Оборудование возвращено.")

            # Перезагружаем список оборудования для возврата, чтобы обновить его и исключить возвращенное оборудование
            self.load_equipment_for_return()

        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка возврата оборудования", str(e))









class EquipmentTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.status_dict = {}
        self.location_dict = {}
        self.init_ui()
        

    def init_ui(self):
        layout = QVBoxLayout()
        filter_layout = QHBoxLayout()

        # Фильтры
        self.manager_input = QLineEdit()
        self.manager_input.setPlaceholderText("Ответственный")

        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Дата (YYYY-MM-DD)")

        self.location_input = QComboBox()
        self.location_input.addItem("Любая локация", userData=None)
        self.load_locations()
        self.location_input.currentIndexChanged.connect(self.load_equipment)

        # Новый комбобокс для статусов
        self.status_input = QComboBox()
        self.status_input.addItem("Любой статус", userData=None)
        self.load_statuses()
        self.status_input.currentIndexChanged.connect(self.load_equipment)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск (имя, артикул, инв. номер)")

        self.salvaged_checkbox = QCheckBox("Показать списанные")
        self.salvaged_checkbox.stateChanged.connect(self.load_equipment)

        self.filter_button = QPushButton("Поиск")
        self.filter_button.clicked.connect(self.load_equipment)

        # Добавляем виджеты в layout
        for widget in [self.manager_input, self.date_input, self.location_input, 
                      self.status_input, self.search_input, self.salvaged_checkbox, 
                      self.filter_button]:
            filter_layout.addWidget(widget)

        # Таблица
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.writeoff_button = QPushButton("Списать выбранное")
        self.writeoff_button.clicked.connect(self.writeoff_selected)
        
        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.save_changes)
        
        button_layout.addWidget(self.writeoff_button)
        button_layout.addWidget(self.save_button)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)

        layout.addLayout(filter_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        


    def save_changes(self):
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите оборудование для изменения.")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите изменить {len(selected_rows)} единиц оборудования?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        headers = {
            'Authorization': f'Bearer {self.parent.access_token}',
            'Content-Type': 'application/json'
        }
        success_count = 0

        for row in selected_rows:
            equipment_id = self.table.item(row, 0).text()  # ID в первом столбце
            
            # Получаем полные данные об оборудовании
            try:
                url = f"{API_URL}{equipment_id}/"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                equipment_data = response.json()
            except requests.RequestException as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить данные для ID {equipment_id}: {e}")
                continue

            # Обновляем только измененные поля
            payload = {}
            for col in range(1, self.table.columnCount()):
                key = self.raw_headers[col]  # ключ из API, а не заголовок таблицы
                item = self.table.item(row, col)

                if item is not None:
                    new_value = item.text()

                    if key == "status":
                        old_value = equipment_data.get("status", {}).get("name_of_status", "")
                        if new_value != old_value:
                            status_id = self.status_dict.get(new_value)
                            if status_id:
                                payload["status_id"] = status_id

                    elif key == "default_location":
                        old_value = equipment_data.get("default_location", {}).get("name", "")
                        if new_value != old_value:
                            loc_id = self.location_dict.get(new_value)
                            if loc_id:
                                payload["default_location_id"] = loc_id

                    else:
                        current_value = str(equipment_data.get(key, ""))
                        if new_value != current_value:
                            payload[key] = new_value


            if not payload:
                continue

            try:
                response = requests.patch(url, json=payload, headers=headers)
                response.raise_for_status()
                success_count += 1
            except requests.RequestException as e:
                error_msg = f"Не удалось обновить ID {equipment_id}: {e}"
                if response.status_code == 400:
                    error_msg += f"\nОшибка сервера: {response.text}"
                QMessageBox.warning(self, "Ошибка", error_msg)

        QMessageBox.information(self, "Готово", f"Обновлено {success_count} записей.")
        self.load_equipment()  # Обновляем таблицу

    

    def writeoff_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Выберите оборудование для списания.")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите списать {len(selected_rows)} единиц оборудования?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        headers = {'Authorization': f'Bearer {self.parent.access_token}', 'Content-Type': 'application/json'}
        success_count = 0

        for row in selected_rows:
            equipment_id = self.table.item(row.row(), 0).text()  # предполагается, что id в первом столбце
            try:
                url = f"{API_URL}{equipment_id}/"
                payload = {"status_id": 4}  # статус "списано"
                response = requests.patch(url, json=payload, headers=headers)
                response.raise_for_status()
                success_count += 1
            except requests.RequestException as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось списать ID {equipment_id}: {e}")

        QMessageBox.information(self, "Готово", f"Списано {success_count} записей.")
        self.load_equipment()


    def get_location_id_by_name(self, name):
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            response = requests.get('http://127.0.0.1:8000/api/place/', headers=headers)
            response.raise_for_status()
            places = response.json()
            for place in places:
                if place.get('name') == name:
                    return place.get('id')
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка при поиске локации", str(e))
        return None


    def load_statuses(self):
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            response = requests.get('http://127.0.0.1:8000/api/status/', headers=headers)
            response.raise_for_status()
            statuses = response.json()
            for status in statuses:
                name = status.get("name_of_status")
                status_id = status.get("id")
                self.status_input.addItem(name, userData=status_id)
                self.status_dict[name] = status_id  # сохраняем соответствие
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка загрузки статусов", str(e))



    def load_equipment(self):
        if not self.parent.access_token:
            return

        params = {}
        if self.manager_input.text():
            params['equipment_manager__icontains'] = self.manager_input.text()
        if self.date_input.text():
            params['commissioning_date'] = self.date_input.text()

        if self.location_input.currentData():
            location_id = self.location_input.currentData()
            if location_id:
                params['default_location'] = location_id

        # Добавляем фильтр по статусу
        if self.status_input.currentData():
            status_id = self.status_input.currentData()
            if status_id:
                params['status_id'] = status_id

        if self.search_input.text():
            params['search'] = self.search_input.text()
        
        if self.salvaged_checkbox.isChecked():
            params['show_salvaged'] = 'true'

        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            url = f"{API_URL}?{urlencode(params)}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.populate_table(data)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))

    def populate_table(self, data):
        if not data:
            QMessageBox.information(self, "Информация", "Нет данных для отображения.")
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Отображаемые заголовки
        header_map = {
            "id": "id",
            "article": "Артикул",
            "inventory_number": "Инвентарный номер",
            "name": "Название",
            "default_location": "Базовая локация",
            "status": "Статус",
            "commissioning_date": "Дата ввода в эксплуатацию",
            "location": "Текущая локация",
            "equipment_manager": "Ответственный",
            # добавьте другие поля по необходимости
        }

        headers = list(data[0].keys())
        self.raw_headers = headers
        self.table.setColumnCount(len(headers))
        display_headers = [header_map.get(h, h) for h in headers]
        self.table.setHorizontalHeaderLabels(display_headers)
        self.table.setRowCount(len(data))

        for row_idx, item in enumerate(data):
            for col_idx, key in enumerate(headers):
                value = item.get(key, "")
                if isinstance(value, dict):
                    if key == 'status' and 'name_of_status' in value:
                        value = value['name_of_status']
                    elif key == 'default_location' and 'name' in value:
                        value = value['name']
                    else:
                        value = str(value)
                else:
                    value = str(value)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

        # Установка делегатов — должно быть после headers
        for col_idx, key in enumerate(headers):
            if key == "status":
                self.table.setItemDelegateForColumn(col_idx, ComboBoxDelegate(self.status_dict, self.table))
            elif key == "default_location":
                self.table.setItemDelegateForColumn(col_idx, ComboBoxDelegate(self.location_dict, self.table))

        self.table.resizeColumnsToContents()

        

    def load_locations(self):
        headers = {'Authorization': f'Bearer {self.parent.access_token}'}
        try:
            response = requests.get('http://127.0.0.1:8000/api/place/', headers=headers)
            response.raise_for_status()
            locations = response.json()
            for loc in locations:
                name = loc.get("name")
                loc_id = loc.get("id")
                self.location_input.addItem(name, userData=loc_id)
                self.location_dict[name] = loc_id  # сохраняем соответствие
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка загрузки локаций", str(e))



class AddEquipmentTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Обязательные поля
        self.article_input = QLineEdit()
        self.inv_number_input = QLineEdit()
        self.name_input = QLineEdit()
        self.default_location_combo = QComboBox()
        self.status_combo = QComboBox()  # Добавлен статус

        self.commissioning_date_input = QLineEdit()
        self.location_input = QLineEdit()
        self.manager_input = QLineEdit()

        # Добавляем подсказки для обязательных полей
        layout.addRow("Артикул:", self.article_input)
        layout.addRow("Инвентарный номер:", self.inv_number_input)
        layout.addRow("Название:", self.name_input)
        layout.addRow("Базовая локация:", self.default_location_combo)
        layout.addRow("Статус:", self.status_combo)  # Добавлен статус
        layout.addRow("Дата ввода в эксплуатацию:", self.commissioning_date_input)
        layout.addRow("Текущая локация:", self.location_input)
        layout.addRow("Ответственный:", self.manager_input)

        self.submit_button = QPushButton("Добавить оборудование")
        self.submit_button.clicked.connect(self.submit_data)
        layout.addRow(self.submit_button)

        self.setLayout(layout)

        # Загрузить данные в комбинированные списки
        self.load_combobox_data()

        # Добавление подсказки для обязательных полей
        self.article_input.setStyleSheet("border: 1px solid red;")  # Артикул обязателен
        self.inv_number_input.setStyleSheet("border: 1px solid red;")  # Инв. номер обязателен
        self.name_input.setStyleSheet("border: 1px solid red;")  # Название обязательно

    def load_combobox_data(self):
        # Очистим комбобокс перед загрузкой новых данных
        self.status_combo.clear()
        self.default_location_combo.clear()

         # Сначала добавим пустой элемент в комбобокс статусов
        self.status_combo.addItem("", None)
        self.default_location_combo.addItem("", None)

        headers = {'Authorization': f'Bearer {self.parent.access_token}'}

        # Загрузка базовых локаций
        try:
            response = requests.get('http://127.0.0.1:8000/api/place/', headers=headers)
            response.raise_for_status()
            places = response.json()
            for place in places:
                self.default_location_combo.addItem(place['name'], place['id'])
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить базовые локации: {e}")

        # Загрузка статусов
        try:
            response = requests.get('http://127.0.0.1:8000/api/status/', headers=headers)
            response.raise_for_status()
            statuses = response.json()
            for status in statuses:
                self.status_combo.addItem(status['name_of_status'], status['id'])
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить статусы: {e}")

    def submit_data(self):
        # Проверка обязательных полей
        if not self.article_input.text():
            self.show_error("Артикул обязателен!")
            return

        if not self.inv_number_input.text():
            self.show_error("Инвентарный номер обязателен!")
            return

        if not self.name_input.text():
            self.show_error("Название обязательно!")
            return

        if not self.default_location_combo.currentData():
            self.show_error("Базовая локация обязана быть выбрана!")
            return

        if not self.status_combo.currentData():
            self.show_error("Статус обязателен!")
            return

        url = API_URL
        headers = {
            'Authorization': f'Bearer {self.parent.access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "article": self.article_input.text(),
            "inventory_number": self.inv_number_input.text(),
            "name": self.name_input.text(),
            "default_location_id": self.default_location_combo.currentData(),
            "status_id": self.status_combo.currentData()
        }

        # Добавляем необязательные поля, если они введены
        if self.commissioning_date_input.text():
            payload["commissioning_date"] = self.commissioning_date_input.text()
        if self.location_input.text():
            payload["location"] = self.location_input.text()
        if self.manager_input.text():
            payload["equipment_manager"] = self.manager_input.text()

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            QMessageBox.information(self, "Успех", "Оборудование добавлено успешно.")
            self.clear_fields()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    def clear_fields(self):
        for field in [
            self.article_input, self.inv_number_input, self.name_input,
            self.default_location_combo, self.status_combo,
            self.commissioning_date_input, self.location_input, self.manager_input
        ]:
            if isinstance(field, QLineEdit):
                field.clear()
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)





class EquipmentApp(QWidget):
    def __init__(self, token):
        super().__init__()
        self.access_token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Учёт оборудования")
        self.setGeometry(100, 100, 1200, 700)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()  # ← создаем self.tabs, а не tabs

        self.equipment_tab = EquipmentTab(self)
        self.equipment_tab.load_equipment()
        self.add_equipment_tab = AddEquipmentTab(self)
        self.settings_tab = QLabel("Здесь будут настройки")
        self.sendLogTab = SendEquipmentTab(self)

        self.tabs.addTab(self.equipment_tab, "Список оборудования")
        self.tabs.addTab(self.add_equipment_tab, "Добавить оборудование")
        self.tabs.addTab(self.settings_tab, "Настройки")
        self.tabs.addTab(self.sendLogTab, "Отправка оборудования")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # Верхняя панель с кнопкой выхода
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        logout_btn = QPushButton("⎋")
        logout_btn.setFixedSize(30, 30)
        logout_btn.setToolTip("Выйти")
        logout_btn.clicked.connect(self.logout)

        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        top_bar.addWidget(logout_btn)
        layout.addLayout(top_bar)

        self.return_tab = ReturnEquipmentTab(self)
        self.tabs.addTab(self.return_tab, "Возврат оборудования")


        


    def logout(self):
        self.close()
        main()


    def on_tab_changed(self, index):
        current_widget = self.tabs.widget(index)
        if isinstance(current_widget, EquipmentTab):
            current_widget.load_equipment()
        elif isinstance(current_widget, AddEquipmentTab):
            current_widget.load_combobox_data()


def main():
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        token = login_dialog.token
        window = EquipmentApp(token)
        window.show()
        app.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main()