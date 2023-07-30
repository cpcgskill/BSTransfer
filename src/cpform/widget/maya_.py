# -*-coding:utf-8 -*-
"""
:创建时间: 2022/7/10 3:29
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

import maya.cmds as mc
from cpform.utils import call_block
from cpform.exc import CPMelFormException
from cpform.widget.core import *

__all__ = ['Select', 'SelectWidget', 'SelectListWidget', 'CreateObjectWidget']


class SelectWidget(Warp):
    def __init__(self, load_end_func=None, mobject_type=None, *args, **kwargs):
        self.load_end_func = load_end_func
        self.mobject_type = mobject_type
        self.line_edit = LineEdit(*args, **kwargs)
        self.load_bn = Button('载入', func=lambda *args: self.load())
        super(SelectWidget, self).__init__(HBoxLayout(childs=[self.line_edit, self.load_bn], margins=0, spacing=5))

    @call_block
    def load(self):
        if self.mobject_type is None:
            sel = mc.ls(sl=True)
        else:
            sel = mc.ls(sl=True, typ=self.mobject_type)
        if len(sel) < 1:
            raise CPMelFormException("选择一个有效物体")
        self.line_edit.set_text(sel[0])
        if self.load_end_func is not None:
            self.load_end_func(sel[0])

    def read_data(self):
        return self.line_edit.read_data()


Select = SelectWidget


class SelectListWidget(Warp):
    def __init__(self, load_end_func=None, mobject_type=None, *args, **kwargs):
        self.load_end_func = load_end_func
        self.mobject_type = mobject_type

        self.line_edit = LineEdit(*args, **kwargs)
        self.load_bn = Button('载入', func=lambda *args: self.load())
        super(SelectListWidget, self).__init__(HBoxLayout(childs=[self.line_edit, self.load_bn], margins=0, spacing=5))

    @call_block
    def load(self):
        if self.mobject_type is None:
            sel = mc.ls(sl=True)
        else:
            sel = mc.ls(sl=True, typ=self.mobject_type)
        self.line_edit.set_text(u";".join(sel))
        if self.load_end_func is not None:
            self.load_end_func(sel[0])

    def read_data(self):
        return [self.line_edit.read_data()[0].split(";")]


SelectList = SelectListWidget


class CreateObjectWidget(Warp):
    def __init__(self, info, create_object, delete_object, find_object):
        """

        :type info: unicode
        :type create_object: function
        :type delete_object: function
        :type find_object: function
        """
        self.create_object = create_object
        self.delete_object = delete_object
        self.find_object = find_object
        self.checkbox = CheckBox(
            info=info,
            default_state=self._obj_exists(),
            update_func=lambda state: self._create_object() if state else self._delete_object()
        )
        super(CreateObjectWidget, self).__init__(
            HBoxLayout(
                childs=[
                    self.checkbox,
                ]
            )
        )

    def _create_object(self):
        try:
            self.create_object()
        finally:
            self.checkbox.set_state(self._obj_exists())

    def _delete_object(self):
        try:
            self.delete_object()
        finally:
            self.checkbox.set_state(self._obj_exists())

    def _obj_exists(self):
        return self.find_object() is not None

    def read_data(self):
        return [self.find_object()]


CreateObject = CreateObjectWidget
