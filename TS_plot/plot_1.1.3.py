#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by hui_zhou@mail.ecust.edu.cn
#modified at 2019/04/19
#modified at 2019/06/03 增加CO3绘制过程
# <--Version:1.1.3-->
import math
from matplotlib import pyplot as plt
from functools import wraps
from collections import defaultdict,deque

def plot_wrap(func):
	"""图像类的装饰器，增加字体，字号功能"""
	@wraps(func)
	def wrapper(self,*args,**kargs):
		plt.rc('font',family='Times New Roman') #配置全局字体
		plt.rcParams['mathtext.default']='regular' #配置数学公式字体
		func(self,*args,**kargs)
		plt.title(self.title,fontsize=18)
		plt.xticks([])
		plt.yticks(fontsize=14)
		#plt.ylim((-1.6,0.5))
		plt.xlabel(self.xlabel,fontsize=16)
		plt.ylabel(self.ylabel,fontsize=16)
		#plt.legend(loc='best')
	return wrapper

class Figure():
	"""图像类，为图像增加实线对象、虚线对象"""
	@plot_wrap
	def __init__(self,xticks='',title='',xlabel='Reaction coordinate',ylabel='Energy(eV)',width=9,height=4.5):
		self.fig=plt.figure(figsize=(width,height))
		self.ax=self.fig.add_subplot(1,1,1)
		self.colors=['#000000','#110141','#01545a','#710162','#ed0345','#017351','#03c383','#aad962','#fbbf45','#ef6932','#a12a5e']
		self.title=title
		#self.count=count
		self.xticks=xticks
		self.xlabel=xlabel
		self.ylabel=ylabel
		self.texts=defaultdict(list)

	def add_solid(self,x,y,color):
		SolidLine(x=x,y=y,color=color)

	def add_dash(self,x,y,color):
		DashLine(x=x,y=y,color=color)

	def add_text(self,x,y,text,color):
		self.texts[color].append(Text(x,y,text,color))

class Data():
	"""将每一条路径数据转换为实线和虚线坐标"""
	def __init__(self,data):
		self.data=data
		self.solid_x,self.solid_y,self.dash_x,self.dash_y=self.__convert()

	def __convert(self):
		solid_x=[[0.75+2*i,1.25+2*i] for i in range(len(self.data))]
		solid_y=[[value,value] for value in self.data]
		dash_x_1=[2*index+1.25 for index,value in enumerate(self.data[:-1]) if value is not None]
		dash_x_2=[2*index+2.75 for index,value in enumerate(self.data[1:]) if value is not None]
		dash_x=[item for item in zip(dash_x_1,dash_x_2)]
		dash_y=[[self.data[int((index[0]-1.25)/2)],self.data[int((index[1]-2.75)/2+1)]] for index in dash_x]
		return solid_x,solid_y,dash_x,dash_y

class LineBase():
	"""线条基类，需提供x,y,color参数，默认实线"""
	def __init__(self,x,y,color,linewidth='',linestyle='-',**kargs):
		super().__init__(**kargs)
		self.x=x
		self.y=y
		self.color=color
		self.linewidth=linewidth
		self.linestyle=linestyle
		self.plot_line()

	def plot_line(self):
		plt.plot(self.x,self.y,self.linestyle,color=self.color,linewidth=self.linewidth)

class SolidLine(LineBase):
	"""实线类：根据给定x,y,color绘制一条实线"""
	def __init__(self,linewidth=3,**kargs):
		super().__init__(linewidth=linewidth,**kargs)

class DashLine(LineBase):
	"""虚线类：根据给定x,y,color绘制一条虚线"""
	def __init__(self,linewidth=0.5,linestyle='--',**kargs):
		super().__init__(linewidth=linewidth,linestyle=linestyle,**kargs)

class Text():
	def __init__(self,x,y,text,color,fontsize=12.5):
		self.x=x
		self.y=y
		self.color=color
		self.fontsize=fontsize
		self.text=text
		self.plot_text()

	def plot_text(self):
		plt.text(self.x,self.y,self.text,ha='center',va='center',fontsize=self.fontsize,color=self.color)

def plot_(line,f,color,states='',option='default'):
	data=Data(line)
	states=deque(states)
	for x,y in zip(data.solid_x,data.solid_y):
		f.add_solid(x,y,color)
		f.add_text(sum(x)/len(x),y[0]+0.2,states.popleft(),color) if option=='default' else 0
	for x,y in zip(data.dash_x,data.dash_y):
		f.add_dash(x,y,color)
		f.add_text(sum(x)/2,sum(y)/2,'{:.2f}'.format(abs(y[1]-y[0])),color) if option=='default' else 0

def CO3_plot(figure,loc,value_CO,value_CO3,color):
	"简化CO3绘制过程"
	figure.add_solid([0.75+2*loc,1.25+2*loc],[value_CO3,value_CO3],color)
	figure.add_text(2*loc+1,value_CO3+0.2,r'$CO_3$',color)
	figure.add_dash([3.25,0.75+2*loc],[value_CO,value_CO3],color)
	figure.add_text(loc+2,(value_CO+value_CO3)/2,'{:.2f}'.format(value_CO3-value_CO),color)

def main():
	figure=Figure()
	#Ot=[0,-0.36,0.34,-1.08,-1.97,-1.39,-3.68,-3.98,-3.13,-6.68] #Ot_clean
	#Ot=[0,-0.42,0.16,-1.40,-2.32,-2.31,-3.51,-3.89,-3.29,-7.05] #Ot_1H2O
	#Ot=[0,-0.17,0.51,-2.02,-1.95,-3.59,-3.75,-2.84,-7.07,-7.03] #Ot_2H2O
	#Ot=[0,-0.28,-0.10,-2.75,-2.40,-3.27,-3.39,-3.13,-6.93] #CeO4t_clean
	#Ot=[0,-0.33,0.23,-0.37,-1.58,-0.99]
	#Ot=[0,-0.31,0.05,-0.70,-1.60,-1.21]
	Ot=[0,-0.06,0.19,-2.38,-2.26,-3.15,-3.23,-2.73,-6.77] #CeO4t_1H2O
	#Ot=[0,-0.05,0.55,-2.47,-2.27] #CeOt_2H2O

	#Ot=[0,-0.77,-0.53,-1.44,-1.23,-2.10,-2.84,-2.80,-3.39] #CeO4t_H2O
	#Ot=[0,-0.98,-1.6,-1.29,-1.79,-2.90,-3.74,-3.12,-3.91] #Ot_H2O

	lines=[Ot]
	for line,color in zip(lines,figure.colors):
		#plot_(Ot,figure,'#01545a',states=['IS','CO','TS','IM',r'$CO_2$',r'$O_v$'])
		plot_(Ot,figure,'#ef6932',states=[r'IS','S1','TS4',r'FS1',r'$O_v$','S2','S3','TSD','FS2'])
		#plot_(Ot,figure,'#a12a5e',states=['IS',r'IM1','ID1','TS1','ID2','IM2','ID3','TS2','ID4'])
	#CO3_plot(figure,3,-0.37,-3.61,"#01545a") #绘制CO3函数
	#plt.show()
	plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')

if __name__ == '__main__':
	main()









