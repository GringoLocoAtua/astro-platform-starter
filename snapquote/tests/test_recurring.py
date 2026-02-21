from core.recurring_detector import is_recurring


def test_recurring_keywords():
    assert is_recurring('weekly home clean')
    assert is_recurring('fortnightly office service')
    assert is_recurring('monthly schedule')


def test_recurring_no_false_positive():
    assert not is_recurring('one-off deep clean next Tuesday')
