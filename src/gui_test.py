# -*-coding:utf-8 -*-
"""
:创建时间: 2022/9/9 8:44
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *

    gui_runtime = 'PyQt6'
except ImportError:
    try:
        from PySide6.QtGui import *
        from PySide6.QtCore import *
        from PySide6.QtWidgets import *

        gui_runtime = 'PySide6'
    except ImportError:
        try:
            from PyQt5.QtWidgets import *
            from PyQt5.QtCore import *
            from PyQt5.QtGui import *

            gui_runtime = 'PyQt5'
        except ImportError:
            try:
                from PySide2.QtGui import *
                from PySide2.QtCore import *
                from PySide2.QtWidgets import *

                gui_runtime = 'PySide2'
            except ImportError:
                from PySide.QtGui import *
                from PySide.QtCore import *

                gui_runtime = 'PySide'

try:
    from shiboken6 import *
except ImportError:
    try:
        from shiboken2 import *
    except ImportError:
        from shiboken import *
import sys

app = QApplication(sys.argv)
import cpmel.cmds as cc
from gui import create_main_window

if __name__ == '__main__':
    from maya_test_tools import open_file, question_open_maya_gui

    cc.mel.eval(
r'''
polySphere -r 1 -sx 20 -sy 20 -ax 0 1 0 -cuv 2 -ch off;
polySphere -r 1 -sx 20 -sy 20 -ax 0 1 0 -cuv 2 -ch off;

select -r pSphere2.vtx[199] ;
softSelect -softSelectEnabled true -ssd 0.811789 -sud 0.5 ;
move -r -os -wd 0.550086 0 0 ;
select -d pSphere2.vtx[199] ;

select -cl  ;
select -add pSphere2 ;
select -add pSphere1 ;
blendShape;

select -r pSphere2 ;
duplicate -rr;

setAttr "blendShape1.pSphere2" 0.4;
blendShape -e -ib -tc on -ibt absolute -t |pSphere1|pSphereShape1 0 pSphere3 0.4  blendShape1;

setAttr "blendShape1.pSphere2" 0.6;
blendShape -e -ib -tc on -ibt absolute -t |pSphere1|pSphereShape1 0 pSphere3 0.6  blendShape1;

select -r pSphere1 ;
'''
)

    create_main_window()

    app.exec_()

    question_open_maya_gui()
