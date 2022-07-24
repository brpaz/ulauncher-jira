""" Main Module """

import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.item.ResultItem import ResultItem
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from extension.listeners.query import KeywordQueryEventListener
from extension.listeners.item_enter import ItemEnterEventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.event import PreferencesEvent, PreferencesUpdateEvent
from extension.listeners.preferences import PreferencesEventListener, PreferencesUpdateEventListener
from typing import List
from jira import JIRA, Issue
from .utils.filters import Filters

logger = logging.getLogger(__name__)


class JiraExtension(Extension):
    """ Main Extension Class  """

    jira_client: JIRA

    current_items: List[ResultItem]

    def __init__(self):
        """ Initializes the extension """
        super(JiraExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.jira_client = None
        self.extension_id = 'com.github.brpaz.ulauncher-jira'
        self.icon = 'images/icon.png'

        self.filters = Filters(self.extension_id)

        self.current_items = []

    def go_back(self):
        return RenderResultListAction(self.current_items)

    def show_no_results_message(self, query):
        return RenderResultListAction([
            ExtensionResultItem(icon=self.icon,
                                name='No results found matching your criteria',
                                highlightable=False,
                                on_enter=HideWindowAction())
        ])

    def search_issues(self, event: KeywordQueryEvent):
        query = event.get_argument() or ""
        if len(query) < 3:
            return RenderResultListAction([
                ExtensionResultItem(icon=self.icon,
                                    name='Keep typing to search ...',
                                    description='Searching Jira issues',
                                    highlightable=False,
                                    on_enter=DoNothingAction())
            ])

        jql = 'summary ~ "{}" ORDER BY created DESC'.format(query)

        return self._search_with_jql(event, jql)

    def assigned_issues(self, event: KeywordQueryEvent):

        query = event.get_argument() or ""

        jql = 'assignee = currentUser() and statusCategory != Done'

        if len(query) > 2:
            jql = jql + 'AND summary ~ "{}"'.format(query)

        jql = jql + ' order by priority DESC,updated DESC'
        return self._search_with_jql(event, jql)

    def reported_issues(self, event: KeywordQueryEvent):

        query = event.get_argument() or ""

        jql = 'reporter = currentUser() and statusCategory != Done'

        if len(query) > 2:
            jql = jql + 'AND summary ~ "{}"'.format(query)

        jql = jql + ' order by priority DESC,updated DESC'
        return self._search_with_jql(event, jql)

    def _search_with_jql(self, event: KeywordQueryEvent, jql: str):

        issues = self.jira_client.search_issues(jql_str=jql, maxResults=10)

        if len(issues) == 0:
            return self.show_no_results_message(event.get_argument())

        items = []

        for issue in issues:
            issue_url = self.get_jira_issue_url(issue)
            items.append(
                ExtensionResultItem(
                    icon=self.icon,
                    name='{}: {}'.format(issue.key, issue.fields.summary),
                    description="Type: {} | Status: {} | Assignee: {}".format(
                        issue.fields.issuetype, issue.fields.status,
                        issue.fields.assignee),
                    on_alt_enter=OpenUrlAction(issue_url),
                    on_enter=ExtensionCustomAction(
                        {
                            "action": "issue.detail",
                            "issue": issue,
                        },
                        keep_app_open=True),
                ))

        self.current_items = items
        return RenderResultListAction(items)

    def issue_detail(self, issue: Issue):
        """ Displays an issue detail"""
        issue_url = self.get_jira_issue_url(issue)

        return RenderResultListAction([
            ExtensionResultItem(icon='images/icon-summary.png',
                                description="Title",
                                name=issue.fields.summary,
                                highlightable=False,
                                on_enter=CopyToClipboardAction(
                                    issue.fields.summary)),
            ExtensionResultItem(icon='images/icon-id.png',
                                description="Key",
                                name=issue.key,
                                highlightable=False,
                                on_enter=CopyToClipboardAction(issue.key)),
            ExtensionResultItem(icon=self.icon,
                                description="Type",
                                name=str(issue.fields.issuetype),
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon=self.icon,
                                description="Status",
                                name=str(issue.fields.status),
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon=self.icon,
                                description="Priority",
                                name=str(issue.fields.priority),
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon='images/icon-assignee.png',
                                description="Assignee",
                                name=str(issue.fields.assignee),
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon='images/icon-assignee.png',
                                description="Reporter",
                                name=str(issue.fields.reporter),
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon='images/icon-date.png',
                                description="Created At",
                                name=issue.fields.created,
                                highlightable=False,
                                on_enter=DoNothingAction()),
            ExtensionResultItem(icon='images/icon-url.png',
                                description="URL",
                                name=issue_url,
                                highlightable=False,
                                on_enter=OpenUrlAction(issue_url)),
            ExtensionResultItem(
                icon='images/icon-back.png',
                name="Go back",
                description="Back to list",
                on_enter=ExtensionCustomAction({
                    "action": "go.back",
                },
                                               keep_app_open=True),
            )
        ])

    def custom_filters(self, event: KeywordQueryEvent):

        query = event.get_argument()

        filters_list = self.filters.load()

        # Empty query: We want to list all the custom filters available.
        if query is None:
            return self.list_custom_filters(filters_list, event.get_keyword(),
                                            "")

        # If the query is not empty, we split it by space,
        # so we can see if we are filtering the list on filters
        # or accessing a specific filter.
        # If the first part matches a id of an existing filter, it means that we use use that filter as base.

        query_parts = query.split(" ")

        filter_id = query_parts[0]
        filter_term = " ".join(query_parts[0:])

        filter_item = None
        for item in filters_list:
            if item["id"] == filter_id:
                filter_item = item
                break

        if filter_item is None:
            return self.list_custom_filters(filters_list, event.get_keyword(),
                                            filter_term)

        filter_term = " ".join(query_parts[1:])

        if len(filter_term) > 2:
            jql = 'summary ~ "{}" AND {}'.format(filter_term,
                                                 filter_item["jql"])
        else:
            jql = filter_item["jql"]

        return self._search_with_jql(event, jql)

    def list_custom_filters(self, filters_data: List[dict], keyword: str,
                            query: str):

        custom_filters = filters_data

        if query is not None:
            custom_filters = [
                x for x in filters_data if query.lower() in x["title"].lower()
            ]

        if len(custom_filters) == 0:
            return self.show_no_results_message(query)

        items = []
        for custom_filter in custom_filters:
            items.append(
                ExtensionResultItem(icon=self.icon,
                                    name=custom_filter["title"],
                                    description=custom_filter["jql"],
                                    on_enter=SetUserQueryAction(
                                        "{} {} ".format(
                                            keyword, custom_filter["id"]))))

        return RenderResultListAction(items)

    def list_boards(self, event: KeywordQueryEvent):
        query = event.get_argument() or ""
        boards = self.jira_client.boards(name=query, maxResults=10)
        self.jira_client.sprints_by_name
        if len(boards) == 0:
            return self.show_no_results_message(query)

        items = []

        for board in boards:
            items.append(
                ExtensionResultItem(
                    icon=self.icon,
                    name=board.name,
                    on_enter=ExtensionCustomAction({
                        "action": "board.open",
                        "board": board,
                    }),
                ))

        self.current_items = items
        return RenderResultListAction(items)

    def current_sprint(self, event: KeywordQueryEvent):
        query = event.get_argument() or ""
        board_id = self.preferences["board_id"]

        if board_id == "":
            return RenderResultListAction([
                ExtensionResultItem(
                    icon=self.icon,
                    name='Board ID not configured',
                    description='define "board_id" on extension settings',
                    highlightable=False,
                    on_enter=HideWindowAction())
            ])

        sprints = self.jira_client.sprints(board_id=board_id, state="active")

        if len(sprints) == 0:
            return self.show_no_results_message(query)

        if query:
            jql = 'Sprint = {} AND summary ~ "{}*" ORDER BY priority DESC'.format(
                sprints[0].id, query)
        else:
            jql = 'Sprint = {} ORDER BY priority DESC'.format(sprints[0].id)

        return self._search_with_jql(event, jql)

    def open_board(self, board):
        board_data = board.raw
        project_key = board_data["location"]["projectKey"]
        project_type = board_data["location"]["projectTypeKey"]

        board_url = "{}/jira/{}/c/projects/{}/boards/{}".format(
            self.preferences["server_url"], project_type, project_key,
            board.id)

        return OpenUrlAction(board_url).run()

    def open_issue(self, event: KeywordQueryEvent):
        issue_key = event.get_argument()

        issue_url = "{}/browse/{}".format(self.preferences["server_url"],
                                          issue_key)
        return RenderResultListAction([
            ExtensionResultItem(
                icon=self.icon,
                name='Press enter to open issue: {}'.format(issue_key),
                highlightable=False,
                on_enter=OpenUrlAction(issue_url))
        ])

    def create_jira_client(self, server_url: str, username: str,
                           access_token: str):
        self.jira_client = JIRA(server=server_url,
                                basic_auth=(username, access_token))

    def get_jira_issue_url(self, issue: Issue):
        return "{}/browse/{}".format(self.preferences["server_url"], issue.key)
