from arche.interfaces import IBaseView
from arche.interfaces import IViewInitializedEvent
from fanstatic import Library
from fanstatic import Resource

from js.jqueryui import ui_sortable
from js.jqueryui_touch_punch import touch_punch

library = Library('voteit_stv', 'static')
sortable_styles = Resource(library, 'styles.css')


def always_needed(view, event):
    if view.request.meeting:
        ui_sortable.need()
        sortable_styles.need()
        touch_punch.need()


def includeme(config):
    config.add_subscriber(always_needed, [IBaseView, IViewInitializedEvent])
