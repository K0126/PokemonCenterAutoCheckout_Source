from PyQt5 import QtWidgets, QtCore, QtGui

class CreateDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(520, 520)
        self.setWindowTitle("새 작업 생성")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #2d2d2d;
                color: #FFFFFF;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                min-height: 20px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover {
                border: 1px solid #5D43FB;
            }
            QComboBox:focus, QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #5D43FB;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #FFFFFF;
                border: 1px solid #3d3d3d;
                selection-background-color: #5D43FB;
            }
            QCheckBox {
                color: #CCCCCC;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #5D43FB;
                border: 1px solid #5D43FB;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton#addBtn {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#addBtn:hover {
                background-color: #45a049;
            }
            QPushButton#cancelBtn {
                background-color: #555555;
                color: white;
            }
            QPushButton#cancelBtn:hover {
                background-color: #666666;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #2d2d2d;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)
        
        title = QtWidgets.QLabel("➕ 새 작업 추가")
        title.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold; border: none;")
        main_layout.addWidget(title)
        
        form_widget = QtWidgets.QWidget()
        form_layout = QtWidgets.QFormLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        self.site_box = QtWidgets.QComboBox()
        self.site_box.addItems(["Pokemon Center"])
        self.site_box.setFixedHeight(32)
        form_layout.addRow("사이트:", self.site_box)
        
        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.setPlaceholderText("https://www.pokemoncenter.com/product/...")
        self.input_edit.setFixedHeight(32)
        form_layout.addRow("상품 URL:", self.input_edit)
        
        self.profile_box = QtWidgets.QComboBox()
        self._load_profiles()
        self.profile_box.setFixedHeight(32)
        form_layout.addRow("프로필:", self.profile_box)
        
        # ===== 프록시 선택 (추가) =====
        self.proxies_box = QtWidgets.QComboBox()
        self._load_proxies()
        self.proxies_box.setFixedHeight(32)
        form_layout.addRow("프록시:", self.proxies_box)
        
        self.monitor_edit = QtWidgets.QLineEdit("5")
        self.monitor_edit.setFixedHeight(32)
        form_layout.addRow("모니터링 딜레이 (초):", self.monitor_edit)
        
        self.error_edit = QtWidgets.QLineEdit("5")
        self.error_edit.setFixedHeight(32)
        form_layout.addRow("에러 딜레이 (초):", self.error_edit)
        
        self.maxprice_checkbox = QtWidgets.QCheckBox("최대 가격 설정")
        self.maxprice_checkbox.setFixedHeight(25)
        form_layout.addRow("", self.maxprice_checkbox)
        
        self.price_edit = QtWidgets.QLineEdit()
        self.price_edit.setPlaceholderText("최대 가격 (USD)")
        self.price_edit.setFixedHeight(32)
        self.price_edit.setEnabled(False)
        self.maxprice_checkbox.toggled.connect(self.price_edit.setEnabled)
        form_layout.addRow("최대 가격:", self.price_edit)
        
        self.taskcount_spinbox = QtWidgets.QSpinBox()
        self.taskcount_spinbox.setMinimum(1)
        self.taskcount_spinbox.setMaximum(10)
        self.taskcount_spinbox.setFixedHeight(32)
        form_layout.addRow("작업 개수:", self.taskcount_spinbox)
        
        main_layout.addWidget(form_widget)
        main_layout.addStretch()
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        self.addtask_btn = QtWidgets.QPushButton("✅ 작업 추가")
        self.addtask_btn.setObjectName("addBtn")
        self.addtask_btn.setFixedSize(120, 38)
        btn_layout.addWidget(self.addtask_btn)
        
        self.cancel_btn = QtWidgets.QPushButton("❌ 취소")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedSize(100, 38)
        self.cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(btn_layout)
    
    def _load_profiles(self):
        """프로필 목록 로드"""
        import os
        profiles = ["프로필 선택"]
        if os.path.exists("profiles"):
            for f in os.listdir("profiles"):
                if f.endswith(".json"):
                    profiles.append(f.replace(".json", ""))
        self.profile_box.addItems(profiles)
    
    def _load_proxies(self):
        """프록시 목록 로드"""
        import os
        proxies = ["사용 안함"]
        
        # proxies.txt 파일에서 로드
        if os.path.exists("proxies.txt"):
            try:
                with open("proxies.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            proxies.append(line)
            except:
                pass
        
        self.proxies_box.addItems(proxies)