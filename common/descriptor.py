from typing import List


class Descriptor(object):
    """
    Base Descriptor, <get, set, del> method of each param is unlimited
    """

    def __new__(cls, *args, **kwargs):
        if cls is Descriptor:
            raise TypeError(f"<{cls.__name__} class> may not be instantiated")
        return super().__new__(cls)

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        elif self.name in instance.__dict__.keys():
            return instance.__dict__[self.name]
        else:
            return cls.__getattr__(instance, self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class TypeDescriptor(Descriptor):
    """
    Type Descriptor, limit param's type
    """

    def __init__(self, name, type):
        super(TypeDescriptor, self).__init__(name=name)
        self.type = type

    def __set__(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError(f"{self.name}'s type should be {self.type}")
        super().__set__(instance, value)


class TypeListDescriptor(Descriptor):
    """
    TypeList Descriptor, limit param's type
    """

    def __init__(self, name, type):
        super(TypeListDescriptor, self).__init__(name=name)
        self.type = type

    def __set__(self, instance, values: List):
        for value in values:
            if not isinstance(value, self.type):
                raise TypeError(f"{self.name}'s type should be {self.type}")
        super().__set__(instance, values)


class ValueDescriptor(Descriptor):
    """
    Value Descriptor, limit param's value
    """

    def __init__(self, name, value):
        super(ValueDescriptor, self).__init__(name=name)
        self.value = value

    def __set__(self, instance, value):
        if value not in self.value:
            raise ValueError(f"{self.name}'s value should be {self.value}")
        super().__set__(instance, value)


class IntegerLeftDescriptor(ValueDescriptor):
    """
    IntegerLeft Descriptor, limit param's value
    """

    def __set__(self, instance, value):
        if not isinstance(value, int) or value < self.value:
            raise ValueError(f"{self.name}'s value should be integer and >= {self.value}")
        instance.__dict__[self.name] = value


class IntegerLeftRealRightDescriptor(IntegerLeftDescriptor):
    """
    IntegerLeftRealRight Descriptor, limit param's value
    """

    def __set__(self, instance, value):
        if (isinstance(value, int) and value >= self.value and value <= 0) or (isinstance(value, float) and value >= 0):
            instance.__dict__[self.name] = value
        else:
            raise ValueError(f"{self.name}'s value should be integer and {self.value} <= value < 0 or "
                             f"{self.name}'s value should be real and > 0")


class TypeValueDescriptor(TypeDescriptor, ValueDescriptor):
    def __init__(self, name, value, type):
        TypeDescriptor.__init__(self, name=name, type=type)
        ValueDescriptor.__init__(self, name=name, value=value)


class TypeListValueDescriptor(TypeListDescriptor, ValueDescriptor):
    def __init__(self, name, value, type):
        TypeListDescriptor.__init__(self, name=name, type=type)
        ValueDescriptor.__init__(self, name=name, value=value)
