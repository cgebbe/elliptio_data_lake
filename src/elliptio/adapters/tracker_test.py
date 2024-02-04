from elliptio.adapters.tracker import Tracker


def test_tracker():
    Tracker().get_automatic_metadata()
    # we're just checking if it runs through.
