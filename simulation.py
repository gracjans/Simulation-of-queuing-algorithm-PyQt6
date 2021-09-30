import time
import random

from datetime import timedelta

from simulation_GUI import Ui_MainWindow

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dialog_font = QFont()
        self.dialog_font.setPointSize(11)

        self.start_time = time.time()

        self.timer_clients = QTimer()
        self.function_timer_clients()

        self.disc1 = Disc(1)
        self.disc2 = Disc(2)
        self.disc3 = Disc(3)
        self.disc4 = Disc(4)
        self.disc5 = Disc(5)
        self.active_discs = [self.disc1, self.disc2, self.disc3, self.disc4, self.disc5]

        self.timer_discs = QTimer()
        self.function_timer_discs()

        self.actual_id = 0
        self.active_clients = []
        self.client_count = 0
        self.ui.ClientsTextBrowser.setText(str(self.client_count))

        self.service_time = 10
        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))

        self.frequency = 0
        self.ui.FrequencyTextBrowser.setText(str(self.frequency))

        self.priority_top = {'NaN0': 0,
                             'NaN1': 0,
                             'NaN2': 0,
                             'NaN3': 0,
                             'NaN4': 0}
        self.NaN_counter = 4

        self.count_minute = 0

        self.ui.AddClientButton.clicked.connect(lambda: self.add_client(self.actual_id))

    def add_client(self, actual_id):
        client = Client(actual_id)
        self.active_clients.append(client)

        if client.files_count == 1:
            files_size = str(client.file1_size)
        elif client.files_count == 2:
            files_size = str(client.file1_size) + ', ' + str(client.file2_size)
        elif client.files_count == 3:
            files_size = str(client.file1_size) + ', ' + str(client.file2_size) + ', ' + str(client.file3_size)

        rowPosition = self.ui.ClientsTable.rowCount()
        self.ui.ClientsTable.insertRow(rowPosition)
        self.ui.ClientsTable.setItem(rowPosition, 0, QTableWidgetItem(str(client.id)))
        self.ui.ClientsTable.setItem(rowPosition, 1, QTableWidgetItem(str(files_size)))
        self.ui.ClientsTable.setItem(rowPosition, 2, QTableWidgetItem(str(client.waiting_time)))
        self.ui.ClientsTable.setItem(rowPosition, 3, QTableWidgetItem(str(client.priority)))
        self.ui.ClientsTable.scrollToBottom()
        self.ui.ClientsTextBrowser.setText(str(len(self.active_clients)))

        self.client_count += 1
        self.actual_id += 1

    def function_timer_clients(self):
        self.timer_clients.setInterval(1000)
        self.timer_clients.timeout.connect(self.recurring_timer_clients)
        self.timer_clients.start()

    def recurring_timer_clients(self):
        for client in self.active_clients:
            client.update_time()
            self.ui.ClientsTable.setItem(client.id, 2, QTableWidgetItem(str(client.waiting_time)))

            self.priority_algorithm(client)
            self.ui.ClientsTable.setItem(client.id, 3, QTableWidgetItem(str(client.priority)))

            self.check_priority_top(client)
            self.refresh_priority_top(client)

        self.refresh_table_top(self.priority_top)

    def function_timer_discs(self):
        self.timer_discs.setInterval(1000)
        self.timer_discs.timeout.connect(self.recurring_timer_discs)
        self.timer_discs.start()

    def recurring_timer_discs(self):
        self.count_minute += 1
        if self.count_minute > 30:
            self.frequency -= 5
            if self.frequency < 0:
                self.frequency = 0
            self.ui.FrequencyTextBrowser.setText(str(self.frequency))
            self.count_minute = 0
        for disc in self.active_discs:
            if disc.actual_client is None:
                top_client = list(self.priority_top.keys())[0]
                if type(top_client) == str:
                    break
                else:
                    self.NaN_counter += 1
                    NaN = 'NaN' + str(self.NaN_counter)
                    disc.actual_client = top_client.id
                    disc.upload_start_time = time.time()
                    disc.file_size_to_upload = top_client.files_size
                    disc.client_waiting_time = top_client.waiting_time
                    self.priority_top[NaN] = self.priority_top.pop(top_client)
                    self.priority_top[NaN] = 0
                    self.active_clients.remove(top_client)
        self.refresh_discs()

    def refresh_discs(self):
        for idx, disc in enumerate(self.active_discs):
            if idx == 0:
                self.ui.Disc1Client.setText('Klient: ' + str(disc.actual_client))
                if disc.actual_client is not None:
                    uploaded = False
                    disc.update_time()
                    timed = timedelta(seconds=disc.upload_time)
                    self.ui.Disc1Time.setText(str(timed))
                    progress = int(round(disc.upload_time * 80000 / disc.file_size_to_upload))
                    if progress > 100:
                        progress = 100
                        uploaded = True
                    self.ui.Disc1ProgressBar.setValue(progress)
                    if uploaded:
                        self.service_time = disc.upload_time + disc.client_waiting_time
                        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))
                        self.disc1.__init__(1)
                        self.frequency += 1
                        self.ui.FrequencyTextBrowser.setText(str(self.frequency))
            elif idx == 1:
                self.ui.Disc2Client.setText('Klient: ' + str(disc.actual_client))
                if disc.actual_client is not None:
                    uploaded = False
                    disc.update_time()
                    timed = timedelta(seconds=disc.upload_time)
                    self.ui.Disc2Time.setText(str(timed))
                    progress = int(round(disc.upload_time * 50000 / disc.file_size_to_upload))
                    if progress > 100:
                        progress = 100
                        uploaded = True
                    self.ui.Disc2ProgressBar.setValue(progress)
                    if uploaded:
                        self.service_time = disc.upload_time + disc.client_waiting_time
                        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))
                        self.disc2.__init__(2)
                        self.frequency += 1
                        self.ui.FrequencyTextBrowser.setText(str(self.frequency))
            elif idx == 2:
                self.ui.Disc3Client.setText('Klient: ' + str(disc.actual_client))
                if disc.actual_client is not None:
                    uploaded = False
                    disc.update_time()
                    timed = timedelta(seconds=disc.upload_time)
                    self.ui.Disc3Time.setText(str(timed))
                    progress = int(round(disc.upload_time * 50000 / disc.file_size_to_upload))
                    if progress > 100:
                        progress = 100
                        uploaded = True
                    self.ui.Disc3ProgressBar.setValue(progress)
                    if uploaded:
                        self.service_time = disc.upload_time + disc.client_waiting_time
                        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))
                        self.disc3.__init__(3)
                        self.frequency += 1
                        self.ui.FrequencyTextBrowser.setText(str(self.frequency))
            elif idx == 3:
                self.ui.Disc4Client.setText('Klient: ' + str(disc.actual_client))
                if disc.actual_client is not None:
                    uploaded = False
                    disc.update_time()
                    timed = timedelta(seconds=disc.upload_time)
                    self.ui.Disc4Time.setText(str(timed))
                    progress = int(round(disc.upload_time * 50000 / disc.file_size_to_upload))
                    if progress > 100:
                        progress = 100
                        uploaded = True
                    self.ui.Disc4ProgressBar.setValue(progress)
                    if uploaded:
                        self.service_time = disc.upload_time + disc.client_waiting_time
                        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))
                        self.disc4.__init__(4)
                        self.frequency += 1
                        self.ui.FrequencyTextBrowser.setText(str(self.frequency))
            elif idx == 4:
                self.ui.Disc5Client.setText('Klient: ' + str(disc.actual_client))
                if disc.actual_client is not None:
                    uploaded = False
                    disc.update_time()
                    timed = timedelta(seconds=disc.upload_time)
                    self.ui.Disc5Time.setText(str(timed))
                    progress = int(round(disc.upload_time * 50000 / disc.file_size_to_upload))
                    if progress > 100:
                        progress = 100
                        uploaded = True
                    self.ui.Disc5ProgressBar.setValue(progress)
                    if uploaded:
                        self.service_time = disc.upload_time + disc.client_waiting_time
                        self.ui.ServiceTimeTextBrowser.setText(str(self.service_time))
                        self.disc5.__init__(5)
                        self.frequency += 1
                        self.ui.FrequencyTextBrowser.setText(str(self.frequency))

    def priority_algorithm(self, client):
        function_time = client.waiting_time ** 2 / self.service_time
        function_file = (len(self.active_clients) * self.service_time ** 2) / (client.files_size + 2 * self.frequency)
        priority = round(function_time + function_file, 3)
        client.priority = priority

    def check_priority_top(self, client):
        lowest_key = list(self.priority_top.keys())[-1]
        if client not in self.priority_top.keys() and self.priority_top[lowest_key] < client.priority:
            self.priority_top[client] = self.priority_top.pop(lowest_key)
            self.priority_top[client] = client.priority

    def refresh_priority_top(self, client):
        if client in self.priority_top.keys():
            self.priority_top[client] = client.priority
            self.priority_top = {k: v for k, v in
                                 sorted(self.priority_top.items(), key=lambda item: item[1], reverse=True)}

    def refresh_table_top(self, priority_top):
        for idx, top_client in enumerate(priority_top):
            if type(top_client) == str:
                self.ui.TopViewTable.setItem(idx, 0, QTableWidgetItem(str('None')))
                self.ui.TopViewTable.setItem(idx, 1, QTableWidgetItem(str(0)))
                self.ui.TopViewTable.setItem(idx, 2, QTableWidgetItem(str(0)))
                self.ui.TopViewTable.setItem(idx, 3, QTableWidgetItem(str(0)))
            else:
                self.ui.TopViewTable.setItem(idx, 0, QTableWidgetItem(str(top_client.id)))
                self.ui.TopViewTable.setItem(idx, 1, QTableWidgetItem(str(top_client.files_size)))
                self.ui.TopViewTable.setItem(idx, 2, QTableWidgetItem(str(top_client.waiting_time)))
                self.ui.TopViewTable.setItem(idx, 3, QTableWidgetItem(str(top_client.priority)))
                self.ui.TopViewTable.scrollToBottom()
            self.ui.ClientsTextBrowser.setText(str(len(self.active_clients)))


class Client:
    def __init__(self, actual_id):
        self.id = actual_id

        self.files_size = 0
        self.files_count = random.randint(1, 3)
        self.file1_size = random.randint(1, 10000)
        self.files_size += self.file1_size
        if self.files_count >= 2:
            self.file2_size = random.randint(1, 10000)
            self.files_size += self.file2_size
        if self.files_count == 3:
            self.file3_size = random.randint(1, 10000)
            self.files_size += self.file3_size

        self.start_time = time.time()
        self.waiting_time = round(time.time() - self.start_time)
        self.priority = 0

    def update_time(self):
        self.waiting_time = round(time.time() - self.start_time)


class Disc:
    def __init__(self, disc_id):
        self.id = disc_id
        self.actual_client = None
        self.file_size_to_upload = 0
        self.upload_start_time = 0
        self.upload_time = 0
        self.progress = 0
        self.client_waiting_time = 0

    def update_time(self):
        self.upload_time = round(time.time() - self.upload_start_time)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
