# -*-coding:utf-8 -*-
"""
:创建时间: 2022/7/28 0:14
:作者: 苍之幻灵
:我的主页: https://cpcgskill.com
:Github: https://github.com/cpcgskill
:QQ: 2921251087
:aboutcg: https://www.aboutcg.org/teacher/54335
:bilibili: https://space.bilibili.com/351598127
:爱发电: https://afdian.net/@Phantom_of_the_Cang

"""
from __future__ import unicode_literals, print_function, division

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

_gui_library = None
try:
    from PySide2.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
except:
    from PySide.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from cpform.widget.core import *
from cpform.utils import *

_bytes_t = type(b'')
_unicode_t = type('')

__all__ = ['HttpError', 'HttpRequest', 'HttpGet', 'HttpPost', 'HttpPut', 'HttpPatch', 'HttpDelete', 'HttpHead',
           'HttpOptions']


class HttpError(object):
    class ConnectionRefusedError(object): pass

    class RemoteHostClosedError(object): pass

    class HostNotFoundError(object): pass

    class TimeoutError(object): pass

    class SslHandshakeFailedError(object): pass

    class InternalServerError(object): pass

    class UnknownError(object): pass


_QT_ERROR_TO_CPFORM_ERROR_MAP = {
    QNetworkReply.NetworkError.ConnectionRefusedError: HttpError.ConnectionRefusedError,
    QNetworkReply.NetworkError.RemoteHostClosedError: HttpError.RemoteHostClosedError,
    QNetworkReply.NetworkError.HostNotFoundError: HttpError.HostNotFoundError,
    QNetworkReply.NetworkError.TimeoutError: HttpError.TimeoutError,
    QNetworkReply.NetworkError.SslHandshakeFailedError: HttpError.SslHandshakeFailedError,
    # QNetworkReply.NetworkError.UnknownContentError if is_pyside else QNetworkReply.NetworkError.InternalServerError: HttpError.InternalServerError,
}

_DEBUG = False


class HttpRequest(Warp):
    def __init__(self, child, url, method='GET', headers=dict(), body=b'', success_call=None, fail_call=None):
        self.success_call = success_call
        self.fail_call = fail_call
        if type(method) == _unicode_t:
            method = method.encode('utf-8')
        if type(body) == _unicode_t:
            body = body.encode('utf-8')
        super(HttpRequest, self).__init__(child)
        self.manager = QNetworkAccessManager(self)
        # self.manager.finished[QNetworkReply].connect(self.__success_call)
        request = QNetworkRequest(QUrl(url))
        for k, v in headers.items():
            if type(k) == _unicode_t:
                k = k.encode('utf-8')
            if type(v) == _unicode_t:
                v = v.encode('utf-8')
            request.setRawHeader(k, v)
        self.in_bytes = QByteArray(body)
        self.in_buffer = QBuffer(self.in_bytes)
        self.in_buffer.open(QBuffer.ReadOnly)
        self.reply = self.manager.sendCustomRequest(
            request,
            method,
            self.in_buffer,
        )  # type: QNetworkReply
        self.reply.finished.connect(self.__call)
        if runtime() == 'maya' and runtime_version() < 2018:
            self.reply.ignoreSslErrors()
        self.in_buffer.setParent(self.reply)

    @call_block
    def __call(self):
        """
        # :type reply: QNetworkReply
        :return:
        """
        error = self.reply.error()
        status_code = self.reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        headers = {bytes(i): bytes(self.reply.rawHeader(i)) for i in self.reply.rawHeaderList()}
        body = bytes(self.reply.readAll())
        if _DEBUG:
            print('reply:', self.reply, self.reply.url())
        if error == QNetworkReply.NetworkError.NoError or status_code is not None:
            if _DEBUG:
                print('success')
                print('code: ', type(status_code), status_code)
                print('headers: ', headers)
                print('body: ', repr(body))
            if self.success_call is not None:
                self.success_call(status_code, headers, body)
        elif error in _QT_ERROR_TO_CPFORM_ERROR_MAP:
            if _DEBUG:
                print('KnownError')
                print('error: ', type(error), error)
                print('code: ', type(status_code), status_code)
                print('headers: ', headers)
                print('body: ', repr(body))
            if self.fail_call is not None:
                self.fail_call(_QT_ERROR_TO_CPFORM_ERROR_MAP[error])
        else:
            if _DEBUG:
                print('UnknownError')
                print('error: ', type(error), error)
                print('code: ', type(status_code), status_code)
                print('headers: ', headers)
                print('body: ', repr(body))
            if self.fail_call is not None:
                self.fail_call(HttpError.UnknownError)


class HttpGet(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpGet, self).__init__(child, url, method='GET', headers=headers, body=body,
                                      success_call=success_call, fail_call=fail_call)


class HttpPost(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpPost, self).__init__(child, url, method='POST', headers=headers, body=body,
                                       success_call=success_call, fail_call=fail_call)


class HttpPut(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpPut, self).__init__(child, url, method='PUT', headers=headers, body=body,
                                      success_call=success_call, fail_call=fail_call)


class HttpPatch(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpPatch, self).__init__(child, url, method='PATCH', headers=headers, body=body,
                                        success_call=success_call, fail_call=fail_call)


class HttpDelete(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpDelete, self).__init__(child, url, method='DELETE', headers=headers, body=body,
                                         success_call=success_call, fail_call=fail_call)


class HttpHead(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpHead, self).__init__(child, url, method='HEAD', headers=headers, body=body,
                                       success_call=success_call, fail_call=fail_call)


class HttpOptions(HttpRequest):
    def __init__(self, child, url, headers=dict(), body=b'', success_call=None, fail_call=None):
        super(HttpOptions, self).__init__(child, url, method='OPTIONS', headers=headers, body=body,
                                          success_call=success_call, fail_call=fail_call)
