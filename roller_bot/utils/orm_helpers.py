import operator

from sqlalchemy.orm.collections import MappedCollection, collection


def attributed_mapped_keyed_list_collection(attribute_name):
    return lambda: KeyedListCollection(attribute_name)


class KeyedListCollection(MappedCollection):
    """This transforms a collection of attribute values into a dict of lists.

    This is useful when representing an EAV table, for instance, because
    any given attribute can have multiple values, but it is typically
    most useful to access them by attribute name.
    """
    def __init__(self, key):
        super(KeyedListCollection, self).__init__(operator.attrgetter(key))

    # @collection.internally_instrumented
    # def __setitem__(self, key, value, _sa_initiator=None):
    #     print("!!!!!! THIS IS TEST !!!!!!!")
    #     if not super(KeyedListCollection, self).get(key):
    #         super(KeyedListCollection, self).__setitem__(key, [], _sa_initiator)
    #     super(KeyedListCollection, self).__getitem__(key).append(value)
    @collection.appender
    @collection.internally_instrumented
    def set(self, value, _sa_initiator=None) -> None:
        print("!!!!!! THIS IS TEST !!!!!!!")
        if not super(KeyedListCollection, self).get(value):
            super(KeyedListCollection, self).__setitem__(value, [], _sa_initiator)
        super(KeyedListCollection, self).__getitem__(value).append(value)
