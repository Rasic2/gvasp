!将VASP计算得到的电荷文件转化为MS可读的.grd文件
!created at 2019/11/6

PROGRAM CHGCAR2GRD
  IMPLICIT none
  CHARACTER(*), PARAMETER :: vasp_form = '(5(1X,E17.11))'
  CHARACTER(*), PARAMETER :: elf_form = '(10(1X,E11.5))'
  CHARACTER(*), PARAMETER :: dmol_form = '(1p,e12.5)'
  REAL :: version
  REAL(8) :: pi=4.*atan(1.)
  CHARACTER(len=80)::HEADER, grid
  CHARACTER(len=20)::filename
  REAL(8), DIMENSION(3,3) :: A
  INTEGER, DIMENSION(10) :: num, iatom
  REAL(8) :: scale, temp1, temp2
  REAL(8), DIMENSION(3) :: length, angle
  REAL(8), DIMENSION(:,:,:), POINTER :: work1, work2, work3, work4
  INTEGER :: nspin, nx, ny, nz, sum, number, i, j, k, l, m

  !input parameters
  write(*,*) 'The program is convert the CHGCAR to the .grd file format!'
  write(*,*) 'Please input the charge density file you want to process (CHGCAR/CHGCAR_mag/ELFCAR):'
  read(*,*) filename
  IF(filename=='CHGCAR_mag') THEN
    nspin=1
  ELSE
    write(*,*) 'spin resolved or not (1 for unpolarized and 2 for polarized)'
    read *,nspin
  ENDIF
  write(*,1000) filename,nspin
  1000 FORMAT('The input file name is: ',A,'ISPIN=',I3)

  !read the CHGCAR file
  OPEN(unit=16,file=filename)
  READ(16,*) !first line
  READ(16,*) scale !second line
  DO i=1,3
     READ(16,*) (A(j,i),j=1,3) !lattice parameters (3-5 lines)
     length(i)=sqrt(A(1,i)**2+A(2,i)**2+A(3,i)**2)*scale
  END DO

  angle(1)=acos(dot_product(A(:,2),A(:,3))/(length(2)*length(3)))*180/pi
  angle(2)=acos(dot_product(A(:,3),A(:,1))/(length(3)*length(1)))*180/pi
  angle(3)=acos(dot_product(A(:,1),A(:,2))/(length(1)*length(2)))*180/pi

  READ(16,*) !element name
  READ(16,'(A)') HEADER !element counts (最多四种元素)
  i=0; j=0; k=0; l=0; m=0
  READ(HEADER,*,END=12) i,j,k,l,m
  12  sum=i+j+k+l+m

  READ (16,*) !direct line
  DO i = 1, sum
      READ (16,*)
  END DO
  READ (16,*) !空行
  READ(16,*) nx,ny,nz !grid numbers
  WRITE(grid,'(I5,I5,I5)')nx,ny,nz

  IF(nspin==1) THEN
     OPEN(unit=15,file='vasp.grd')
     WRITE(15,'(A)') 'VASP charge density'
     WRITE(15,'(A)') dmol_form
	 WRITE(15,'(6F8.3)') (length(i),i=1,3),(angle(i),i=1,3)
  	 WRITE(15,'(3I5)') nx-1,ny-1,nz-1
     WRITE(15,'(7I5)') 1,0,nx-1,0,ny-1,0,nz-1
     ALLOCATE(work1(nx,ny,nz))
     READ(16,vasp_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz)
     WRITE(15,dmol_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz)
     DEALLOCATE(work1)
  ELSE
     OPEN(unit=11,file='spin-up.grd')
     WRITE(11,'(A)') 'VASP spin-charge density'
     WRITE(11,'(A)') dmol_form
	 WRITE(11,'(6F8.3)') (length(i),i=1,3),(angle(i),i=1,3)
  	 WRITE(11,'(3I5)') nx-1,ny-1,nz-1
     WRITE(11,'(7I5)') 1,0,nx-1,0,ny-1,0,nz-1
	 OPEN(unit=12,file='spin-down.grd')
     WRITE(12,'(A)') 'VASP spin-charge density'
     WRITE(12,'(A)') dmol_form
	 WRITE(12,'(6F8.3)') (length(i),i=1,3),(angle(i),i=1,3)
  	 WRITE(12,'(3I5)') nx-1,ny-1,nz-1
     WRITE(12,'(7I5)') 1,0,nx-1,0,ny-1,0,nz-1

     ALLOCATE(work1(nx,ny,nz),work2(nx,ny,nz),work3(nx,ny,nz),work4(nx,ny,nz)) !指针:读取CHGCAR数据
     IF(filename=='ELFCAR') THEN
        READ(16,elf_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz)
     ELSE
        READ(16,vasp_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz) !up+down
     ENDIF
     DO WHILE (.NOT.(HEADER==grid))
	     READ(16,'(A)') HEADER
     ENDDO
     IF(filename=='ELFCAR') THEN
        READ(16,elf_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz)
     ELSE
        READ(16,vasp_form) (((work1(i,j,k),i=1,nx),j=1,ny),k=1,nz) !up-down
     ENDIF

     DO k=1,nz
	     DO j=1,ny
	       DO i=1,nx
	         temp1=work1(i,j,k)
	 	       temp2=work2(i,j,k)
     	     work3(i,j,k)=(temp1+temp2)/2
		       work4(i,j,k)=(temp1-temp2)/2
	        ENDDO
        ENDDO
	   ENDDO
     WRITE(11,dmol_form) (((work3(i,j,k),i=1,nx),j=1,ny),k=1,nz) !spin-up
     WRITE(12,dmol_form) (((work4(i,j,k),i=1,nx),j=1,ny),k=1,nz) !spin-down
     DEALLOCATE(work1,work2,work3,work4)

  END IF

  CLOSE(11)
  CLOSE(12)
  CLOSE(15)
  CLOSE(16)
END PROGRAM CHGCAR2GRD


