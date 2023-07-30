# -*-coding:utf-8 -*-
"""
:创建时间: 2022/7/25 5:54
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

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

from cpform.widget.core import *
from cpform.utils import call_block
__all__ = ['Process']


class Process(Warp):
    def __init__(self, child, command, args=[], workdir=None, stdin=None, success_call=None, fail_call=None):
        """
        :type child: Widget
        :type command: unicode
        :type args: unicode
        :type workdir: unicode
        :type stdin: bytes
        :type success_call: function
        :type fail_call: function
        """
        self.success_call = success_call
        self.fail_call = fail_call
        super(Process, self).__init__(child)
        self.process = QProcess()
        self.process.finished.connect(self.__call)
        if workdir is not None:
            self.process.setWorkingDirectory(workdir)
        self.process.start(command, args)
        if stdin is not None:
            self.process.write(stdin)

    @call_block
    def __call(self, *args, **kwargs):
        exit_code = self.process.exitCode()
        exit_status = self.process.exitStatus()
        stdout = bytes(self.process.readAllStandardOutput())
        stderr = bytes(self.process.readAllStandardError())
        if exit_status == QProcess.ExitStatus.NormalExit:
            if self.success_call is not None:
                self.success_call(exit_code, stdout, stderr)
        else:
            if self.fail_call is not None:
                self.fail_call(exit_code, stdout, stderr)
