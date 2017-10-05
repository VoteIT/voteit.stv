from BTrees.OOBTree import OOBTree
from pyramid.renderers import render
from voteit.core.models.poll_plugin import PollPlugin
from pyvotecore.stv import STV

from voteit.stv import _
from voteit.stv.schemas import SettingsSchema
from voteit.stv.schemas import STVPollSchema


class STVPoll(PollPlugin):
    name = 'stv'
    title = _(u"Single transferable vote")
    description = _("")

    def get_settings_schema(self):
        return SettingsSchema()

    def get_vote_schema(self):
        schema = STVPollSchema()
        return schema

    def format_ballots(self):
        formatted = []
        for (ballot, count) in self.context.ballots:
            formatted.append({'count':count, 'ballot':list(ballot['proposals'])})
        return formatted

    def handle_close(self):
        ballots = self.format_ballots()
        if ballots:
            winners = self.context.poll_settings.get('winners', 1)
            results = STV(ballots, required_winners = winners).as_dict()
        else:
            #No votes!
            results = {'candidates': set(self.context.proposal_uids), 'winners': ()}
        self.context.poll_result = OOBTree(results)

    def change_states_of(self):
        """ This gets called when a poll has finished.
            It returns a dictionary with proposal uid as key and new state as value.
            Like: {'<uid>':'approved', '<uid>', 'denied'}
        """
        result = {}
        winners = self.context.poll_result.get('winners', ())
        losers = self.context.poll_result['candidates'] - set(winners)
        if winners:
            for winner in winners:
                result[winner] = 'approved'
            for loser in losers:
                result[loser] = 'denied'
        return result

    def render_result(self, view):
        winner_uids = self.context.poll_result.get('winners', set())
        winners = []
        for uid in winner_uids:
            winners.append(view.resolve_uid(uid))
        looser_uids = set(self.context.poll_result['candidates']) - winner_uids
        loosers = []
        for uid in looser_uids:
            loosers.append(view.resolve_uid(uid))
        response = {}
        response['context'] = self.context
        response['winners'] = winners
        response['loosers'] = loosers
        return render('voteit.stv:templates/results.pt', response, request = view.request)


def includeme(config):
    config.registry.registerAdapter(STVPoll, name = STVPoll.name)
