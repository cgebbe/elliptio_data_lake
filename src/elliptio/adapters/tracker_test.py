from elliptio.adapters.tracker import Tracker


def test_tracker():
    # we're just checking if it runs through.
    Tracker().get_automatic_metadata()
