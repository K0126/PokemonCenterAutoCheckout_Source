from PyQt5 import QtWidgets, QtCore, QtGui
from core.pokemon_buyer import PokemonBuyer

class TaskTab(QtWidgets.QWidget):
    """개별 태스크 위젯"""
    delete_signal = QtCore.pyqtSignal(object)
    
    def __init__(self, task_num, site, product, profile, proxy, monitor_delay, error_delay, max_price, stop_all_callback, parent=None):
        super().__init__(parent)
        self.task_num = task_num
        self.site = site
        self.product = product
        self.profile = profile
        self.proxy = proxy
        self.monitor_delay = monitor_delay
        self.error_delay = error_delay
        self.max_price = max_price
        self.stop_all_callback = stop_all_callback
        self.is_running = False
        self.worker_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(55)
        self.setStyleSheet("""
            TaskTab {
                background-color: #2a2a2a;
                border-radius: 5px;
                margin: 2px 0px;
            }
            TaskTab:hover {
                background-color: #333333;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(10)
        
        # 태스크 번호
        self.task_num_label = QtWidgets.QLabel(f"#{self.task_num}")
        self.task_num_label.setStyleSheet("color: #5D43FB; font-weight: bold; min-width: 30px; font-size: 12px;")
        layout.addWidget(self.task_num_label)
        
        # 사이트명
        self.site_label = QtWidgets.QLabel("🛒 " + self.site)
        self.site_label.setStyleSheet("color: #FFFFFF; min-width: 120px; font-size: 12px;")
        layout.addWidget(self.site_label)
        
        # 상품명
        display_name = self.product[:30] + "..." if len(self.product) > 30 else self.product
        self.product_label = QtWidgets.QLabel(display_name)
        self.product_label.setStyleSheet("color: #AAAAAA; min-width: 180px; font-size: 12px;")
        self.product_label.setToolTip(self.product)
        layout.addWidget(self.product_label)
        
        # 프로필
        self.profile_label = QtWidgets.QLabel(f"👤 {self.profile}")
        self.profile_label.setStyleSheet("color: #FFFFFF; min-width: 80px; font-size: 12px;")
        layout.addWidget(self.profile_label)
        
        # 프록시 (추가)
        proxy_display = self.proxy[:20] + "..." if len(self.proxy) > 20 else self.proxy
        self.proxy_label = QtWidgets.QLabel(f"🌐 {proxy_display}")
        self.proxy_label.setStyleSheet("color: #888888; min-width: 80px; font-size: 11px;")
        self.proxy_label.setToolTip(self.proxy)
        layout.addWidget(self.proxy_label)
        
        # 상태
        self.status_label = QtWidgets.QLabel("대기중")
        self.status_label.setStyleSheet("""
            color: #FFA500; 
            font-weight: bold; 
            min-width: 90px;
            max-width: 90px;
            background-color: #2d2d2d;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
        """)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 버튼들
        self.start_btn = QtWidgets.QPushButton("시작")
        self.start_btn.setFixedSize(60, 30)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.start_btn.clicked.connect(self.start_task)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QtWidgets.QPushButton("중지")
        self.stop_btn.setFixedSize(60, 30)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_task)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.delete_btn = QtWidgets.QPushButton("✕")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ff4444;
                background-color: #3d1a1a;
                border-radius: 4px;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.delete_signal.emit(self))
        layout.addWidget(self.delete_btn)
        
    def start_task(self):
        """태스크 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.update_status("실행중", "#4CAF50")
        
        self.worker_thread = PokemonBuyer(
            product_url=self.product,
            profile_name=self.profile,
            proxy=self.proxy,
            status_callback=self.update_status,
            log_callback=self.add_log
        )
        
        self.worker_thread.finished.connect(self.on_task_finished)
        self.worker_thread.start()
    
    def on_task_finished(self):
        """태스크 종료"""
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if self.status_label.text() not in ["주문 완료", "실패", "오류", "품절"]:
            self.update_status("완료", "#FFFFFF")
        
    def stop_task(self):
        """태스크 중지"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread = None
            
        self.is_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.update_status("중지됨", "#FFA500")
        
    def update_status(self, status, color="#FFFFFF"):
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            min-width: 90px;
            max-width: 90px;
            background-color: #2d2d2d;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
        """)
        
    def add_log(self, message):
        parent = self.parent()
        while parent and not hasattr(parent, 'log_text'):
            parent = parent.parent()
            
        if parent and hasattr(parent, 'log_text'):
            timestamp = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
            QtCore.QMetaObject.invokeMethod(
                parent.log_text,
                "append",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"[{timestamp}] {message}")
            )


class HomePage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setGeometry(QtCore.QRect(71, 0, 1129, 701))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 상단 헤더
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("📋 작업 목록 (게스트 모드)")
        title.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # 새 작업 버튼
        self.newtask_btn = QtWidgets.QPushButton("+ 새 작업")
        self.newtask_btn.setFixedSize(100, 35)
        self.newtask_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(self.newtask_btn)
        
        self.start_all_btn = QtWidgets.QPushButton("전체 시작")
        self.start_all_btn.setFixedSize(90, 35)
        self.start_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.start_all_btn.clicked.connect(self.start_all_tasks)
        header_layout.addWidget(self.start_all_btn)
        
        self.stop_all_btn = QtWidgets.QPushButton("전체 중지")
        self.stop_all_btn.setFixedSize(90, 35)
        self.stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_all_btn.clicked.connect(self.stop_all_tasks)
        header_layout.addWidget(self.stop_all_btn)
        
        layout.addLayout(header_layout)
        
        # 태스크 리스트
        scroll = QtWidgets.QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #5D43FB;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        scroll.setWidgetResizable(True)
        
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setStyleSheet("background-color: transparent;")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addStretch()
        
        scroll.setWidget(self.scrollAreaWidgetContents)
        layout.addWidget(scroll)
        
        # 로그 영역
        log_group = QtWidgets.QGroupBox("📊 실행 로그")
        log_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #2d2d2d;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        log_group.setFixedHeight(150)
        
        log_layout = QtWidgets.QVBoxLayout(log_group)
        log_layout.setContentsMargins(5, 15, 5, 5)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #0d0d0d;
            color: #00ff41;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            border: none;
            padding: 5px;
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
    def start_all_tasks(self):
        for i in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(i).widget()
            if isinstance(widget, TaskTab):
                if not widget.is_running:
                    widget.start_task()
                    
    def stop_all_tasks(self):
        for i in range(self.verticalLayout.count()):
            widget = self.verticalLayout.itemAt(i).widget()
            if isinstance(widget, TaskTab):
                widget.stop_task()