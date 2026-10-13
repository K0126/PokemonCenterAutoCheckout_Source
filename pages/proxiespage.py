from PyQt5 import QtWidgets, QtCore

class ProxiesPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(QtCore.QRect(71, 0, 1129, 701))
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QtWidgets.QLabel("🌐 프록시 관리")
        title.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QtWidgets.QLabel("프록시는 proxies.txt 파일에 저장됩니다.")
        info.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout.addWidget(info)
        
        # 프록시 목록 표시
        self.proxy_list = QtWidgets.QListWidget()
        self.proxy_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                color: #FFFFFF;
                border: 1px solid #2d2d2d;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #5D43FB;
            }
        """)
        self.load_proxies()
        layout.addWidget(self.proxy_list)
        
        # 버튼들
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.add_btn = QtWidgets.QPushButton("+ 프록시 추가")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_btn.clicked.connect(self.add_proxy)
        btn_layout.addWidget(self.add_btn)
        
        self.remove_btn = QtWidgets.QPushButton("🗑 선택 삭제")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.remove_btn.clicked.connect(self.remove_proxy)
        btn_layout.addWidget(self.remove_btn)
        
        self.refresh_btn = QtWidgets.QPushButton("🔄 새로고침")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_proxies)
        btn_layout.addWidget(self.refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 프록시 형식 안내
        format_info = QtWidgets.QLabel(
            "📌 프록시 형식:\n"
            "• IP:PORT (예: 192.168.1.1:8080)\n"
            "• http://user:pass@IP:PORT (예: http://user:pass@192.168.1.1:8080)\n"
            "• https://user:pass@IP:PORT (예: https://user:pass@192.168.1.1:8080)"
        )
        format_info.setStyleSheet("color: #888888; font-size: 11px; background-color: #1a1a1a; padding: 10px; border-radius: 5px;")
        format_info.setWordWrap(True)
        layout.addWidget(format_info)
    
    def load_proxies(self):
        """proxies.txt 파일에서 프록시 목록 로드"""
        import os
        self.proxy_list.clear()
        
        if os.path.exists("proxies.txt"):
            try:
                with open("proxies.txt", "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            self.proxy_list.addItem(line)
            except Exception as e:
                self.proxy_list.addItem(f"❌ 읽기 오류: {e}")
        else:
            self.proxy_list.addItem("📁 proxies.txt 파일이 없습니다.")
            self.proxy_list.addItem("💡 '프록시 추가' 버튼으로 생성하세요.")
    
    def add_proxy(self):
        """프록시 추가 다이얼로그"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("프록시 추가")
        dialog.setFixedSize(400, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #FFFFFF;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        label = QtWidgets.QLabel("프록시 입력 (형식: http://user:pass@ip:port 또는 ip:port)")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        input_field = QtWidgets.QLineEdit()
        input_field.setPlaceholderText("http://user:pass@192.168.1.1:8080")
        layout.addWidget(input_field)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("✅ 추가")
        ok_btn.clicked.connect(lambda: self.save_proxy(input_field.text(), dialog))
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QtWidgets.QPushButton("❌ 취소")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def save_proxy(self, proxy_text, dialog):
        """프록시 저장"""
        import os
        proxy_text = proxy_text.strip()
        
        if not proxy_text:
            QtWidgets.QMessageBox.warning(self, "경고", "프록시를 입력해주세요.")
            return
        
        # proxies.txt 파일에 추가
        with open("proxies.txt", "a") as f:
            f.write(proxy_text + "\n")
        
        dialog.close()
        self.load_proxies()
        QtWidgets.QMessageBox.information(self, "완료", "프록시가 추가되었습니다.")
    
    def remove_proxy(self):
        """선택한 프록시 삭제"""
        import os
        current_item = self.proxy_list.currentItem()
        if not current_item:
            QtWidgets.QMessageBox.warning(self, "경고", "삭제할 프록시를 선택해주세요.")
            return
        
        proxy_text = current_item.text()
        
        # 확인
        reply = QtWidgets.QMessageBox.question(
            self,
            "삭제 확인",
            f"'{proxy_text}'를 삭제하시겠습니까?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        # proxies.txt 다시 쓰기 (선택한 항목 제외)
        if os.path.exists("proxies.txt"):
            with open("proxies.txt", "r") as f:
                lines = f.readlines()
            
            with open("proxies.txt", "w") as f:
                for line in lines:
                    if line.strip() != proxy_text:
                        f.write(line)
        
        self.load_proxies()
        QtWidgets.QMessageBox.information(self, "완료", "프록시가 삭제되었습니다.")