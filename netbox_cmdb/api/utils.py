from rest_framework.relations import RelatedField


class NameRelatedField(RelatedField):
    """Custom field allowing to display the name of the object.
    This is useful when the __str__ representation is not using the object's name."""

    def __init__(self, **kwargs):
        kwargs["read_only"] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(value.name)
