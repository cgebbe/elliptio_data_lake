import uuid

from elliptio.interfaces import ID, IdCreatorInterface


class IdCreator(IdCreatorInterface):
    def create_unique_id(self, prefix: str = "") -> ID:
        id_ = uuid.uuid4()
        if not prefix:
            return ID(id_)
        return ID(f"{prefix}_{id_}")
