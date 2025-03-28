"""
UI工具模块，提供UI相关的工具函数和类。
"""
import math
from typing import Optional, Tuple, Union

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QSize, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QGraphicsBlurEffect, QGraphicsDropShadowEffect, QWidget


class BlurEffect(QGraphicsBlurEffect):
    """毛玻璃效果类，提供可自定义的毛玻璃效果。"""

    def __init__(self, parent: Optional[QWidget] = None, radius: int = 10):
        """
        初始化毛玻璃效果。

        Args:
            parent: 父窗口
            radius: 模糊半径
        """
        super().__init__(parent)
        self.setBlurRadius(radius)
        self.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)


class ShadowEffect(QGraphicsDropShadowEffect):
    """阴影效果类，提供可自定义的阴影效果。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        color: QColor = QColor(0, 0, 0, 50),
        blur_radius: int = 10,
        offset_x: int = 0,
        offset_y: int = 5,
    ):
        """
        初始化阴影效果。

        Args:
            parent: 父窗口
            color: 阴影颜色
            blur_radius: 模糊半径
            offset_x: X轴偏移
            offset_y: Y轴偏移
        """
        super().__init__(parent)
        self.setColor(color)
        self.setBlurRadius(blur_radius)
        self.setOffset(offset_x, offset_y)


class RoundedRectWidget(QWidget):
    """圆角矩形窗口类，提供可自定义的圆角矩形窗口。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        radius: int = 10,
        background_color: QColor = QColor(255, 255, 255),
        border_color: Optional[QColor] = None,
        border_width: int = 0,
    ):
        """
        初始化圆角矩形窗口。

        Args:
            parent: 父窗口
            radius: 圆角半径
            background_color: 背景颜色
            border_color: 边框颜色
            border_width: 边框宽度
        """
        super().__init__(parent)
        self._radius = radius
        self._background_color = background_color
        self._border_color = border_color
        self._border_width = border_width
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        """
        绘制事件。

        Args:
            event: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 创建圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, self.width(), self.height()), self._radius, self._radius)
        
        # 设置裁剪区域
        painter.setClipPath(path)
        
        # 绘制背景
        painter.fillPath(path, self._background_color)
        
        # 绘制边框
        if self._border_color and self._border_width > 0:
            painter.setPen(self._border_color)
            painter.drawRoundedRect(
                self._border_width // 2,
                self._border_width // 2,
                self.width() - self._border_width,
                self.height() - self._border_width,
                self._radius,
                self._radius,
            )


class GlassWidget(RoundedRectWidget):
    """毛玻璃窗口类，提供可自定义的毛玻璃效果窗口。"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        radius: int = 10,
        background_color: QColor = QColor(255, 255, 255, 200),
        border_color: Optional[QColor] = None,
        border_width: int = 0,
        blur_radius: int = 10,
    ):
        """
        初始化毛玻璃窗口。

        Args:
            parent: 父窗口
            radius: 圆角半径
            background_color: 背景颜色
            border_color: 边框颜色
            border_width: 边框宽度
            blur_radius: 模糊半径
        """
        super().__init__(parent, radius, background_color, border_color, border_width)
        self._blur_radius = blur_radius
        self._blur_effect = BlurEffect(self, blur_radius)
        self.setGraphicsEffect(self._blur_effect)


class AnimationHelper:
    """动画助手类，提供常用的动画效果。"""

    @staticmethod
    def fade_in(
        widget: QWidget,
        duration: int = 300,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        start_value: float = 0.0,
        end_value: float = 1.0,
    ) -> QPropertyAnimation:
        """
        淡入动画。

        Args:
            widget: 目标窗口
            duration: 动画持续时间（毫秒）
            easing: 缓动曲线
            start_value: 起始值
            end_value: 结束值

        Returns:
            动画对象
        """
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def fade_out(
        widget: QWidget,
        duration: int = 300,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        start_value: float = 1.0,
        end_value: float = 0.0,
    ) -> QPropertyAnimation:
        """
        淡出动画。

        Args:
            widget: 目标窗口
            duration: 动画持续时间（毫秒）
            easing: 缓动曲线
            start_value: 起始值
            end_value: 结束值

        Returns:
            动画对象
        """
        return AnimationHelper.fade_in(widget, duration, easing, start_value, end_value)

    @staticmethod
    def slide_in(
        widget: QWidget,
        direction: str = "right",
        duration: int = 300,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> QPropertyAnimation:
        """
        滑入动画。

        Args:
            widget: 目标窗口
            direction: 方向，可选值：left, right, top, bottom
            duration: 动画持续时间（毫秒）
            easing: 缓动曲线

        Returns:
            动画对象
        """
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        
        start_rect = widget.geometry()
        end_rect = widget.geometry()
        
        if direction == "left":
            start_rect.setX(widget.x() - widget.width())
        elif direction == "right":
            start_rect.setX(widget.x() + widget.width())
        elif direction == "top":
            start_rect.setY(widget.y() - widget.height())
        elif direction == "bottom":
            start_rect.setY(widget.y() + widget.height())
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation

    @staticmethod
    def slide_out(
        widget: QWidget,
        direction: str = "right",
        duration: int = 300,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> QPropertyAnimation:
        """
        滑出动画。

        Args:
            widget: 目标窗口
            direction: 方向，可选值：left, right, top, bottom
            duration: 动画持续时间（毫秒）
            easing: 缓动曲线

        Returns:
            动画对象
        """
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        
        start_rect = widget.geometry()
        end_rect = widget.geometry()
        
        if direction == "left":
            end_rect.setX(widget.x() - widget.width())
        elif direction == "right":
            end_rect.setX(widget.x() + widget.width())
        elif direction == "top":
            end_rect.setY(widget.y() - widget.height())
        elif direction == "bottom":
            end_rect.setY(widget.y() + widget.height())
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation

    @staticmethod
    def scale(
        widget: QWidget,
        duration: int = 300,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
        start_value: float = 0.8,
        end_value: float = 1.0,
    ) -> QPropertyAnimation:
        """
        缩放动画。

        Args:
            widget: 目标窗口
            duration: 动画持续时间（毫秒）
            easing: 缓动曲线
            start_value: 起始值
            end_value: 结束值

        Returns:
            动画对象
        """
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(easing)
        return animation


def create_rounded_pixmap(pixmap: QPixmap, radius: int) -> QPixmap:
    """
    创建圆角图片。

    Args:
        pixmap: 原始图片
        radius: 圆角半径

    Returns:
        圆角图片
    """
    rounded_pixmap = QPixmap(pixmap.size())
    rounded_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(rounded_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 创建圆角矩形路径
    path = QPainterPath()
    path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
    
    # 设置裁剪区域
    painter.setClipPath(path)
    
    # 绘制图片
    painter.drawPixmap(0, 0, pixmap)
    
    return rounded_pixmap


def create_circular_pixmap(pixmap: QPixmap) -> QPixmap:
    """
    创建圆形图片。

    Args:
        pixmap: 原始图片

    Returns:
        圆形图片
    """
    # 确保图片是正方形
    size = min(pixmap.width(), pixmap.height())
    pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
    
    # 创建圆形图片
    circular_pixmap = QPixmap(size, size)
    circular_pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(circular_pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 创建圆形路径
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    
    # 设置裁剪区域
    painter.setClipPath(path)
    
    # 绘制图片
    painter.drawPixmap(0, 0, pixmap)
    
    return circular_pixmap


def hex_to_qcolor(hex_color: str) -> QColor:
    """
    将十六进制颜色转换为QColor。

    Args:
        hex_color: 十六进制颜色字符串，格式：#RRGGBB 或 #AARRGGBB

    Returns:
        QColor对象
    """
    hex_color = hex_color.lstrip("#")
    
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return QColor(r, g, b)
    elif len(hex_color) == 8:
        a = int(hex_color[0:2], 16)
        r = int(hex_color[2:4], 16)
        g = int(hex_color[4:6], 16)
        b = int(hex_color[6:8], 16)
        return QColor(r, g, b, a)
    else:
        return QColor(0, 0, 0)


def qcolor_to_hex(color: QColor) -> str:
    """
    将QColor转换为十六进制颜色。

    Args:
        color: QColor对象

    Returns:
        十六进制颜色字符串，格式：#RRGGBB
    """
    return f"#{color.red():02x}{color.green():02x}{color.blue():02x}"


def qcolor_to_rgba(color: QColor) -> str:
    """
    将QColor转换为RGBA颜色。

    Args:
        color: QColor对象

    Returns:
        RGBA颜色字符串，格式：rgba(r, g, b, a)
    """
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha() / 255.0})"


def get_contrasting_text_color(background_color: QColor) -> QColor:
    """
    获取与背景颜色对比的文本颜色。

    Args:
        background_color: 背景颜色

    Returns:
        文本颜色
    """
    # 计算亮度
    luminance = (0.299 * background_color.red() + 0.587 * background_color.green() + 0.114 * background_color.blue()) / 255
    
    # 如果亮度大于0.5，返回黑色，否则返回白色
    if luminance > 0.5:
        return QColor(0, 0, 0)
    else:
        return QColor(255, 255, 255)


def get_color_with_opacity(color: QColor, opacity: float) -> QColor:
    """
    获取带有不透明度的颜色。

    Args:
        color: 原始颜色
        opacity: 不透明度（0-1）

    Returns:
        带有不透明度的颜色
    """
    return QColor(color.red(), color.green(), color.blue(), int(opacity * 255))


def get_lighter_color(color: QColor, factor: float = 0.2) -> QColor:
    """
    获取更亮的颜色。

    Args:
        color: 原始颜色
        factor: 亮度因子（0-1）

    Returns:
        更亮的颜色
    """
    h, s, l, a = color.getHslF()
    l = min(1.0, l + factor)
    result = QColor()
    result.setHslF(h, s, l, a)
    return result


def get_darker_color(color: QColor, factor: float = 0.2) -> QColor:
    """
    获取更暗的颜色。

    Args:
        color: 原始颜色
        factor: 暗度因子（0-1）

    Returns:
        更暗的颜色
    """
    h, s, l, a = color.getHslF()
    l = max(0.0, l - factor)
    result = QColor()
    result.setHslF(h, s, l, a)
    return result
