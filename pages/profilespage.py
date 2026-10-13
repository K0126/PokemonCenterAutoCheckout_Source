from PyQt5 import QtWidgets, QtCore

class ProfilesPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(71, 0, 1129, 701))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QtWidgets.QLabel("👤 프로필 관리")
        title.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("프로필은 profiles/ 폴더에 JSON 파일로 저장됩니다.")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)
        
        import os
        profile_list = QtWidgets.QListWidget()
        profile_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #FFFFFF;
                border: 1px solid #2d2d2d;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #5D43FB;
            }
        """)
        
        if os.path.exists("profiles"):
            for f in os.listdir("profiles"):
                if f.endswith(".json"):
                    profile_list.addItem(f.replace(".json", ""))
        else:
            profile_list.addItem("프로필 없음")
        
        layout.addWidget(profile_list)
        layout.addStretch()