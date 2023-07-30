# -*-coding:utf-8 -*-
"""
:创建时间: 2022/3/13 17:29
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:QQ: 2921251087
:爱发电: https://afdian.net/@Phantom_of_the_Cang
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127

"""
from __future__ import unicode_literals, print_function

import functools
import io
import os
import sys

import maya.cmds as mc
from maya.OpenMaya import MGlobal as MGlobal_api1
from maya.api.OpenMaya import MGlobal as MGlobal_api2

_bytes_t = type(b'')
_unicode_t = type('')


def undo_block(fn):
    @functools.wraps(fn)
    def _(*args, **kwargs):
        mc.undoInfo(ock=True)
        try:
            return fn(*args, **kwargs)
        finally:
            mc.undoInfo(cck=True)

    return _


def decode_string(s):
    u"""
    字符串解码函数

    :param s:
    :return:
    """
    if isinstance(s, _unicode_t):
        return s
    elif isinstance(s, _bytes_t):
        try:
            return s.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return s.decode("GB18030")
            except UnicodeDecodeError:
                try:
                    return s.decode("Shift-JIS")
                except UnicodeDecodeError:
                    try:
                        return s.decode("EUC-KR")
                    except UnicodeDecodeError:
                        return _unicode_t(s)
    else:
        raise TypeError


def format_exception(ex_type, ex_value, ex_traceback):
    # 分割线
    fgx = "#" * 126 + "\n"

    str_io = io.StringIO("")

    str_io.write("{}: {}\n".format(ex_type.__name__, ex_value))
    i = 1
    while ex_traceback:
        tracebackCode = ex_traceback.tb_frame.f_code
        tb_lineno = ex_traceback.tb_lineno - 1
        co_filename = tracebackCode.co_filename
        co_name = tracebackCode.co_name
        if os.path.isfile(co_filename):
            try:
                with open(co_filename, "rb") as f:
                    str_io.write('  file "{}"  line {}, in {}: \n'.format(
                        co_filename,
                        tb_lineno,
                        co_name,
                    ))

                    str_io.write(fgx)

                    lines = f.read().decode('utf-8').splitlines()
                    lines = [decode_string(t) for t in
                             lines[max(tb_lineno - 3, 0):min(tb_lineno + 4, len(lines))]]

                    for i in range(len(lines)):
                        if i == 3:
                            str_io.write(">> " + lines[i].ljust(120, ' ') + " ##\n")
                        else:
                            str_io.write("## " + lines[i].ljust(120, ' ') + " ##\n")

                    str_io.write(fgx)
            except:
                str_io.write('  file "{}"  line {}, in {}\n'.format(
                    co_filename,
                    tb_lineno,
                    co_name,
                ))
        else:
            str_io.write('  file "{}"  line {}, in {}\n'.format(
                co_filename,
                tb_lineno,
                co_name,
            ))
        ex_traceback = ex_traceback.tb_next
        i += 1
    return str_io.getvalue()


# 异常输出格式化头
format_exception_handle = format_exception
# 异常输出头
exception_output_handle = MGlobal_api2.displayError


# 基础自动异常输出异常类
class SimpleOutputException(Exception): pass


# 简单输出的异常类列表， 输出格式为'{异常类型}: {异常信息}'
simple_output_ex_types = [SimpleOutputException]


def exception_responder(fn):
    """

    :return:
    """

    @functools.wraps(fn)
    def _(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            for et in simple_output_ex_types:
                if isinstance(ex_value, et):
                    exception_output_handle("{}: {}".format(et.__name__, ex_value))
                    return
            ex_str = format_exception_handle(ex_type, ex_value, ex_traceback)
            exception_output_handle(ex_str)
            return

    return _


def execute_deferred(fn):
    @functools.wraps(fn)
    def _(*args, **kwargs):
        from maya.utils import executeDeferred as _executeDeferred
        if MGlobal_api1.mayaState() == MGlobal_api1.kInteractive:
            _executeDeferred(fn, *args, **kwargs)
        else:
            fn(*args, **kwargs)
    return _


def call_block(fn):
    return functools.wraps(fn)(undo_block(exception_responder(fn)))
