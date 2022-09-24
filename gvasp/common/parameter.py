from gvasp.common.descriptor import TypeDescriptor, ValueDescriptor, IntegerLeftDescriptor, TypeListDescriptor, \
    IntegerLeftRealRightDescriptor


def logic(value: str):
    """transform str to bool"""
    if value.upper() == ".FALSE.":
        return False
    elif value.upper() == ".TRUE.":
        return True
    else:
        raise ValueError(f"{value} can't transform to <class bool>")


def bool_str(value):
    """transform str to (bool, str)"""
    if value.upper() == ".FALSE.":
        return False
    elif value.upper() == ".TRUE.":
        return True
    else:
        return value


def int_float(value):
    """transform str to int (value<0) or float (value>0)"""
    return float(value) if float(value) > 0 else int(float(value))


def list_int(values):
    """transform str to List[int]"""
    return list(map(int, values.split()))


def list_float(values):
    """transform str to List[float]"""
    return list(map(float, values.split()))


class Parameter(object):
    """
    Parameters manager, register parameter && check theirs type
    """
    SYSTEM = TypeDescriptor('SYSTEM', str)
    PREC = ValueDescriptor('PREC', ['Low', 'Medium', 'High', 'Normal', 'Single', 'Accurate'])
    ISTART = ValueDescriptor("ISTART", [0, 1, 2, 3])
    IBRION = ValueDescriptor("IBRION", [-1, 0, 1, 2, 3, 5, 6, 7, 8, 44])
    NSW = TypeDescriptor("NSW", int)
    ISIF = ValueDescriptor("ISIF", [0, 1, 2, 3, 4, 5, 6, 7])
    ENCUT = TypeDescriptor("ENCUT", float)
    NELM = TypeDescriptor("NELM", int)
    NELMIN = TypeDescriptor("NELMIN", int)
    EDIFF = TypeDescriptor("EDIFF", float)
    EDIFFG = TypeDescriptor("EDIFFG", float)
    GGA = ValueDescriptor("GGA", ['CA', 'PZ', 'VW', 'HL', 'WI', 'LIBXC', 'LI', '91', 'PE', 'RE', 'RP', 'PS', 'AM', 'B3',
                                  'B5', 'BF', 'OR', 'BO', 'MK', 'ML', 'CX'])
    ISPIN = ValueDescriptor("ISPIN", [1, 2])
    LWAVE = TypeDescriptor('LWAVE', bool)
    LCHARG = TypeDescriptor('LCHARG', bool)
    LREAL = ValueDescriptor("LREAL", [False, 'Auto', 'A', 'On', 'O', True])
    ALGO = ValueDescriptor("ALGO", ['Normal', 'VeryFast', 'Fast', 'Conjugate', 'All', 'Damped', 'Subrot', 'Eigenval',
                                    'Exact', 'None', 'Nothing', 'CHI', 'G0W0', 'GW0', 'GW', 'scGW0', 'scGW', 'G0W0R',
                                    'GW0R', 'GWR', 'scGW0R', 'scGWR', 'ACFDT', 'RPA', 'ACFDTR', 'RPAR', 'BSE', 'TDHF'])
    ISMEAR = IntegerLeftDescriptor("ISMEAR", -5)
    SIGMA = TypeDescriptor('SIGMA', float)
    AMIX = TypeDescriptor('AMIX', float)
    BMIX = TypeDescriptor('BMIX', float)
    AMIX_MAG = TypeDescriptor('AMIX_MAG', float)
    BMIX_MAG = TypeDescriptor('BMIX_MAG', float)
    LDAU = TypeDescriptor('LDAU', bool)
    LDAUTYPE = ValueDescriptor("LDAUTYPE", [1, 2, 4])
    LDAUL = TypeListDescriptor('LDAUL', int)
    LDAUU = TypeListDescriptor('LDAUU', float)
    LDAUJ = TypeListDescriptor('LDAUJ', float)
    LDAUPRINT = ValueDescriptor("LDAUPRINT", [0, 1, 2])
    LMAXMIX = TypeDescriptor("LMAXMIX", int)
    NPAR = TypeDescriptor("NPAR", int)
    LAECHG = TypeDescriptor("LAECHG", bool)
    POTIM = TypeDescriptor("POTIM", float)
    ISYM = ValueDescriptor("ISYM", [-1, 0, 1, 2, 3])
    ICHAIN = ValueDescriptor("ICHAIN", [0, 1, 2, 3])
    DdR = TypeDescriptor("DdR", float)
    DRotMax = TypeDescriptor("DRotMax", int)
    DFNMin = TypeDescriptor('DFNMin', float)
    DFNMax = TypeDescriptor('DFNMax', float)
    IOPT = ValueDescriptor('IOPT', [0, 1, 2, 3, 4, 7])
    ICHARG = ValueDescriptor('ICHARG', [0, 1, 2, 4, 11, 12])
    LORBIT = ValueDescriptor("LORBIT", [0, 1, 2, 5, 10, 11, 12, 13, 14])
    NEDOS = TypeDescriptor('NEDOS', int)
    NFREE = TypeDescriptor('NFREE', int)
    SMASS = IntegerLeftRealRightDescriptor("SMASS", -3)
    MDALGO = ValueDescriptor('MDALGO', [0, 1, 2, 3, 11, 21, 13])
    TEBEG = TypeDescriptor('TEBEG', float)
    TEEND = TypeDescriptor('TEEND', float)
    SPRING = TypeDescriptor('SPRING', float)
    LCLIMB = TypeDescriptor('LCLIMB', bool)
    MAXMOVE = TypeDescriptor('MAXMOVE', float)
    IMAGES = TypeDescriptor('IMAGES', int)
    LPARD = TypeDescriptor('LPARD', bool)
    NBMOD = TypeDescriptor('NBMOD', int)
    EINT = TypeDescriptor('EINT', float)
    LSEPB = TypeDescriptor('LSEPB', bool)
    LSEPK = TypeDescriptor('LSEPK', bool)
    IVDW = ValueDescriptor("IVDW", [0, 1, 10, 11, 12, 2, 20, 21, 202, 4])

    _type_trans = {"_strParam":
                       {'func': str,
                        'name': ['SYSTEM', 'PREC', 'GGA', 'ALGO'],
                        },
                   "_intParam":
                       {'func': int,
                        'name': ['ISTART', 'IBRION', 'NSW', 'ISIF', 'NELM', 'NELMIN', 'ISPIN', 'ISMEAR', 'LDAUTYPE',
                                 'LDAUPRINT', 'LMAXMIX', 'NPAR', 'ISYM', 'ICHAIN', 'DRotMax', 'IOPT', 'ICHARG',
                                 'LORBIT', 'NEDOS', 'NFREE', 'MDALGO', 'IMAGES', 'NBMOD', "IVDW"]
                        },
                   "_floatParam":
                       {'func': float,
                        'name': ['ENCUT', 'EDIFF', 'EDIFFG', 'SIGMA', 'AMIX', 'BMIX', 'AMIX_MAG', 'BMIX_MAG', 'POTIM',
                                 'DdR', 'DFNMin', 'DFNMax', 'TEBEG', 'TEEND', 'SPRING', 'MAXMOVE', 'EINT'],
                        },
                   "_bool_Param":
                       {'func': logic,
                        'name': ['LWAVE', 'LCHARG', 'LDAU', 'LAECHG', 'LCLIMB', 'LPARD', 'LSEPB', 'LSEPK'],
                        },
                   "_bool_str_Param":
                       {'func': bool_str,
                        'name': ['LREAL'],
                        },
                   "_int_float_Param":
                       {'func': int_float,
                        'name': ['SMASS'],
                        },
                   "_list_int_Param":
                       {'func': list_int,
                        'name': ['LDAUL'],
                        },
                   "_list_float_Param":
                       {'func': list_float,
                        'name': ['LDAUU', 'LDAUJ'],
                        }
                   }

    _baseParam = ('SYSTEM', 'PREC', 'ISTART', 'ISYM', 'ENCUT', 'NELM', 'NELMIN', 'EDIFF', 'EDIFFG', 'GGA', 'ISPIN',
                  'LWAVE', 'NPAR',)

    _scfParam = ('AMIX', 'BMIX', 'AMIX_MAG', 'BMIX_MAG')

    _optParam = ('IBRION', 'NSW', 'POTIM', 'ISIF',)

    _mdParam = ('SMASS', 'MDALGO', 'TEBEG', 'TEEND')

    _chgParam = ('LAECHG', 'LCHARG', 'LREAL', 'ALGO', 'ISMEAR', 'SIGMA',)

    _dosParam = ('ICHARG', 'LORBIT', 'NEDOS')

    _freqParam = ('NFREE',)

    _stmParam = ('LPARD', 'NBMOD', 'EINT', 'LSEPB', 'LSEPK')

    _vtstParam = ('ICHAIN', 'IOPT',)

    _nebParam = ('SPRING', 'LCLIMB', 'MAXMOVE', 'IMAGES')

    _dimerParam = ('DdR', 'DRotMax', 'DFNMin', 'DFNMax')

    _plusUParam = ('LDAU', 'LDAUTYPE', 'LDAUL', 'LDAUU', 'LDAUJ', 'LDAUPRINT', 'LMAXMIX')

    _vdwParam = ('IVDW',)
