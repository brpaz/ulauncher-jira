import logging

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import PreferencesEvent, PreferencesUpdateEvent

logger = logging.getLogger(__name__)


class PreferencesEventListener(EventListener):
    """ Handles preferences initialization event """

    def on_event(self, event: PreferencesEvent, extension: Extension):
        """ Handle event """
        extension.create_jira_client(event.preferences["server_url"],
                                     event.preferences["email"],
                                     event.preferences["access_token"])


class PreferencesUpdateEventListener(EventListener):
    """ Handles Preferences Update event """

    def on_event(self, event: PreferencesUpdateEvent, extension: Extension):
        if event.id == "email":
            extension.create_jira_client(extension.preferences["server_url"],
                                         event.new_value,
                                         extension.preferences["access_token"])

        if event.id == "access_token":
            extension.create_jira_client(
                extension.preferences["server_url"],
                extension.preferences["email"],
                event.new_value,
            )

        if event.id == "server_url":
            extension.create_jira_client(
                event.new_value,
                extension.preferences["email"],
                extension.preferences["access_token"],
            )
