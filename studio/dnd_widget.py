"""
Ispired by https://www.pythonguis.com/faq/pyqt6-drag-drop-widgets/
Some code by chatGPT
"""

from PyQt6.QtCore import QMimeData, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class DragTargetIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(25, 5, 25, 5)
        self.setStyleSheet(
            "QLabel { background-color: #ccc; border: 1px solid black; }"
        )


class DragItemContainer(QWidget):
    def __init__(self, inner_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not inner_widget.reorder_data:
            raise ValueError("Inner widget must have a data attribute for reordering")
        self.inner_widget = inner_widget
        layout = QVBoxLayout()

        # Draggable area in the top left corner
        self.drag_handle = QLabel(self)
        self.drag_handle.setStyleSheet("background-color: lightgray; padding: 5px;")
        self.drag_handle.setFixedSize(20, 20)  # Customize as needed

        # Add drag handle and the main widget to layout
        layout.addWidget(
            self.drag_handle,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        layout.addWidget(inner_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

    def mouseMoveEvent(self, e):
        # Check if the mouse position is within the drag handle area
        if (
            e.buttons() == Qt.MouseButton.LeftButton
            and self.drag_handle.geometry().contains(e.pos())
        ):
            # Initiate drag from the drag handle
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size().width() * 2, self.size().height() * 2)
            pixmap.setDevicePixelRatio(2)
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)
            self.show()  # Show this widget again if it's dropped outside


class DragWidget(QWidget):
    on_order_change = pyqtSignal(list)

    def __init__(self, orientation=Qt.Orientation.Vertical):
        super().__init__()
        self.setAcceptDrops(True)
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        self._drag_target_indicator = DragTargetIndicator()
        self.blayout.addWidget(self._drag_target_indicator)
        self._drag_target_indicator.hide()
        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        # Only accept drag if source is from this DragWidget
        if e.source().parent() == self:
            e.accept()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self._drag_target_indicator.hide()
        e.accept()

    def dragMoveEvent(self, e):
        # Only allow move if source is from this DragWidget
        if e.source().parent() == self:
            index = self._find_drop_location(e)
            if index is not None:
                self._drag_target_indicator.setFixedSize(e.source().size())
                self.blayout.insertWidget(index, self._drag_target_indicator)
                e.source().hide()
                self._drag_target_indicator.show()
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        # Only allow drop if source is from this DragWidget
        if e.source().parent() == self:
            widget = e.source()
            self._drag_target_indicator.hide()
            index = self.blayout.indexOf(self._drag_target_indicator)
            if index is not None:
                self.blayout.insertWidget(index, widget)
                self.on_order_change.emit(self.get_item_data())
                widget.show()
                self.blayout.activate()
            e.accept()
        else:
            e.ignore()

    def _find_drop_location(self, e):
        pos = e.position().toPoint()
        spacing = self.blayout.spacing() / 2

        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()
            widget_geometry = w.geometry()

            if self.orientation == Qt.Orientation.Vertical:
                # Calculate vertical drop zone based on widget height and position
                drop_here = (
                    pos.y() >= widget_geometry.top() - spacing
                    and pos.y() <= widget_geometry.bottom() + spacing
                )
            else:
                # Calculate horizontal drop zone based on widget width and position
                drop_here = (
                    pos.x() >= widget_geometry.left() - spacing
                    and pos.x() <= widget_geometry.right() + spacing
                )

            if drop_here:
                return n

        # Default to last position if no match found
        return self.blayout.count() - 1

    def add_item(self, item):
        self.blayout.addWidget(item)

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            w = self.blayout.itemAt(n).widget()
            if w != self._drag_target_indicator:
                data.append(w.inner_widget.reorder_data)
        return data
