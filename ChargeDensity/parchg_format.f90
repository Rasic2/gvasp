      implicit real*8 (a-h,o-z)  !规定变量类型，以a-h，o-z开头的变量为双精度浮点型
      dimension dump(20),num(2),elem(2),x(100),y(100),z(100),chg(100,100,800) !定义数组
      dimension a(3,3) 

      write(6,*) 'Spin polarized calculation? (no=1, yes=2):' !将内容以默认格式输出到6号设备（默认显示器）
      read (5,*) ispin

      open(15,file='/Users/apple/Desktop/PARCHG')
      open(7,file='/Users/apple/Desktop/parchg-cut_1')

      read(15,1) dump
      write(7,1) dump
      read(15,*) scale
      write(7,199) scale
      do i=1,3
      read(15,*) (a(i,j),j=1,3)
      write(7,199) (a(i,j),j=1,3)
 199  format(3f11.6) !3个小数点后5位共10位的浮点数
      enddo
 1    format(20a4)   !20个长度为4的字符串
      read(15,3) elem(1),elem(2)  
      write(7,3) elem(1),elem(2)
 3    format(2a6)  
      read(15,2) num(1),num(2)
      write(7,2) num(1),num(2)
 2    format(2i6)    !2个4位整数
      ity=1
      if (num(2) .gt. 0) ity=2 !大于
      natm=0
      do i=1,ity
      natm=natm+num(i)
      enddo
      read(15,1) dump
      write(7,1) dump
      do i=1,natm
      read(15,88) x(i),y(i),z(i)
      write(7,88) x(i),y(i),z(i)
      enddo
 88   format(3(f10.6))
      read(15,1) dump
      write(7,1) dump  
      do 600 is = 1,ispin
        read(15,4) nx,ny,nz
        write(7,4) nx,ny,nz
 4      format(3i5)
      read(15,*) (((chg(i,j,k),i=1,nx),j=1,ny),k=1,nz)
      do i=1,nx
      do j = 1,ny
      do k = 1,nz
      enddo
      enddo
      enddo
      write(7,5) (((chg(i,j,k),i=1,nx),j=1,ny),k=1,nz)
   5  format(5(e12.5,1x)) !5个以指数形式输出，右移一位
      if (is .eq. 2) go to 600 
      read(15,1) dump
      write(7,1) dump
 600  continue
      stop  
  	end