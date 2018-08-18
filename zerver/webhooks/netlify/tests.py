# -*- coding: utf-8 -*-
from django.conf import settings

from zerver.lib.test_classes import WebhookTestCase
from zerver.models import get_system_bot

class NetlifyHookTests(WebhookTestCase):
    STREAM_NAME = 'netlify'
    URL_TEMPLATE = u"/api/v1/external/netlify?stream={stream}&api_key={api_key}"

    def test_building_message(self) -> None:
        expected_subject = u"objective-jepsen-35fbb2"
        expected_message = (
            u'State: building\n'
            u'Name: objective-jepsen-35fbb2\n'
            u'Branch: master'
        )

        self.send_and_test_stream_message('building', expected_subject, expected_message,
                                          content_type="application/json")

    def test_created_message(self) -> None:
        expected_subject = u"objective-jepsen-35fbb2"
        expected_message = (
            u'State: ready\n'
            u'Name: objective-jepsen-35fbb2\n'
            u'Branch: master'
        )

        self.send_and_test_stream_message('created', expected_subject, expected_message,
                                          content_type="application/json")

    def get_body(self, fixture_name: str) -> str:
        return self.webhook_fixture_data("netlify", fixture_name, file_type="json")
