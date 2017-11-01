from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from pyramid.renderers import render
from stvpoll.exceptions import STVException
from typing import List

from voteit.core.models.poll_plugin import PollPlugin
from pyvotecore.stv import STV
from stvpoll.scottish_stv import ScottishSTV
from stvpoll.cpo_stv import CPO_STV

from voteit.stv import _
from voteit.stv.schemas import SettingsSchema
from voteit.stv.schemas import STVPollSchema


class ScottishSTVPoll(PollPlugin):
    name = 'scottish_stv'
    title = _("Scottish STV (Single Transferable Vote)")
    description = _("moderator_description_scottish_stv",
                    default="Ranked poll with single or multiple winners. "
                            "Voters rank proposals by order of preference. "
                            "Surplus or discarded votes are transferred to reduce wasted votes.")
    voter_description = _("voter_description_scottish_stv",
                          default="Rank proposals by order of preference. "
                                  "In case your proposal is excluded or get surplus votes, "
                                  "your vote will be transferred according to your list.")
    method = ScottishSTV
    template_name = 'voteit.stv:templates/result_scottish_stv.pt'

    def get_settings_schema(self):
        return SettingsSchema()

    def get_vote_schema(self):
        schema = STVPollSchema()
        return schema

    def format_ballots(self):
        # type: () -> List[dict]
        formatted = []
        for (ballot, count) in self.context.ballots:
            formatted.append({
                'count': count,
                'ballot': list(ballot['proposals'])
            })
        return formatted

    def handle_close(self):
        ballots = self.format_ballots()
        winners = self.context.poll_settings.get('winners', 1)
        method = self.method(seats=winners, candidates=self.context.proposals)
        for ballot in ballots:
            method.add_ballot(ballot['ballot'], ballot['count'])

        try:
            method.calculate()
        except STVException:
            # Should only happen on no votes! Result will be incomplete, but still returns dict.
            pass

        self.context.poll_result = OOBTree(method.result.as_dict())

    def change_states_of(self):
        """ This gets called when a poll has finished.
            It returns a dictionary with proposal uid as key and new state as value.
            Like: {'<uid>':'approved', '<uid>', 'denied'}
        """
        result = {}
        winners = set(self.context.poll_result.get('winners', ()))
        losers = set(self.context.proposals) - winners
        if winners:
            for winner in winners:
                result[winner] = 'approved'
            for loser in losers:
                result[loser] = 'denied'
        return result

    def render_result(self, view):
        winner_uids = set(self.context.poll_result.get('winners', ()))
        winners = []
        for uid in winner_uids:
            winners.append(view.resolve_uid(uid))

        loser_uids = set(self.context.proposals) - winner_uids
        losers = []
        for uid in loser_uids:
            losers.append(view.resolve_uid(uid))

        rounds = []
        for _round in self.context.poll_result.get('rounds', ()):
            round_copy = dict(_round)
            selected = []
            for proposal_uid in _round['selected']:
                selected.append(view.resolve_uid(proposal_uid))
            round_copy['selected'] = selected
            rounds.append(round_copy)

        response = {
            'context': self.context,
            'winners': winners,
            'losers': losers,
            'rounds': rounds,
        }
        return render(self.template_name, response, request=view.request)


class CPOSTVPoll(ScottishSTVPoll):
    name = 'cpo_stv'
    title = _("Comparison of Pairs of Outcomes (STV)")
    description = _("moderator_description_cpo_stv",
                    default="Ranked poll with single or multiple winners. "
                            "Voters rank proposals by order of preference. "
                            "Winners are determined by comparing all possible combination "
                            "of winners to find the combination with highest approval.")
    voter_description = _("voter_description_cpo_stv",
                          default="Rank proposals by order of preference. "
                                  "Winners are determined by comparing all possible combination "
                                  "of winners to find the combination with highest approval.")
    method = CPO_STV
    template_name = 'voteit.stv:templates/result_cpo_stv.pt'


def includeme(config):
    config.registry.registerAdapter(ScottishSTVPoll, name=ScottishSTVPoll.name)
    # CPO needs more testing, and should probable not be used in most cases. disabled for now.
    # config.registry.registerAdapter(CPOSTVPoll, name=CPOSTVPoll.name)
