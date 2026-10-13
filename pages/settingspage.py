from PyQt5 import QtWidgets, QtCore

class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(71, 0, 1129, 701))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QtWidgets.QLabel("⚙️ 설정")
        title.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("설정 기능은 추후 업데이트 예정입니다.")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)
        
        layout.addStretch()