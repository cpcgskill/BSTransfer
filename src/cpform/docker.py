#!/usr/bin/python
# -*-coding:utf-8 -*-
"""
:创建时间: 2020/11/9 11:07
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

import os
import sys

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

import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as mc

try:
    if hasattr(mc, 'about'):
        ptr_t = int if sys.version_info.major > 2 else long
        mui = wrapInstance(ptr_t(OpenMayaUI.MQtUtil.mainWindow()), QWidget)
    else:
        mui = None
except:
    mui = None

from cpform.utils import call_block
from cpform.widget.core import ToggleWidget, WarpWidget, BackgroundWidget, VBoxLayout, Widget
from cpform.exc import CPMelFormException

PATH = os.path.dirname(os.path.abspath(__file__))
ICON = os.sep.join([PATH, 'icon.png'])
QSS = os.sep.join([PATH, 'qss.css'])
HEAD = os.sep.join([PATH, 'head.png'])
FONT = os.sep.join([PATH, 'NotoSansHans-Black.otf'])
with open(QSS, 'rb') as f:
    QSS_STRING = f.read().decode('utf-8')


def _initialization_Widget(widget):
    widget.setStyleSheet(QSS_STRING)
    id_ = QFontDatabase.addApplicationFont(FONT)
    QFontDatabase.applicationFontFamilies(id_)


class DockerWarp(object):
    def __init__(self, delete_callback):
        self._delete_callback = delete_callback

    def delete_docker(self):
        self._delete_callback()
        return self


class DialogDocker(QDialog):
    def __init__(self, form, icon=None, title='CPWindow'):
        """

        :type form: Widget
        :type icon: AnyStr
        :type title: AnyStr
        """
        if icon is None:
            icon = ICON
        super(DialogDocker, self).__init__(mui)
        _initialization_Widget(self)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self.toggle = ToggleWidget(BackgroundWidget(form, color='#444444'))

        self._main_layout.addWidget(self.toggle)


class PopupMenuDocker(QDialog):
    def __init__(self, form, close_callback=None):
        """

        :type form: Widget
        """
        self._is_delete = False

        self._close_callback = None
        if callable(close_callback):
            self._close_callback = call_block(close_callback)

        super(PopupMenuDocker, self).__init__()
        _initialization_Widget(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._main_layout.addWidget(BackgroundWidget(form, color='#444444'))

    def showEvent(self, *args, **kwargs):
        self.setFocus()
        # 监测焦点变化并关闭菜单
        def _on_focus_changed(old, new):
            if not self._is_delete:
                if new is None or not self.isAncestorOf(new):
                    self.delete_popup_menu()

        QApplication.instance().focusChanged.connect(_on_focus_changed)

    def closeEvent(self, *args, **kwargs):
        if self._close_callback is not None:
            self._close_callback()

    def delete_popup_menu(self):
        if not self._is_delete:
            self.close()
            self.deleteLater()
            self._is_delete = True


class _HeadWidget(WarpWidget):
    def __init__(self):
        head_label = QLabel()
        pix = QPixmap(HEAD)
        head_label.setPixmap(pix)

        super(_HeadWidget, self).__init__(
            child=head_label,
            left_clicked_callback=lambda *args: QDesktopServices.openUrl(QUrl(u'https://www.cpcgskill.com')),
            fixed_width=pix.width(),
            fixed_height=pix.height(),
        )

    def read_data(self):
        return []


class WindowDocker(QWidget):
    def __init__(self, form, icon=None, title='CPWindow'):
        """

        :type form: Widget
        :type icon: AnyStr
        :type title: AnyStr
        """
        if icon is None:
            icon = ICON
        super(WindowDocker, self).__init__(mui)
        _initialization_Widget(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self.toggle = ToggleWidget(BackgroundWidget(form, color='#444444'))

        self._main_layout.addWidget(self.toggle)

    def set_form(self, form, icon, title):
        if icon is None:
            icon = ICON
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.toggle.toggle_to(BackgroundWidget(form, color='#444444'))


_this_dialog = None  # type: DialogDocker or None


def dialog_docker(form, icon=None, title='CPWindow'):
    """
    build函数提供将表单(列表 or 元组)编译为界面的功能

    :type form: Widget
    :param form: 表单
    :param icon: 图标路径
    :param title: 标题
    :return:
    """
    global _this_dialog
    old_this_dialog = _this_dialog
    try:
        _this_dialog = DialogDocker(form, icon, title)
        _this_dialog.exec_()
        _this_dialog.close()
        _this_dialog.deleteLater()
        return _this_dialog
    finally:
        _this_dialog = old_this_dialog


def quit_dialog_docker():
    global _this_dialog
    if _this_dialog is not None:
        _this_dialog.close()


def popup_menu_docker(form, pos=None, from_widget=None, close_callback=None):
    widget = PopupMenuDocker(form, close_callback=close_callback)
    if pos is None:
        pos = QCursor().pos()
    widget.move(pos)
    if from_widget is not None:
        widget.move(from_widget.mapToGlobal(QPoint(0, from_widget.height())))
        widget.setFixedWidth(from_widget.width())
    widget.show()

    return DockerWarp(delete_callback=widget.delete_popup_menu)


_docker_table = dict()


def get_docker(name, default=None):
    return _docker_table.get(name, default)


def close_docker(name='CPWindow'):
    widget = _docker_table.get(name, None)
    if widget is None:
        raise CPMelFormException('容器不存在')
    widget.close()


def delete_docker(name='CPWindow'):
    widget = _docker_table.get(name, None)
    if widget is None:
        raise CPMelFormException('容器不存在')
    widget.close()
    widget.deleteLater()
    _docker_table.pop(name)


def default_docker(form, icon=None, name='CPWindow', title=None):
    """
    build函数提供将表单(列表 or 元组)编译为界面的功能

    :type form: Widget
    :param form: 表单
    :param name: docker的名称
    :param icon: 图标路径
    :param title: 标题
    :return:
    """
    if title is None:
        title = name
    if name in _docker_table:
        widget = _docker_table[name]
        widget.set_form(form, icon, title)
    else:
        widget = WindowDocker(form, icon, title)
    _docker_table[name] = widget
    if not widget.isVisible():
        widget.show()


def logo_docker(form, icon=None, name='CPWindow', title=None):
    """
    build函数提供将表单(列表 or 元组)编译为界面的功能

    :type form: Widget
    :param form: 表单
    :param name: docker的名称
    :param icon: 图标路径
    :param title: 标题
    :return:
    """
    form = VBoxLayout(
        childs=[_HeadWidget(), form]
    )
    default_docker(form, icon, name, title)
