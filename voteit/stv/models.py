# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from BTrees.OOBTree import OOBTree
from pyramid.httpexceptions import HTTPForbidden
from pyramid.renderers import render
from stvpoll import STVPollBase
from stvpoll.cpo_stv import CPO_STV
from stvpoll.exceptions import STVException
from stvpoll.scottish_stv import ScottishSTV
from voteit.core.models import poll_plugin

from voteit.stv import _
from voteit.stv.schemas import STVPollSchema
from voteit.stv.schemas import SettingsSchema


class BaseSTVPoll(poll_plugin.PollPlugin):
    template_name = None
    method = STVPollBase
    multiple_winners = True
    proposals_min = 3

    def get_settings_schema(self):
        return SettingsSchema()

    def get_vote_schema(self):
        return STVPollSchema()

    def format_ballots(self):
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
        random_tiebreak = self.context.poll_settings.get('random_in_tiebreaks', True)
        method = self.method(
            seats=winners,
            candidates=self.context.proposals,
            random_in_tiebreaks=random_tiebreak,
        )
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
        winners = self.context.poll_result.get('winners', ())
        losers = set(self.context.proposals).difference(winners)
        if winners:
            for winner in winners:
                result[winner] = 'approved'
            for loser in losers:
                result[loser] = 'denied'
        return result

    def render_result(self, view):
        winner_uids = self.context.poll_result.get('winners', ())
        winners = []
        for uid in winner_uids:
            winners.append(view.resolve_uid(uid))

        loser_uids = set(self.context.proposals).difference(winner_uids)
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


class ScottishSTVPoll(BaseSTVPoll):
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

    multiple_winners = True
    priority = 3
    recommended_for = _("Board elections with a proportional result or proportionally selecting proposals.")

    criteria = (
        poll_plugin.MajorityWinner(
            False,
            comment=_("Incompatible with proportional.")
        ),
        poll_plugin.CondorcetWinner(
            False,
            comment=_("Incompatible with proportional.")
        ),
        poll_plugin.Proportional(True),
    )

    def handle_start(self, request):
        if len(self.context.proposals) < 3:
            raise HTTPForbidden(_("This is only usable for 3 or more proposals"))
        winners = self.context.poll_settings.get('winners', None)
        if winners is None:
            raise HTTPForbidden(_("No winners?"))
        if len(self.context.proposals) == winners:
            raise HTTPForbidden(_("Same amount of winners as proposals. This method can't be used for sorting."))


class CPOSTVPoll(BaseSTVPoll):
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

    multiple_winners = True
    priority = 3
    possible_combinations_cap = 1000

    @classmethod
    def check_applicable(cls, proposals, winners=1, random_tiebreaks=True):
        # type: (int, int, bool) -> bool
        # 1000 possible combinations means almost ½ million comparisons.
        # Calculating number of comparisons is possible, but a waste of time.
        return winners > 1 and CPO_STV.possible_combinations(proposals, winners) < cls.possible_combinations_cap


def includeme(config):
    config.registry.registerAdapter(ScottishSTVPoll, name=ScottishSTVPoll.name)
    # CPO needs more testing, and should probable not be used in most cases. disabled for now.
    # config.registry.registerAdapter(CPOSTVPoll, name=CPOSTVPoll.name)
