# -*-coding:utf-8 -*-
u"""
:创建时间: 2022/4/22 2:36
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:QQ: 2921251087
:爱发电: https://afdian.net/@Phantom_of_the_Cang
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import abc

from cpform.utils import decode_string, call_block

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    try:
        from PySide2.QtGui import *
        from PySide2.QtCore import *
        from PySide2.QtWidgets import *
    except ImportError:
        from PySide.QtGui import *
        from PySide.QtCore import *

try:
    from shiboken2 import *
except ImportError:
    from shiboken import *

import cpform.config as config
import cpform.svg as svg

__all__ = [
    'UnicodeStrType', 'AnyStrType', 'ColorType',
    'new_color',
    'Widget',
    'Warp', 'WarpWidget',
    'DataSetWidget',
    'DataMaskingWidget',
    'Background', 'BackgroundWidget',
    'ToggleWidget',
    'Label', 'LabelWidget',
    'LineEdit', 'LineEditWidget',
    'TextEditWidget',
    'AbstractButtonWidget', 'Button', 'ButtonWidget',
    'CheckBox', 'CheckBoxWidget', 'SpinBoxWidget',
    'HBoxLayout', 'VBoxLayout', 'FormLayout',
    'ScrollArea', 'ScrollAreaWidget',
    'SubmitWidget',
    'Help', 'HelpWidget',
    'IntSlider', 'IntSliderWidget',
    'FloatSlider', 'FloatSliderWidget',
    'Collapse', 'CollapseWidget',
    'HeadLine', 'HeadLineWidget',
]

UnicodeStrType = type('')
AnyStrType = (bytes, UnicodeStrType)
ColorType = QColor

_align_map = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'top': Qt.AlignTop,
    'bottom': Qt.AlignBottom,
    'center': Qt.AlignCenter,
}


def new_color(color):
    """
    :type color: str|(int, int, int)|(int, int, int, int)
    :rtype: ColorType
    """
    if isinstance(color, AnyStrType):
        return QColor(color)
    else:
        return QColor(*color)


def rgb(r, g, b):
    return r, g, b


def rgba(r, g, b, a):
    return r, g, b, a


class Widget(QWidget):
    def __init__(self,
                 left_clicked_callback=None,
                 right_clicked_callback=None,
                 min_width=None,
                 min_height=None,
                 max_width=None,
                 max_height=None,
                 fixed_width=None,
                 fixed_height=None,
                 ):
        super(Widget, self).__init__()
        self.__left_clicked_callback = left_clicked_callback
        self.__right_clicked_callback = right_clicked_callback
        self.__left_button_pressed = False
        self.__right_button_pressed = False
        if min_width is not None:
            self.setMinimumWidth(min_width)
        if min_height is not None:
            self.setMinimumHeight(min_height)
        if max_width is not None:
            self.setMaximumWidth(max_width)
        if max_height is not None:
            self.setMaximumHeight(max_height)
        if fixed_width is not None:
            self.setFixedWidth(fixed_width)
        if fixed_height is not None:
            self.setFixedHeight(fixed_height)

    def mousePressEvent(self, event):
        """

        :type event: QMouseEvent
        :return:
        """
        if event.button() == Qt.LeftButton and callable(self.__left_clicked_callback):
            self.__left_button_pressed = True
            return
        if event.button() == Qt.RightButton and callable(self.__right_clicked_callback):
            self.__right_button_pressed = True
            return
        event.ignore()
        return

    def mouseReleaseEvent(self, event):
        """

        :type event: QMouseEvent
        :return:
        """
        if event.button() == Qt.LeftButton and self.__left_button_pressed and callable(self.__left_clicked_callback):
            self.__left_clicked_callback()
            return
        if event.button() == Qt.RightButton and self.__right_button_pressed and callable(self.__right_clicked_callback):
            self.__right_clicked_callback()
            return
        event.ignore()
        return

    @abc.abstractmethod
    def read_data(self):
        """
        返回数据

        :rtype: List[Any]
        """
        return []


class Warp(Widget):
    def __init__(self, child, **kwargs):
        """

        :type child: QWidget
        """
        super(Warp, self).__init__(**kwargs)
        self.child = child
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(child)

    def read_data(self):
        return self.child.read_data()


WarpWidget = Warp


class DataSetWidget(Warp):
    def read_data(self):
        return [list(super(DataSetWidget, self).read_data())]


class DataMaskingWidget(Warp):
    def read_data(self):
        return []


class Background(Warp):
    def __init__(self, child, color=config.DEFAULT_COLOR, **kwargs):
        """

        :type child: Widget
        :type color: unicode|str|(int, int, int)|(int, int, int, int)
        """
        super(Background, self).__init__(child, **kwargs)
        self.color = new_color(color)

    def paintEvent(self, *args, **kwargs):
        p = QPainter(self)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self.color))
        p.drawRect(self.rect())
        p.end()


BackgroundWidget = Background


class ToggleWidget(Widget):
    """可以进行切换的通用组件"""

    def __init__(self, widget=None, **kwargs):
        super(ToggleWidget, self).__init__(**kwargs)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.widget = Widget() if widget is None else widget
        self.main_layout.addWidget(self.widget)

    def toggle_to(self, widget):
        self.widget.close()
        self.widget.deleteLater()
        self.widget = widget
        self.main_layout.addWidget(widget)

    def read_data(self):
        return self.widget.read_data()


class Label(Widget):
    def __init__(self, text='', word_wrap=False, font_size=None, align=None, **kwargs):
        text = decode_string(text)
        super(Label, self).__init__(**kwargs)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel(text)
        self._label.setWordWrap(word_wrap)
        if align is not None:
            self._label.setAlignment(_align_map[align])
        self.main_layout.addWidget(self._label)

        if font_size is not None:
            self.setStyleSheet('font-size: {}pt;background: transparent;'.format(font_size))

    def set_text(self, text):
        self._label.setText(text)
        return self


LabelWidget = Label


class LineEdit(Widget):
    def __init__(self, text='',
                 is_encrypt=False,
                 placeholder_text='',
                 tool_tip='',
                 return_pressed_callback=None,
                 **kwargs):
        """
        :type text: AnyStr
        :type is_encrypt: bool
        :type placeholder_text: AnyStr
        :type tool_tip: AnyStr
        :type return_pressed_callback: ()->Any
        :param kwargs:
        """
        super(LineEdit, self).__init__(**kwargs)
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._text = QLineEdit(decode_string(text))
        self._text.setPlaceholderText(placeholder_text)
        self._text.setToolTip(decode_string(tool_tip))
        self._text.returnPressed.connect(call_block(lambda *args: return_pressed_callback()))
        if is_encrypt:
            self._text.setEchoMode(QLineEdit.Password)
        self._main_layout.addWidget(self._text)

    def set_text(self, text):
        self._text.setText(text)
        return self

    def get_text(self):
        return self._text.text()

    def read_data(self):
        return [self._text.text()]


LineEditWidget = LineEdit


class TextEditWidget(WarpWidget):
    def __init__(self):
        self.text_edit = QPlainTextEdit()
        super(TextEditWidget, self).__init__(child=self.text_edit)

    def read_data(self):
        return [self.text_edit.toPlainText()]


class AbstractButtonWidget(WarpWidget):
    color = QColor(90, 90, 90, 135)

    def __init__(self, child, **kwargs):
        super(AbstractButtonWidget, self).__init__(child, **kwargs)

    def enterEvent(self, *args, **kwargs):
        super(AbstractButtonWidget, self).enterEvent(*args, **kwargs)
        self.color = QColor(65, 65, 65, 135)
        self.update()

    def leaveEvent(self, *args, **kwargs):
        super(AbstractButtonWidget, self).leaveEvent(*args, **kwargs)
        self.color = QColor(90, 90, 90, 135)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(QColor(90, 90, 90, 135), 4))
        color = self.color
        # if self.isDown():
        #     color = QColor(0, 0, 0, 25)
        # if self.isChecked():
        #     color = QColor(0, 0, 0, 50)
        p.setBrush(QBrush(color))
        p.drawRoundedRect(self.rect(), 2, 2)
        p.end()


class Button(Widget):
    def __init__(self, text='', icon=None, icon_size=None, func=None, **kwargs):
        self.func = func
        text = decode_string(text)
        super(Button, self).__init__(**kwargs)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        bn = QPushButton(text)
        if icon is not None:
            bn.setIcon(svg.icon(icon))
            if icon_size is not None:
                bn.setIconSize(QSize(icon_size, icon_size))
        bn.clicked.connect(self.call)

        self.main_layout.addWidget(bn)

    def call(self):
        if self.func is not None:
            self.func()


ButtonWidget = Button


class CheckBox(Widget):
    def __init__(
            self,
            info=u"",
            default_state=False,
            update_func=None,
            **kwargs
    ):
        info = decode_string(info)
        super(CheckBox, self).__init__(**kwargs)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox = QCheckBox(info, self)
        self.checkbox.setObjectName('cpform_checkbox')
        self.checkbox.setChecked(default_state)
        self.main_layout.addWidget(self.checkbox)
        if update_func is not None:
            update_func = call_block(update_func)
            self.checkbox.clicked.connect(lambda *args: update_func(self.state()))
        self.__update_icon()
        self.checkbox.clicked.connect(lambda *args: self.__update_icon())

    def __update_icon(self):
        if self.state():
            self.checkbox.setIcon(svg.pixmap('check-square'))
        else:
            self.checkbox.setIcon(svg.pixmap('square'))

    def set_state(self, state):
        self.checkbox.setChecked(state)

    def state(self):
        return self.checkbox.isChecked()

    def read_data(self):
        return [self.state()]


CheckBoxWidget = CheckBox


class SpinBoxWidget(Widget):
    def __init__(
            self,
            **kwargs
    ):
        super(SpinBoxWidget, self).__init__(**kwargs)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.spinbox = QSpinBox(self)
        self.spinbox.setObjectName('cpform_spinbox')
        self.main_layout.addWidget(self.spinbox)

        self.spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # self.spinbox.setButtonPixmap(QAbstractSpinBox.Up, svg.pixmap('check-square'))
        # self.spinbox.setButtonSymbols(svg.pixmap('check-square'))


class HBoxLayout(Widget):
    def __init__(self, childs, margins=5, spacing=5, align=None, **kwargs):
        super(HBoxLayout, self).__init__(**kwargs)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(margins, margins, margins, margins)
        self.main_layout.setSpacing(spacing)

        if align is not None:
            self.main_layout.setAlignment(_align_map[align])

        self.childs = childs
        for i in childs:
            self.main_layout.addWidget(i)

    def read_data(self):
        for i in self.childs:
            data = i.read_data()
            for t in data:
                yield t


class VBoxLayout(Widget):
    def __init__(self, childs, margins=5, spacing=5, align=None, **kwargs):
        super(VBoxLayout, self).__init__(**kwargs)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(margins, margins, margins, margins)
        self.main_layout.setSpacing(spacing)

        if align is not None:
            self.main_layout.setAlignment(_align_map[align])

        self.childs = childs
        for i in childs:
            self.main_layout.addWidget(i)

    def read_data(self):
        for i in self.childs:
            data = i.read_data()
            for t in data:
                yield t


class FormLayout(Widget):
    def __init__(self, childs, margins=5, spacing=5, align=None, **kwargs):
        super(FormLayout, self).__init__(**kwargs)
        self.main_layout = QFormLayout(self)
        self.main_layout.setContentsMargins(margins, margins, margins, margins)
        self.main_layout.setSpacing(spacing)

        if align is not None:
            self.main_layout.setAlignment(_align_map[align])

        self.labels = childs[0::2]
        self.childs = childs[1::2]

        for l, w in zip(self.labels, self.childs):
            self.main_layout.addRow(l, w)

    def read_data(self):
        for i in self.childs:
            data = i.read_data()
            for t in data:
                yield t


class Help(Label):
    def __init__(self, text='', **kwargs):
        super(Help, self).__init__(text, word_wrap=True, **kwargs)
        self.setMinimumHeight(40)


HelpWidget = Help


class HeadLine(Label):
    _level_font_size_map = [54, 44, 35, 27, 20, 14]

    def __init__(self, text='', level=1, align='center', **kwargs):
        super(HeadLine, self).__init__(text,
                                       word_wrap=False,
                                       font_size=self._level_font_size_map[level - 1],
                                       align=align,
                                       **kwargs)


HeadLineWidget = HeadLine


class IntSlider(Widget):
    def __init__(self, min=0, max=100, default=0, **kwargs):
        self.min = min
        self.max = max
        super(IntSlider, self).__init__(**kwargs)
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._text = QLineEdit()
        self._text.setFixedWidth(60)
        self._text.returnPressed.connect(lambda *args: self.update_line_edit(self._text.text()))

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setMinimum(self.min)
        self._slider.setMaximum(self.max)
        self._slider.sliderMoved.connect(self.update_slider)

        self._main_layout.addWidget(self._slider)
        self._main_layout.addWidget(self._text)

        self.set_text(str(default))
        self._slider.setValue(default)

    def read_data(self):
        return [max(min(int(self.text()), self.max), self.min)]

    def update_slider(self, v):
        self.set_text(u"%d" % v)

    def update_line_edit(self, v):
        self._slider.setValue(int(v))
        self.update_slider(self._slider.value())

    def set_text(self, s):
        self._text.setText(s)

    def text(self):
        return self._text.text()


IntSliderWidget = IntSlider


class FloatSlider(Widget):
    def __init__(self, min=0, max=1, default=0, **kwargs):
        self.min = float(min)
        self.max = float(max)
        super(FloatSlider, self).__init__(**kwargs)
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._text = QLineEdit()
        self._text.setFixedWidth(60)
        self._text.returnPressed.connect(lambda *args: self.update_line_edit(self._text.text()))

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setMinimum(0)
        self._slider.setMaximum(1000000)
        self._slider.sliderMoved.connect(self.update_slider)

        self._main_layout.addWidget(self._slider)
        self._main_layout.addWidget(self._text)

        self.update_line_edit(default)

    def read_data(self):
        return [max(min(float(self.text()), self.max), self.min)]

    def update_slider(self, v):
        size = self.max - self.min
        v = max(min(float(v) / 1000000, 1), 0)
        v = (v * size) + self.min
        v = max(min(v, self.max), self.min)
        v_str = '%.3f' % v
        while v_str[-1] == '0':
            v_str = v_str[:-1]
        if v_str[-1] == '.':
            v_str = v_str[:-1]
        self.set_text(v_str)

    def update_line_edit(self, v):
        self._slider.setValue((float(v) - self.min) / (self.max - self.min) * 1000000)
        self.update_slider(self._slider.value())

    def set_text(self, s):
        self._text.setText(s)

    def text(self):
        return self._text.text()


FloatSliderWidget = FloatSlider


class ScrollArea(Widget):
    def __init__(self, widget, **kwargs):
        super(ScrollArea, self).__init__(**kwargs)

        self.widget = widget

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.view = QScrollArea()
        self.view.setWidgetResizable(True)
        self.view.setWidget(self.widget)

        self.main_layout.addWidget(self.view)

    def read_data(self):
        return self.widget.read_data()


ScrollAreaWidget = ScrollArea


class SubmitWidget(Widget):
    def __init__(self, form=tuple(),
                 func=lambda *args: 0,
                 doit_text=u"确认表单已填充-执行",
                 margins=5,
                 spacing=5,
                 align=None,
                 **kwargs):
        self.func = call_block(func)
        super(SubmitWidget, self).__init__(**kwargs)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(margins, margins, margins, margins)
        self.main_layout.setSpacing(spacing)
        if align is not None:
            self.main_layout.setAlignment(_align_map[align])

        self.widgets = list()
        for i in form:
            self.main_layout.addWidget(i)
            self.widgets.append(i)

        self.doit_bn = QPushButton(doit_text)
        self.doit_bn.clicked.connect(call_block(self.doit))
        self.main_layout.addWidget(self.doit_bn)

    def doit_value(self):
        for i in self.widgets:
            data = i.read_data()
            for t in data:
                yield t

    def doit(self, *args):
        self.func(*self.doit_value())


class _CollapseButton(Warp):
    state_changed = Signal()

    def __init__(self, text, default_state=False):
        self.close_ico = svg.widget('chevron-right')
        self.close_ico.setFixedSize(QSize(30, 30))
        self.open_ico = svg.widget('chevron-down')
        self.open_ico.setFixedSize(QSize(30, 30))
        self.label = Label(text, False)

        super(_CollapseButton, self).__init__(
            child=HBoxLayout(
                childs=[
                    self.close_ico,
                    self.open_ico,
                    self.label,
                ],
                margins=2,
                spacing=2,
            ),
            left_clicked_callback=lambda *args: self.set_state(not self.state),
        )
        self.state = default_state
        self.set_state(default_state)

    def set_state(self, state):
        self.state = state
        self.open_ico.setVisible(self.state)
        self.close_ico.setVisible(not self.state)
        self.state_changed.emit()

    def paintEvent(self, *args, **kwargs):
        p = QPainter(self)
        p.setPen(QPen(QColor(0, 0, 0, 0)))
        p.setBrush(QBrush(QColor(255, 255, 255, 30)))
        p.drawRect(self.rect())
        p.end()


class Collapse(Warp):
    def __init__(self, body, text='', default_state=False, **kwargs):
        # self.head = CheckBox(info=text, default_state=default_state,
        #                      update_func=self.update_body_state)
        self.head = _CollapseButton(text, default_state)
        self.body = body
        super(Collapse, self).__init__(
            VBoxLayout(
                childs=[self.head,
                        self.body],
                align='top',
                margins=0, spacing=0
            ),
            **kwargs
        )
        self.head.state_changed.connect(self.__update_body_state)
        self.__update_body_state()

    def read_data(self):
        return self.body.read_data()

    def __update_body_state(self):
        if self.head.state:
            self.body.setVisible(True)
        else:
            self.body.setVisible(False)


CollapseWidget = Collapse
