from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import ItemEnterEvent
from jira import Issue


class ItemEnterEventListener(EventListener):
    """ Listener that handles the click on an item """

    # pylint: disable=unused-argument,no-self-use
    def on_event(self, event: ItemEnterEvent, extension: Extension):
        """ Handles the event """
        data = event.get_data()

        if data["action"] == "go.back":
            return extension.go_back()

        if data["action"] == "issue.detail":
            issue: Issue = data["issue"]
            return extension.issue_detail(issue)

        if data["action"] == "board.open":
            return extension.open_board(data["board"])
