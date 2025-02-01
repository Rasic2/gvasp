import pytest

from gvasp.common.descriptor import Descriptor, TypeDescriptor, TypeListDescriptor


class Parameters:
    SYSTEM = TypeDescriptor('SYSTEM', str)
    LDAUL = TypeListDescriptor('LDAUL', int)


class TestDescriptor:
    def test(self):
        with pytest.raises(TypeError):
            descriptor = Descriptor(name="descriptor")


class TestTypeDescriptor:
    def test(self):
        parameters = Parameters()
        parameters.SYSTEM = "Test"

        result = Parameters.SYSTEM.__get__(None, TypeDescriptor)

        with pytest.raises(TypeError):
            parameters.SYSTEM = 1.0

        del parameters.SYSTEM


class TestTypeListDescriptor:
    def test(self):
        parameters = Parameters()

        with pytest.raises(TypeError):
            parameters.LDAUL = [1.0]


if __name__ == '__main__':
    pytest.main([__file__])
