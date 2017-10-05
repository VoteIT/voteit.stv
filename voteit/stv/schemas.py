import colander
import deform
from six import string_types

from voteit.stv import _


class SettingsSchema(colander.Schema):
    """ Settings for a STV poll
    """
    winners = colander.SchemaNode(
        colander.Int(),
        title = _(u"Winners"),
        description = _(u"stv_config_winners_description",
                      default=u"Numbers of possible winners in the poll"),
        default=1,
    )


class ProposalOrderingWidget(deform.widget.Widget):
    template = 'sorting'
    readonly_template = 'sorting' #FIXME
    proposals = {}

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ()
        readonly = kw.get('readonly', self.readonly)
        proposals = kw.get('proposals', self.proposals)
        kw['prop_dict'] = prop_dict = self.as_dict(proposals)
        kw['pool'] = set(prop_dict.keys()) - set(cstruct)
        template = readonly and self.readonly_template or self.template
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        if isinstance(pstruct, string_types):
            return (pstruct,)
        return tuple(pstruct)

    def as_dict(self, proposals):
        return dict([(x.uid, x) for x in proposals])


@colander.deferred
def proposals_ordering_widget(node, kw):
    context = kw['context']
    return ProposalOrderingWidget(proposals = context.get_proposal_objects())


@colander.deferred
def all_must_be_picked_validator(node, kw):
    context = kw['context']
    return ContainsExactly([x.uid for x in context.get_proposal_objects()])


class ContainsExactly(object):
    """ Input must contain exactly all of the values passed as initial choices.
        The order is irrelevant though.
    """

    def __init__(self, choices):
        self.choices = choices

    def __call__(self, node, value):
        if set(value) != set(self.choices):
            msg = ("You must sort all of the proposals.")
            raise colander.Invalid(node, msg)


#The schema will be populated in the stv poll plugin
class STVPollSchema(colander.Schema):
    widget = deform.widget.FormWidget(
        template = 'form_modal',
        readonly_template = 'readonly/form_modal'
    )
    proposals = colander.SchemaNode(
        colander.List(),
        widget = proposals_ordering_widget,
        #validator = all_must_be_picked_validator,
    )
