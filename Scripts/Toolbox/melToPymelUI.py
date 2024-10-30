from PySide2 import QtWidgets
import maya.cmds as cmds

# 全局变量保存对话框实例
_mel_converter_dialog = None

class MelConverter(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MelConverter, self).__init__(parent)
        self.setWindowTitle("MEL to Python")
        self.setMinimumWidth(600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Input text area
        self.input_text = QtWidgets.QTextEdit()
        self.input_text.setPlaceholderText("Paste MEL code here...")
        layout.addWidget(self.input_text)
        
        # Convert button
        convert_btn = QtWidgets.QPushButton("Convert")
        convert_btn.clicked.connect(self.convert)
        layout.addWidget(convert_btn)
        
        # Output text area
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setPlaceholderText("Python code will appear here...")
        layout.addWidget(self.output_text)
        
    def convert(self):
        mel_code = self.input_text.toPlainText()
        try:
            python_code = self.mel_to_python(mel_code)
            self.output_text.setPlainText(python_code)
        except Exception as e:
            self.output_text.setPlainText(f"Error converting: {str(e)}")
            
    def mel_to_python(self, mel_code):
        """更完整的MEL到Python转换"""
        # 基础命令替换
        replacements = {
            # Maya命令
            'setAttr': 'cmds.setAttr',
            'getAttr': 'cmds.getAttr',
            'select': 'cmds.select',
            'ls': 'cmds.ls',
            'delete': 'cmds.delete',
            'group': 'cmds.group',
            'parent': 'cmds.parent',
            
            # MEL语法结构转换
            'proc': 'def',
            'if': 'if',
            'else': 'else',
            'for': 'for',
            'while': 'while',
            
            # MEL变量声明
            'int': '',
            'float': '',
            'string': '',
            'vector': '',
            
            # MEL运算符
            '&&': 'and',
            '||': 'or',
            '!': 'not',
            
            # MEL数组
            '[]': '[]',
            
            # MEL特殊字符
            ';': '',
            '$': '',
            '`': '',  # MEL命令替换符
        }
        
        # 处理MEL代码块
        lines = mel_code.split('\n')
        python_lines = []
        indent_level = 0
        
        for line in lines:
            # 处理缩进
            if '{' in line:
                python_lines.append(line.replace('{', ':'))
                indent_level += 1
            elif '}' in line:
                indent_level -= 1
                continue
            else:
                # 处理命令替换
                for mel_cmd, py_cmd in replacements.items():
                    line = line.replace(mel_cmd, py_cmd)
                # 添加适当的缩进
                python_lines.append('    ' * indent_level + line)
        
        return '\n'.join(python_lines)

def show():
    global _mel_converter_dialog
    
    # 如果已存在对话框，先关闭
    if _mel_converter_dialog:
        try:
            _mel_converter_dialog.close()
            _mel_converter_dialog.deleteLater()
        except:
            pass
    
    # 创建新的对话框
    parent = QtWidgets.QApplication.activeWindow()
    _mel_converter_dialog = MelConverter(parent=parent)
    _mel_converter_dialog.show()
    return _mel_converter_dialog