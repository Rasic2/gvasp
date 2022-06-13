#!/usr/bin/env python
# -*- coding:utf-8 -*-
#created by hui_zhou@mail.ecust.edu.cn
#modified at 2019/04/19
#modified at 2019/06/03 增加CO3绘制过程
#modified at 2019/07/01 用于论文撰写
# <--Version:1.2.5-->
import math
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter
from matplotlib.pyplot import MultipleLocator
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
		#plt.xticks([1,3,5,7,9,11,13,15,17,19],['IS',r'S1','TS1',r'$IM$',r'$FS1$',r'$O_v$','S2','S3','TS2','FS2'],fontsize=22)
		plt.xticks([1,3,5,7,9,11,13,15,17],['IS',r'S1','TS1',r'$FS1$',r'$O_v$','S2','S3','TS2','FS2'],fontsize=22)
		#plt.xticks([1,3,5,7],[r'$O_2^*$',r'$S3$','TS2',r'$S4$'],fontsize=22)
		plt.yticks(fontsize=22)
		#plt.ylim((-1.6,0.5))
		plt.xlabel(self.xlabel,fontsize=24)
		plt.ylabel(self.ylabel,fontsize=24)
		#plt.legend(loc='best')
	return wrapper

class Figure():
	"""图像类，为图像增加实线对象、虚线对象"""
	@plot_wrap
	def __init__(self,xticks='',title='',xlabel='Reaction coordinate',ylabel='Energy(eV)',width=14.4,height=7):
		self.fig=plt.figure(figsize=(width,height))
		self.ax=self.fig.add_subplot(1,1,1)
		ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
		self.ax.yaxis.set_major_formatter(ymajorFormatter)
		#y_major_locator=MultipleLocator(0.5) #把y轴的刻度间隔设置为10，并存在变量里
		#self.ax.yaxis.set_major_locator(y_major_locator)
		self.colors=['#000000','#01545a','#ed0345','#ef6932','#710162','#017351','#03c383','#aad962','#fbbf45','#a12a5e']
		self.colors=['#ed0345','#ef6932','#710162','#017351','#03c383','#aad962','#fbbf45','#a12a5e']
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
	def __init__(self,linewidth=5,**kargs):
		super().__init__(linewidth=linewidth,**kargs)

class DashLine(LineBase):
	"""虚线类：根据给定x,y,color绘制一条虚线"""
	def __init__(self,linewidth=2,linestyle='--',**kargs):
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
		#f.add_text(sum(x)/len(x),y[0]+0.2,states.popleft(),color) if option=='default' else 0
	for x,y in zip(data.dash_x,data.dash_y):
		f.add_dash(x,y,color)
		#f.add_text(sum(x)/2,sum(y)/2,'{:.2f}'.format(abs(y[1]-y[0])),color) if option=='default' else 0

def CO3_plot(figure,loc,value_CO,value_CO3,color):
	"简化CO3绘制过程"
	figure.add_solid([0.75+2*loc,1.25+2*loc],[value_CO3,value_CO3],color)
	figure.add_text(2*loc+1,value_CO3+0.2,r'$CO_3$',color)
	figure.add_dash([3.25,0.75+2*loc],[value_CO,value_CO3],color)
	figure.add_text(loc+2,(value_CO+value_CO3)/2,'{:.2f}'.format(value_CO3-value_CO),color)

def main():
	figure=Figure()

	lines={#'clean  O-t':[0,-0.36,0.34,-1.08,-1.97,-1.39,-3.68,-3.98,-3.13,-6.68],
	#'hydro O-t':[0,-0.42,0.16,-1.40,-2.32,-2.31,-3.51,-3.89,-3.29,-7.05],}
	r'clean  $CeO_4$-t':[0,-0.28,-0.10,-2.75,-2.40,-3.27,-3.39,-3.13,-6.93],
	r'hydro $CeO_4$-t':[0,-0.06,0.19,-2.38,-2.26,-3.15,-3.23,-2.73,-6.77]}
	"""
	lines={r'$O^A$':[0,-0.30,0.55,-3.00],
	r'$O^B$':[0,-0.38,0.22,-3.54],
	r'$O^C$':[0,-0.12,0.14,-3.67],
	r'$O^D$':[0,-0.08,0.42,-3.62]}
	"""
	for name,line,color in zip(lines.keys(),lines.values(),figure.colors):
		plot_(line,figure,color)
		plt.plot(0.5,0,color=color,label=name)
		#plt.plot(0,0,color=color,label=)
	#CO3_plot(figure,3,-0.37,-3.61,"#01545a") #绘制CO3函数
	plt.legend(loc='best',fontsize=18)
	#plt.show()
	plt.savefig('/Users/apple/Desktop/figure.png',dpi=300,bbox_inches='tight')

if __name__ == '__main__':
	main()









