""" Fanstatic lib"""
from arche.interfaces import IBaseView
from arche.interfaces import IViewInitializedEvent
from fanstatic import Library
from fanstatic import Resource

from js.jqueryui import ui_sortable

library = Library('voteit_stv', 'static')
sortable_styles = Resource(library, 'styles.css')

def always_needed(view, event):
    ui_sortable.need()
    sortable_styles.need()

def includeme(config):
    config.add_subscriber(always_needed, [IBaseView, IViewInitializedEvent])
