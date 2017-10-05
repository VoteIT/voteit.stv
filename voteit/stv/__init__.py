from pyramid.i18n import TranslationStringFactory
from pyramid_deform import configure_zpt_renderer

_ = TranslationStringFactory('voteit.stv')


def includeme(config):
    config.include('.models')
    config.include('.fanstatic_lib')
    config.add_translation_dirs('voteit.stv:locale/')
    configure_zpt_renderer(['voteit.stv:templates/deform'])
