"""实例属性赋值必须满足type匹配和value匹配"""
class Descriptor:
	"""
	描述符基类
	"""
	def __init__(self,name,type_,values):
		self.name=name

	def __get__(self,instance,cls):
		if instance is None:
			return self
		elif self.name in instance.__dict__.keys():
			return instance.__dict__[self.name]
		else:
			return cls.__getattr__(instance,self.name)

	def __set__(self,instance,value):
		instance.__dict__[self.name]=value

	def __delete__(self,instance):
		del instance.__dict__[self.name]

class Type_descriptor(Descriptor):
	"""
	类型描述符
	"""
	def __init__(self,name,type_,values):
		self.type_=type_

	def __set__(self,instance,value):
		if not isinstance(value,self.type_):
			raise TypeError("{0}'s type should be {1}.".format(self.name,self.type_))
		super().__set__(instance,value)

class Value_descriptor(Descriptor):
	"""
	值描述符
	"""
	def __init__(self,name,type_,values):
		self.values=values

	def __set__(self,instance,value):
		print(value,self.values)
		if value not in self.values:
			raise ValueError("{0}'s value should be {1}.".format(self.name,self.values))
		super().__set__(instance,value)

class Params_descriptor(Type_descriptor,Value_descriptor):
	"""
	类型+值描述符
	"""
	def __init__(self,name,type_,values):
		self.name=name
		self.type_=type_
		self.values=values
