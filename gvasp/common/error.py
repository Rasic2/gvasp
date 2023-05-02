class AttributeNotRegisteredError(AttributeError):
    pass


class AttributeNotAssignedError(AttributeError):
    pass


class AnimationError(RuntimeError):
    pass


class ArgsNotRegisteredError(TypeError):
    pass


class ConstrainError(TypeError):
    pass


class FrequencyError(IndexError):
    pass


class GridNotEqualError(ValueError):
    pass


class JsonFileNotFoundError(FileNotFoundError):
    pass


class ParameterError(TypeError):
    pass


class PathNotExistError(TypeError):
    pass


class PotDirNotExistError(FileExistsError):
    pass


class StructureNotEqualError(ValueError):
    pass


class StructureOverlapError(ValueError):
    pass


class TooManyXSDFileError(FileExistsError):
    pass


class XSDFileNotFoundError(FileNotFoundError):
    pass
