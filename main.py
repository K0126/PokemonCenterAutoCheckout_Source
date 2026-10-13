from PyQt5 import QtCore, QtGui, QtWidgets
from pages.homepage import HomePage, TaskTab
from pages.createdialog import CreateDialog
from pages.profilespage import ProfilesPage
from pages.proxiespage import ProxiesPage
from pages.settingspage import SettingsPage
import sys
import os

def no_abort(a, b, c):
    sys.__excepthook__(a, b, c)
sys.excepthook = no_abort

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.show()
        
    def setupUi(self, MainWindow):
        MainWindow.setFixedSize(1200, 700)
        MainWindow.setStyleSheet("""
            background-color: #1E1E1E;
            color: #FFFFFF;
        """)
        MainWindow.setWindowTitle("포켓몬센터 자동구매 봇 (게스트 모드)")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("""
            QMessageBox QLabel { color: #FFFFFF; }
            QMessageBox QPushButton { 
                background-color: #5D43FB;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
        """)
        
        # ===== 사이드바 =====
        self.sidebar = QtWidgets.QWidget(self.centralwidget)
        self.sidebar.setGeometry(QtCore.QRect(0, 0, 71, 701))
        self.sidebar.setStyleSheet("""
            background-color: #232323;
            border-right: 1px solid #2e2d2d;
        """)
        
        self.logo = QtWidgets.QLabel(self.sidebar)
        self.logo.setGeometry(QtCore.QRect(15, 20, 41, 41))
        self.logo.setStyleSheet("border: none; font-size: 32px;")
        self.logo.setText("🎯")
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        
        # 홈 탭
        self.home_tab = QtWidgets.QWidget(self.sidebar)
        self.home_tab.setGeometry(QtCore.QRect(0, 85, 71, 50))
        self.home_tab.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.home_tab.setStyleSheet("background-color: #272342; border: none;")
        
        self.home_active_tab = QtWidgets.QWidget(self.home_tab)
        self.home_active_tab.setGeometry(QtCore.QRect(0, 0, 4, 50))
        self.home_active_tab.setStyleSheet("background-color: #5D43FB; border: none;")
        
        self.home_icon = QtWidgets.QLabel(self.home_tab)
        self.home_icon.setGeometry(QtCore.QRect(25, 13, 20, 20))
        self.home_icon.setStyleSheet("border: none; font-size: 20px;")
        self.home_icon.setText("🏠")
        self.home_icon.setAlignment(QtCore.Qt.AlignCenter)
        
        self.home_label = QtWidgets.QLabel(self.home_tab)
        self.home_label.setGeometry(QtCore.QRect(0, 35, 71, 15))
        self.home_label.setStyleSheet("color: #FFFFFF; font-size: 9px; border: none;")
        self.home_label.setText("홈")
        self.home_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # 프로필 탭
        self.profiles_tab = QtWidgets.QWidget(self.sidebar)
        self.profiles_tab.setGeometry(QtCore.QRect(0, 135, 71, 50))
        self.profiles_tab.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.profiles_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.profiles_active_tab = QtWidgets.QWidget(self.profiles_tab)
        self.profiles_active_tab.setGeometry(QtCore.QRect(0, 0, 4, 50))
        self.profiles_active_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.profiles_icon = QtWidgets.QLabel(self.profiles_tab)
        self.profiles_icon.setGeometry(QtCore.QRect(25, 13, 20, 20))
        self.profiles_icon.setStyleSheet("border: none; font-size: 20px;")
        self.profiles_icon.setText("👤")
        self.profiles_icon.setAlignment(QtCore.Qt.AlignCenter)
        
        self.profiles_label = QtWidgets.QLabel(self.profiles_tab)
        self.profiles_label.setGeometry(QtCore.QRect(0, 35, 71, 15))
        self.profiles_label.setStyleSheet("color: #888888; font-size: 9px; border: none;")
        self.profiles_label.setText("프로필")
        self.profiles_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # 프록시 탭
        self.proxies_tab = QtWidgets.QWidget(self.sidebar)
        self.proxies_tab.setGeometry(QtCore.QRect(0, 185, 71, 50))
        self.proxies_tab.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.proxies_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.proxies_active_tab = QtWidgets.QWidget(self.proxies_tab)
        self.proxies_active_tab.setGeometry(QtCore.QRect(0, 0, 4, 50))
        self.proxies_active_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.proxies_icon = QtWidgets.QLabel(self.proxies_tab)
        self.proxies_icon.setGeometry(QtCore.QRect(25, 13, 20, 20))
        self.proxies_icon.setStyleSheet("border: none; font-size: 20px;")
        self.proxies_icon.setText("🌐")
        self.proxies_icon.setAlignment(QtCore.Qt.AlignCenter)
        
        self.proxies_label = QtWidgets.QLabel(self.proxies_tab)
        self.proxies_label.setGeometry(QtCore.QRect(0, 35, 71, 15))
        self.proxies_label.setStyleSheet("color: #888888; font-size: 9px; border: none;")
        self.proxies_label.setText("프록시")
        self.proxies_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # 설정 탭
        self.settings_tab = QtWidgets.QWidget(self.sidebar)
        self.settings_tab.setGeometry(QtCore.QRect(0, 235, 71, 50))
        self.settings_tab.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.settings_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.settings_active_tab = QtWidgets.QWidget(self.settings_tab)
        self.settings_active_tab.setGeometry(QtCore.QRect(0, 0, 4, 50))
        self.settings_active_tab.setStyleSheet("background-color: transparent; border: none;")
        
        self.settings_icon = QtWidgets.QLabel(self.settings_tab)
        self.settings_icon.setGeometry(QtCore.QRect(25, 13, 20, 20))
        self.settings_icon.setStyleSheet("border: none; font-size: 20px;")
        self.settings_icon.setText("⚙️")
        self.settings_icon.setAlignment(QtCore.Qt.AlignCenter)
        
        self.settings_label = QtWidgets.QLabel(self.settings_tab)
        self.settings_label.setGeometry(QtCore.QRect(0, 35, 71, 15))
        self.settings_label.setStyleSheet("color: #888888; font-size: 9px; border: none;")
        self.settings_label.setText("설정")
        self.settings_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # ===== 페이지들 =====
        self.homepage = HomePage(self.centralwidget)
        self.createdialog = CreateDialog(self)
        self.createdialog.addtask_btn.clicked.connect(self.create_task)
        self.createdialog.hide()
        
        self.profilespage = ProfilesPage(self.centralwidget)
        self.profilespage.hide()
        self.proxiespage = ProxiesPage(self.centralwidget)
        self.proxiespage.hide()
        self.settingspage = SettingsPage(self.centralwidget)
        self.settingspage.hide()
        
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.set_functions()
        
    def set_functions(self):
        self.current_page = "home"
        self.home_tab.mousePressEvent = lambda event: self.change_page(event, "home")
        self.profiles_tab.mousePressEvent = lambda event: self.change_page(event, "profiles")
        self.proxies_tab.mousePressEvent = lambda event: self.change_page(event, "proxies")
        self.settings_tab.mousePressEvent = lambda event: self.change_page(event, "settings")
        self.homepage.newtask_btn.clicked.connect(self.createdialog.show)
        
    def change_page(self, event, current_page):
        prev_active = getattr(self, f'{self.current_page}_active_tab')
        prev_tab = getattr(self, f'{self.current_page}_tab')
        prev_label = getattr(self, f'{self.current_page}_label')
        prev_page = getattr(self, f'{self.current_page}page')
        
        prev_active.setStyleSheet("background-color: transparent; border: none;")
        prev_tab.setStyleSheet("background-color: transparent; border: none;")
        prev_label.setStyleSheet("color: #888888; font-size: 9px; border: none;")
        prev_page.hide()
        
        self.current_page = current_page
        new_active = getattr(self, f'{self.current_page}_active_tab')
        new_tab = getattr(self, f'{self.current_page}_tab')
        new_label = getattr(self, f'{self.current_page}_label')
        new_page = getattr(self, f'{self.current_page}page')
        
        new_active.setStyleSheet("background-color: #5D43FB; border: none;")
        new_tab.setStyleSheet("background-color: #272342; border: none;")
        new_label.setStyleSheet("color: #FFFFFF; font-size: 9px; border: none;")
        new_page.show()
        
    def create_task(self):
        site = self.createdialog.site_box.currentText()
        product = self.createdialog.input_edit.text()
        profile = self.createdialog.profile_box.currentText()
        proxies = self.createdialog.proxies_box.currentText()
        monitor_delay = self.createdialog.monitor_edit.text()
        error_delay = self.createdialog.error_edit.text()
        max_price = self.createdialog.price_edit.text() if self.createdialog.maxprice_checkbox.isChecked() else ""
        
        if product == "":
            QtWidgets.QMessageBox.warning(self, "경고", "상품 URL을 입력해주세요!")
            return
            
        if profile == "프로필 선택" or profile == "":
            QtWidgets.QMessageBox.warning(self, "경고", "프로필을 선택해주세요!")
            return
        
        for i in range(self.createdialog.taskcount_spinbox.value()):
            if self.homepage.verticalLayout.count() > 0:
                last_item = self.homepage.verticalLayout.itemAt(self.homepage.verticalLayout.count() - 1)
                if last_item and last_item.spacerItem():
                    self.homepage.verticalLayout.takeAt(self.homepage.verticalLayout.count() - 1)
            
            task_num = self.homepage.verticalLayout.count() + 1
            tab = TaskTab(
                task_num,
                site,
                product,
                profile,
                proxies,
                monitor_delay,
                error_delay,
                max_price,
                self.homepage.stop_all_tasks,
                self.homepage.scrollAreaWidgetContents
            )
            self.homepage.verticalLayout.addWidget(tab)
            
            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.homepage.verticalLayout.addItem(spacerItem)
            
        self.createdialog.close()

if __name__ == "__main__":
    ui_app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(ui_app.exec_())