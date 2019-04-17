from PySide2.QtCore import QAbstractAnimation, QEasingCurve, QObject, QPropertyAnimation, QSize
from PySide2.QtWidgets import QPushButton, QWidget

from modules.detect_language import get_translation
from modules.log import init_logging

LOGGER = init_logging(__name__)

# translate strings
lang = get_translation()
lang.install()
_ = lang.gettext


class KnechtExpandableWidget(QObject):
    expand_height = 250

    def __init__(self, widget: QWidget, expand_btn: QPushButton=None, collapsible_widget: QWidget=None):
        """ Method to add expandable widget functionality to a widget containing an collapsible widget

        :param widget: the widget which size will be changed
        :param expand_btn: the button which will toggle the expanded/collapsed state
        :param collapsible_widget: the widget contained inside >>widget<< whose minimum size height hint will be
                                   set to 0 so it becomes collapsible
        """
        super(KnechtExpandableWidget, self).__init__()

        self.widget = widget

        self.size_animation = QPropertyAnimation(self.widget, b'size')
        self.size_animation.setDuration(150)
        self.size_animation.setEasingCurve(QEasingCurve.OutCurve)
        self.size_animation.finished.connect(self.widget.updateGeometry)

        self.expand_toggle_btn = expand_btn or QPushButton(self)
        self.expand_toggle_btn.setCheckable(True)
        self.expand_toggle_btn.released.connect(self.expand_widget)

        self.collapsible_widget = collapsible_widget or QWidget(self)
        self.collapsible_widget.minimumSizeHint = self._custom_minimum_size_hint

        self.org_resize = self.widget.resizeEvent
        self.widget.resizeEvent = self._custom_resize

        LOGGER.debug('Initialized Expandable Widget with parent: %s', self.parent())

    def _custom_minimum_size_hint(self):
        return QSize(self.collapsible_widget.sizeHint().width(), 0)

    def _custom_resize(self, event):
        self.org_resize(event)
        collapsed_height = self.widget.minimumSizeHint().height()

        if self.size_animation.state() != QAbstractAnimation.Running:
            if event.size().height() > collapsed_height:
                self.expand_toggle_btn.setChecked(True)
            else:
                self.expand_toggle_btn.setChecked(False)

        event.accept()

    def toggle_expand(self, immediate: bool=False):
        if self.expand_toggle_btn.isChecked():
            self.expand_toggle_btn.setChecked(False)
            self.expand_widget(immediate=immediate)
        else:
            self.expand_toggle_btn.setChecked(True)
            self.expand_widget(immediate=immediate)

    def expand_widget(self, immediate: bool=False):
        if self.expand_toggle_btn.isChecked():
            expand_height = self.widget.size().height()
        else:
            expand_height = 0

        expanded_size = QSize(self.widget.size().width(), self.widget.minimumSizeHint().height() + expand_height)

        self.size_animation.setStartValue(self.widget.size())
        self.size_animation.setEndValue(expanded_size)

        if immediate:
            self.widget.resize(expanded_size)
            self.widget.updateGeometry()
        else:
            self.size_animation.start()
