import os
from utils.crypto import encrypt_file, decrypt_file
from PyQt5.QtWidgets import (QApplication, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPainter, QPen, QColor, QFontMetrics

# 重写QLabel的paintEvent来实现省略号效果
class ElidedLabel(QLabel):
    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideMiddle, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class DropArea(QWidget):
    def __init__(self, prompt="拖放文件到这里"):
        super().__init__()
        self.setAcceptDrops(True)
        self.file_path = None
        self.init_ui(prompt)

    def init_ui(self, prompt):
        self.setMinimumSize(280, 250)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.label = ElidedLabel(prompt, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 30px;
                font-weight: 500;
                padding: 20px;
            }
        """)
        # 设置省略号模式
        self.label.setWordWrap(False)           # 禁止换行
        self.label.setAlignment(Qt.AlignCenter) # 居中对齐

        main_layout.addWidget(self.label)
        
        self.clear_btn = QPushButton("×", self)
        self.clear_btn.setFixedSize(32, 32)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setToolTip("清除文件")
        self.clear_btn.hide()
        self.clear_btn.clicked.connect(self.clear_file)
        
        self.clear_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: rgba(233,236,239,0.9);
                border-radius: 16px;
                color: #6c757d;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(206,212,218,0.95);
                color: #dc3545;
            }
            QPushButton:pressed {
                background-color: rgba(173,181,189,0.95);
            }
        """)
        self.update_clear_btn_position()

    def resizeEvent(self, event):
        self.update_clear_btn_position()
        super().resizeEvent(event)

    def update_clear_btn_position(self):
        btn_size = self.clear_btn.size()
        self.clear_btn.move(self.width() - btn_size.width() - 8, 8)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and len(urls) == 1:
            self.file_path = urls[0].toLocalFile()
            self.label.setText(f"选择的文件是: {os.path.basename(self.file_path)}")
            self.clear_btn.show()
            self.update_clear_btn_position()
            event.acceptProposedAction()

    def clear_file(self):
        self.file_path = None
        self.label.setText("拖放文件到这里")
        self.clear_btn.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 12, 12)
        
        # 绘制边框
        pen = QPen(QColor(0, 123, 255, 120))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 12, 12)
        
        super().paintEvent(event)

class CryptoApp(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件加密解密工具")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.init_ui()
        self.setup_styles()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei UI';
                background-color: #f8f9fa;
            }
            QTabWidget::pane {
                border: none;
                padding: 15px;
                background: white;
                border-radius: 12px;
            }
            QTabBar::tab {
                padding: 12px 28px;
                background: #e9ecef;
                border: none;
                border-radius: 8px;
                color: #495057;
                margin: 4px;
                font-size: 20px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #0d6efd, stop:1 #0dcaf0);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #dee2e6;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 20px;
                background: white;
                selection-background-color: #0d6efd;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #0d6efd;
            }
            QPushButton {
                padding: 12px 24px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0d6efd, stop:1 #0dcaf0);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: 500;
                min-width: 140px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0b5ed7, stop:1 #0bacce);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a58ca, stop:1 #0a97b8);
            }
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #212529;
                font-size: 20px;
            }
            QMessageBox QPushButton {
                padding: 8px 16px;
                min-width: 80px;
            }
        """)

    def init_ui(self):
        # 加密标签页
        self.encrypt_tab = self.create_tab(
            drop_prompt="拖放要加密的文件",
            btn_text="🔒 加密文件",
            password_placeholder="输入加密密码",
            is_decrypt=False
        )
        
        # 解密标签页
        self.decrypt_tab = self.create_tab(
            drop_prompt1="拖放加密文件",
            drop_prompt2="拖放密钥文件",
            btn_text="🔓 解密文件",
            password_placeholder="输入解密密码",
            is_decrypt=True
        )

        self.addTab(self.encrypt_tab, "🔒 加密")
        self.addTab(self.decrypt_tab, "🔓 解密")

    def create_tab(self, **kwargs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(25)

        if kwargs.get("is_decrypt", False):
            hbox = QHBoxLayout()
            hbox.setSpacing(20)
            self.decrypt_file_drop = DropArea(kwargs["drop_prompt1"])
            self.decrypt_key_drop = DropArea(kwargs["drop_prompt2"])
            hbox.addWidget(self.decrypt_file_drop)
            hbox.addWidget(self.decrypt_key_drop)
            layout.addLayout(hbox)

            self.key_edit_decrypt = QLineEdit()
            self.key_edit_decrypt.setPlaceholderText(kwargs["password_placeholder"])
            self.key_edit_decrypt.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.key_edit_decrypt)
        else:
            self.encrypt_drop = DropArea(kwargs["drop_prompt"])
            layout.addWidget(self.encrypt_drop)

            self.key_edit_encrypt = QLineEdit()
            self.key_edit_encrypt.setPlaceholderText(kwargs["password_placeholder"])
            self.key_edit_encrypt.setEchoMode(QLineEdit.Password)
            layout.addWidget(self.key_edit_encrypt)

        btn = QPushButton(kwargs["btn_text"])
        if kwargs["is_decrypt"]:
            btn.clicked.connect(self.decrypt_file)
        else:
            btn.clicked.connect(self.encrypt_file)
        layout.addWidget(btn, 0, Qt.AlignCenter)

        return tab

    def encrypt_file(self):
        file_path = self.encrypt_drop.file_path
        password = self.key_edit_encrypt.text()
        
        if not file_path or not password:
            QMessageBox.warning(self, "警告", "请选择文件并输入密码")
            return
        
        try:
            output_file = file_path + ".enc"
            key_file = file_path + ".key"
            
            encrypted_data = encrypt_file(file_path, password)
            
            with open(output_file, "wb") as f:
                f.write(encrypted_data["encrypted_file_combined"])
            
            with open(key_file, "wb") as f:
                f.write(encrypted_data["key_file_data"])
            
            self.show_success_message(
                f"加密完成！\n"
                f"加密文件：{os.path.basename(output_file)}\n"
                f"密钥文件：{os.path.basename(key_file)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加密失败：{str(e)}")

    def decrypt_file(self):
        enc_file = self.decrypt_file_drop.file_path
        key_file = self.decrypt_key_drop.file_path
        password = self.key_edit_decrypt.text()
        
        if not all([enc_file, key_file, password]):
            QMessageBox.warning(self, "警告", "请选择加密文件和密钥文件并输入密码")
            return
        
        try:
            output_file = enc_file[:-4] if enc_file.endswith(".enc") else enc_file + ".decrypted"
            
            decrypted_data = decrypt_file(enc_file, key_file, password)
            
            with open(output_file, "wb") as f:
                f.write(decrypted_data)
            
            self.show_success_message(
                f"解密完成！\n"
                f"文件已保存为：{os.path.basename(output_file)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解密失败：{str(e)}")

    def show_success_message(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("操作成功")
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #1e3a8a;
                font-size: 20px;
                font-weight: 500;
                padding: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                background: #0d6efd;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #0b5ed7;
            }
            QPushButton:pressed {
                background: #0a58ca;
            }
        """)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication([])
    window = CryptoApp()
    window.setMinimumSize(720, 520)
    window.resize(840, 560)
    window.show()
    app.exec_()