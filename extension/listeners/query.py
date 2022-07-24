import logging

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent

logger = logging.getLogger(__name__)

KEYWORD_SEARCH = "kw_issues_search"
KEYWORD_ASSIGNED_ISSUES = "kw_issues_assigned"
KEYWORD_REPORTED_ISSUES = "kw_issues_reported"
KEYWORD_CUSTOM_FILTERS = "kw_custom_filter"
KEYWORD_BOARDS = "kw_boards"
KEYWORD_OPEN = "kw_open_issue"
KEYWORD_CURRENT_SPRINT = "kw_current_sprint"


class KeywordQueryEventListener(EventListener):
    """ Listener that handles the user input """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event: KeywordQueryEvent, extension: Extension):
        """ Handles the event """

        kw_id = self.get_keyword_id(extension.preferences, event.get_keyword())

        if kw_id == KEYWORD_SEARCH:
            return extension.search_issues(event)

        if kw_id == KEYWORD_ASSIGNED_ISSUES:
            return extension.assigned_issues(event)

        if kw_id == KEYWORD_REPORTED_ISSUES:
            return extension.reported_issues(event)

        if kw_id == KEYWORD_CUSTOM_FILTERS:
            return extension.custom_filters(event)

        if kw_id == KEYWORD_BOARDS:
            return extension.list_boards(event)

        if kw_id == KEYWORD_OPEN:
            return extension.open_issue(event)

        if kw_id == KEYWORD_CURRENT_SPRINT:
            return extension.current_sprint(event)

    def get_keyword_id(self, preferences: dict, keyword: str):
        """ Returns the keyword id, that matches the keyword name passed as argument """
        kw_id = None
        for key, value in preferences.items():
            if value == keyword:
                kw_id = key
                break

        return kw_id
