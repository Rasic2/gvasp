class Descriptor(object):

    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

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

    def __set__(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError(f"{self.name}'s type should be {self.type}")
        super().__set__(instance, value)


class ValueDescriptor(Descriptor):

    def __set__(self, instance, value):
        if value not in self.value:
            raise ValueError(f"{self.name}'s value should be {self.value}")
        super().__set__(instance, value)


class ParamDescriptor(TypeDescriptor, ValueDescriptor):
    pass
