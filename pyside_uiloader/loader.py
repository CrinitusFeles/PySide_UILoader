from pathlib import Path
from PySide6 import QtWidgets, QtCore
from PySide6.QtUiTools import QUiLoader


widgets_tree: dict = {}


def save_attr(root_widget: QtCore.QObject, object_name: str,
              obj: QtCore.QObject,
              object_parent: QtCore.QObject):
    setattr(root_widget, object_name, obj)
    # print(f'"{object_name}": {type(obj)} {object_parent}')
    # return {object_parent.objectName(): object_name}


CONTAINERS = (
    QtWidgets.QTabWidget | QtWidgets.QStackedWidget
)


def extract_widgets(parent: QtCore.QObject, layout: QtWidgets.QLayout) -> None:
    count: int = layout.count()
    save_attr(parent, layout.objectName(), layout, layout.parent())
    for i in range(count):
        item: QtWidgets.QLayoutItem | None = layout.itemAt(i)
        if isinstance(item, QtWidgets.QLayout):
            extract_widgets(parent, item)
        elif isinstance(item, QtWidgets.QWidgetItem):
            widget: QtWidgets.QWidget = item.wid  # type: ignore
            save_attr(parent, widget.objectName(), widget, layout)
            widget_layout: QtWidgets.QLayout | None = widget.layout()
            if isinstance(widget, QtWidgets.QScrollArea):
                container: QtWidgets.QWidget = widget.widget()
                container_layout: QtWidgets.QLayout | None = container.layout()
                if container_layout:
                    extract_widgets(parent, container_layout)
            elif isinstance(widget, CONTAINERS):
                if isinstance(widget, QtWidgets.QTabWidget):
                    count = widget.tabBar().count()
                else:
                    count = widget.count()
                for i in range(count):
                    tab: QtWidgets.QWidget = widget.widget(i)
                    save_attr(parent, tab.objectName(), tab, tab.parent())
                    tab_layout: QtWidgets.QLayout | None = tab.layout()
                    if tab_layout:
                        extract_widgets(parent, tab_layout)
            elif widget_layout:
                extract_widgets(parent, widget_layout)
            else:
                ...
        else:  # QSpacerItem
            ...


def loadUi(path: str | Path, parent: QtWidgets.QWidget) -> None:
    loader = QUiLoader()
    w: QtWidgets.QWidget = loader.load(path)
    parent.resize(w.size())
    layout: QtWidgets.QLayout | None = w.layout()
    if layout:
        extract_widgets(parent, layout)
        parent.setLayout(layout)
    QtCore.QMetaObject.connectSlotsByName(parent)
