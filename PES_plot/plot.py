#!/usr/bin/env python
# -*- coding:utf-8 -*-
# created by hui_zhou@mail.ecust.edu.cn
# modified at 2019/04/19
# modified at 2019/06/03 增加CO3绘制过程
# modified at 2019/07/01 用于论文撰写
# modified at 2020/11/22 调整文本框避免重叠（反复横跳机制，考虑截距）
# modified at 2020/11/30 增加识别None值功能
# <--Version:1.4.1-->

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
		bwith=3
		ax=plt.gca()
		ax.spines['bottom'].set_linewidth(bwith) # 设置边框宽度
		ax.spines['left'].set_linewidth(bwith)
		ax.spines['top'].set_linewidth(bwith)
		ax.spines['right'].set_linewidth(bwith)
		plt.tick_params(axis='y',which='both')
		plt.tick_params(width=2,length=4)
		plt.title(self.title,fontsize=18)
		#plt.xticks([1,3,5,7,9,11,13,15,17],[r'$IS$',r'$CH_3OH*$','TS1',r'$CH_3O*+H*$','TS2',r'$CH_2O*+2H*$',r'$CH_2O(t)*+2H*$','TS3'],fontsize=22,rotation=15)
		plt.xticks([])
		plt.yticks(fontsize=22)
		plt.xlim((0.5,15.5))
		plt.ylim((-2.6,0.9))
		plt.xlabel(self.xlabel,fontsize=24)
		plt.ylabel(self.ylabel,fontsize=24)
		#plt.legend(loc='best')
	return wrapper

class Figure():
	"""图像类，为图像增加实线对象、虚线对象"""
	@plot_wrap
	def __init__(self,xticks='',title='',xlabel='Reaction coordinate',ylabel='Energy / eV',width=15.6,height=4):
		self.width=width
		self.height=height
		self.fig=plt.figure(figsize=(width,height))
		self.ax=self.fig.add_subplot(1,1,1)
		ymajorFormatter=FormatStrFormatter('%.1f') #设置y轴主刻度小数位数
		self.ax.yaxis.set_major_formatter(ymajorFormatter)
		#y_major_locator=MultipleLocator(0.5) #把y轴的刻度间隔设置为10，并存在变量里
		#self.ax.yaxis.set_major_locator(y_major_locator)
		#self.colors=['#000000','#01545a','#ed0345','#ef6932','#710162','#017351','#03c383','#aad962','#fbbf45','#a12a5e']
		self.colors=['#000000','#ed0345','#004370','#01545a','#ef6932','#fbbf45',]
		self.title=title
		#self.count=count
		self.xticks=xticks
		self.xlabel=xlabel
		self.ylabel=ylabel
		self.texts=defaultdict(list)

	def add_solid(self,linewidth,x,y,color):
		SolidLine(linewidth,x=x,y=y,color=color)

	def add_dash(self,linewidth,x,y,color):
		DashLine(linewidth,x=x,y=y,color=color)

	def add_text(self,x,y,text,color):
		self.texts[color].append(Text(self,x,y,text,color))

class Data():
	"""将每一条路径数据转换为实线和虚线坐标"""
	def __init__(self,data):
		self.data=data
		self.solid_x,self.solid_y,self.dash_x,self.dash_y=self.__convert()

	def __convert(self):
		solid_x=[[0.75+2*i,1.25+2*i] for i in range(len(self.data))]
		solid_y=[[value,value] for value in self.data]
		dash_x_1=[2*index+1.25 for index,value in enumerate(self.data[:-1]) if value is not None]
		dash_x_2=[value+1.5 for value in dash_x_1]
		dash_x=[item for item in zip(dash_x_1,dash_x_2)]
		dash_y=[[self.data[int((index[0]-1.25)/2)],self.data[int((index[1]-2.75)/2+1)]] for index in dash_x]
		return solid_x,solid_y,dash_x,dash_y

class LineBase():
	"""线条基类，需提供x,y,color参数，默认实线"""
	def __init__(self,x,y,color,linewidth='',linestyle='-',**kargs):
		#super().__init__(**kargs)
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
	def __init__(self,fig_obj,x,y,text,color,fontsize=18):
		self.fig=fig_obj
		self.x=x
		self.y=y
		self.x_ave=sum(x)/2
		self.y_ave=sum(y)/2
		self.color=color
		self.fontsize=fontsize
		self.text=text
		self.check_overlap()
		self.plot_text()

	def check_overlap(self):
		left_m=-0.3*(self.fontsize/18)/(self.fig.width/15.6)/(self.fig.height/8) 	# 左边缘
		right_m=0.3*(self.fontsize/18)/(self.fig.width/15.6)/(self.fig.height/8)	# 右边缘
		top_m=0.07*(self.fontsize/18)/(self.fig.width/15.6)/(self.fig.height/8) 	# 上边缘
		bottom_m=-0.05*(self.fontsize/18)/(self.fig.width/15.6)/(self.fig.height/8) # 下边缘
		index_color=list(self.fig.texts.keys()).index(self.color)
		if(index_color!=0):
			SOD=(self.x_ave+right_m<self.x[1] and self.x_ave+left_m>self.x[0])	# 反复横跳截止判据
			count=1
			b_adj=1
			while(SOD):
				CODs=[]
				for i in range(index_color):
					values=[j.x_ave for j in self.fig.texts[list(self.fig.texts.keys())[i]]]
					if (sum(self.x)/2 in values):
						index_fragment=values.index(sum(self.x)/2)
						item=self.fig.texts[list(self.fig.texts.keys())[i]][index_fragment]
					else:
						continue
					COD1=(self.y_ave+bottom_m>item.y_ave+top_m or self.y_ave+top_m<item.y_ave+bottom_m) # 重叠判据.1
					COD2=(self.x_ave+right_m<item.x_ave+left_m or self.x_ave+left_m>item.x_ave+right_m) # 重叠判据.2
					CODs.append(0) if(COD1 or COD2) else CODs.append(1)
				if(sum(CODs)==0):
					break
				else:
					k=(self.y[1]-self.y[0])/(self.x[1]-self.x[0])
					delta_y=(top_m-bottom_m)/2*count*(-1)**count #反复横跳
					self.y_ave=self.y_ave+delta_y
					self.x_ave=self.x_ave+delta_y/k
					count+=1
					SOD=(self.x_ave+right_m<self.x[1] and self.x_ave+left_m>self.x[0])	# 反复横跳截止判据
				if(SOD!=True):
					record=self.x
					if(record==self.x):
						b_adj+=1
					self.x_ave=sum(self.x)/2
					self.y_ave=sum(self.y)/2+(top_m-bottom_m)/100*b_adj*(-1)**b_adj # 改变截距重新横跳
					SOD=(self.x_ave+right_m<self.x[1] and self.x_ave+left_m>self.x[0])
					count=1
					print("{}: 第 {} 次 Adjust the interacpt!!!".format(record,b_adj-1))

	def plot_text(self):
		plt.text(self.x_ave,self.y_ave,self.text,ha='center',va='center',fontsize=self.fontsize,color=self.color)
		#print(test.__dict__)
		#exit()
def plot_(name,names,line,f,color,states='',option='default'):
	data=Data(line)

	states=deque(states)
	for x,y in zip(data.solid_x,data.solid_y):
		f.add_solid(5,x,y,color)
		#f.add_text(sum(x)/len(x),y[0]+0.2,states.popleft(),color) if option=='default' else 0

	for x,y in zip(data.dash_x,data.dash_y):
		if(name not in names):
			f.add_solid(1.5,x,y,color)
		else:
			f.add_dash(1.5,x,y,color)
		f.add_text(x,y,'{:.2f}'.format(abs(y[1]-y[0])),color) if option=='default' else 0

def main():
	figure=Figure()

	lines={
	#r'undoped_CH3OH_1':[None,None,None,0.44,0.89,-1.07],
	#r'undoped_CH3OH_2':[None,None,None,None,None,-2.05,-0.62,-1.07],
	#r'undoped':[0,-0.06,1.20,0.44,0.59,-2.05,-0.87,-1.41],
	r'Ca-doped_CH3OH_1':[None,None,None,0.06,0.39,-1.51],
	r'Ca-doped_CH3OH_2':[None,None,None,None,None,-2.46,-0.95,-1.66],
	r'Ca-doped':[0,-0.09,0.75,0.06,0.26,-2.46,-1.02,-1.58],
	#r'Ca-doped_CH3OH_2':[0,-0.07,0.89,0.25],
	}

	models=['undoped','Ca-doped']
	suffix=['','_CH3OH_1','_CH3OH_2']
	names=[x+y for x in models for y in suffix]

	#plt.fill_between([0.6,7],-2.2,1.4,facecolor='#FFE1E1')
	#plt.fill_between([7,11],-2.2,1.4,facecolor='#E6FFE7')
	#plt.fill_between([11,15.4],-2.2,1.4,facecolor='#E2E2FF')
	plt.fill_between([0.6,7],-2.6,0.9,facecolor='#FFE1E1')
	plt.fill_between([7,11],-2.6,0.9,facecolor='#E6FFE7')
	plt.fill_between([11,15.4],-2.6,0.9,facecolor='#E2E2FF')

	for name,line,color in zip(lines.keys(),lines.values(),figure.colors):
		if(name=='undoped_CH3OH_1' or name=='Ca-doped_CH3OH_1'):
			plot_(name,names,line,figure,'#ed0345',option='default')
		elif(name=='undoped_CH3OH_2' or name=='Ca-doped_CH3OH_2'):
			plot_(name,names,line,figure,'#004370',option='default')
		elif(name=='undoped'or name=='Ca-doped'):
			plot_(name,names,line,figure,'#000000',option='default')
		else:
			plot_(name,names,line,figure,color)
			plt.plot(0.5,0,color=color,label=name)
	#plt.legend(loc='best',fontsize=18)
	#plt.show()
	plt.savefig('/Users/apple/Desktop/figure.svg',dpi=300,bbox_inches='tight')

if __name__ == '__main__':
	main()
