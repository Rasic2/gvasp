import os
import re
import pandas as pd
from pandas import Series,DataFrame
from collections import defaultdict

from INCAR_module.descriptor import *
from INCAR_module.logger import *
from INCAR_module.params import PARAMS

PARAMS=DataFrame(PARAMS)

class Incar():
	"""
	API:
		self.mode           读取何种类型INCAR
		self.attrs			获取参数属性值
		self.set_(**kargs)  设置参数的值，当设定值不在PARAMS里面时，返回错误
		self.del_(*args)  	删除属性值
		self.create			根据读取、修改、删除值生成新的INCAR
	"""
	def __init__(self,mode='opt',SYSTEM=None,pot=None,nodes=None):
		self.mode=mode
		setattr(self,'SYSTEM',SYSTEM)
		if pot=='PAW_PW91':
			setattr(self,'GGA','91')
			setattr(self,'VOSKOWN',1)
		elif pot=='PAW_PBE':
			setattr(self,'GGA','PE')
		else:
			raise ValueError('Please indicate the POT!')
		if nodes==20:
			setattr(self, 'NPAR', 4)
		elif nodes==10:
			setattr(self, 'NPAR', 2)
		else:
			raise ValueError('{} is not in {}!'.format(nodes,[10,20]))
		Incar.__store(self)

	@staticmethod
	def __store(self):
		try:
			filepath=os.path.dirname('.')+'INCAR_module/lib/INCAR_{}'.format(self.mode)
			with open(filepath) as f:
				f.seek(0)
				for line in f:
					pattern=re.compile('(\w*?)\s*?=\s(.*?)\s*$')
					result=pattern.search(line)
					setattr(self,result.group(1),result.group(2)) if result else None
		except FileNotFoundError:
			logger.error('File {} not found'.format(os.path.basename(filepath)))

	def set_(self,**kargs):
		for key,value in kargs.items():
			if key in list(PARAMS['name']):
				setattr(self,key,value)
			else:
				raise ValueError('{} not exist.'.format(key))

	def U_plus(self,U,elements):
		setattr(self,'LDAU','.True.')
		setattr(self,'LDAUTYPE',2)
		setattr(self,'LDAUPRINT',2)
		LDAUL=[]
		LDAUU=[]
		LDAUJ=[]
		for element in elements:
			if element in U.keys():
				if U[element][0]=='f':
					LDAUL.append(3)
				LDAUU.append(U[element][1]+0.5)
				LDAUJ.append(0.5)
			else:
				LDAUL.append(-1)
				LDAUU.append(0)
				LDAUJ.append(0)
		i=0
		var_names=list(name for name in locals().keys() if name.startswith('LDAU'))
		for item in [LDAUL,LDAUU,LDAUJ]:
			format_item='  '.join(str(i) for i in item)
			setattr(self,'{}'.format(var_names[i]),format_item)
			i+=1
		setattr(self,'LMAXMIX',max(LDAUL)*2)

	def del_(self,*args):
		for key in args:
			try:
				delattr(self,key)
			except KeyError:
				logger.error("{} doesn't exist.".format(key))

	def create(self,path):
		PARAMS_=defaultdict(list)
		for key,value in self.__dict__.items():
			if key!='mode':
				PARAMS_['name'].append(key)
				PARAMS_['value'].append(value)
				try:
					PARAMS_['usage'].append(PARAMS.loc[PARAMS['name']==key,'usage'].values[0])
				except IndexError:
					print("PARAMS doesn't have this new param!")
		PARAMS_=DataFrame(PARAMS_)
		with open('./{}/INCAR'.format(path),'w')as f:
			for index,group in PARAMS_.groupby('usage'):
				f.write('#'*5+'/'+index[1:].title()+'/'+'#'*5+'\n')
				group=DataFrame(group)
				for i in range(len(group.index)):
					f.write('  '+group['name'].values[i]+' = '+str(group['value'].values[i])+'\n')
