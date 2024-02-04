from elliptio.adapters import id_creator


def test_id_creator():
    id_creator.IdCreator().create_unique_id()
