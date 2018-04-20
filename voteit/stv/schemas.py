import colander
import deform
from six import string_types
from voteit.core.helpers import strip_and_truncate

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
        kw['prop_dict'] = dict([(x.uid, x) for x in proposals])
        kw['pool'] = [x.uid for x in proposals if x.uid not in cstruct]
        kw['trunc'] = strip_and_truncate
        template = readonly and self.readonly_template or self.template
        tmpl_values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **tmpl_values)

    def deserialize(self, field, pstruct):
        if pstruct is colander.null:
            return colander.null
        if isinstance(pstruct, string_types):
            return (pstruct,)
        return tuple(pstruct)


@colander.deferred
def proposals_ordering_widget(node, kw):
    context = kw['context']
    return ProposalOrderingWidget(proposals = context.get_proposal_objects())


#The schema will be populated in the stv poll plugin
class STVPollSchema(colander.Schema):
    widget = deform.widget.FormWidget(
        template = 'form_modal',
        readonly_template = 'readonly/form_modal'
    )
    proposals = colander.SchemaNode(
        colander.List(),
        widget = proposals_ordering_widget,
        title = _("Proposals"),
    )
