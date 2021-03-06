from gcalcli import gcalcli
from gcalcli.gcalcli import GoogleCalendarInterface
from gcalcli.gcalcli import CLR
from apiclient.discovery import HttpMock, build
import pytest
import os
from json import load

TEST_DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + '/data'


def mocked_calendar_service(self):
    http = HttpMock(
            TEST_DATA_DIR + '/cal_service_discovery.json', {'status': '200'})
    if not self.calService:
        self.calService = build(
                serviceName='calendar', version='v3', http=http)
    return self.calService


def mocked_calendar_list(self):
    http = HttpMock(
            TEST_DATA_DIR + '/cal_list.json', {'status': '200'})
    request = self._CalService().calendarList().list()
    cal_list = request.execute(http=http)
    self.allCals = [cal for cal in cal_list['items']]
    if not self.calService:
        self.calService = build(
                serviceName='calendar', version='v3', http=http)
    return self.calService


@pytest.fixture
def gcal(monkeypatch):
    monkeypatch.setattr(
            GoogleCalendarInterface, '_CalService', mocked_calendar_service)
    monkeypatch.setattr(
            GoogleCalendarInterface, '_GetCached', mocked_calendar_list)
    return GoogleCalendarInterface(cache=False)


# TODO: These are more like placeholders for proper unit tests
#       We just try the commands and make sure no errors occur.
def test_list(gcal, capsys):
    with open(TEST_DATA_DIR + '/cal_list.json') as cl:
        cal_count = len(load(cl)['items'])

    # test data has 6 cals
    assert cal_count == len(gcal.allCals)

    # color state is being stored in the colors class.
    # ugh, is this java?!
    CLR.useColor = False
    expected_header = ''' Access  Title\n'''

    gcal.ListAllCalendars()
    captured = capsys.readouterr()
    assert captured.out.startswith(expected_header)

    # +3 cos one for the header, one for the '----' decorations,
    # and one for the eom
    assert len(captured.out.split('\n')) == cal_count + 3


def test_agenda(gcal):
    gcal.AgendaQuery()


def test_cal_query(gcal):
    gcal.AgendaQuery('calw')
    gcal.AgendaQuery('calm')


def test_ValidColor():
    with pytest.raises(Exception):
        gcalcli.ValidColor('not a valid color')
