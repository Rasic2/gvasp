!fort_func
!created at 2019/11/6

subroutine multiply(a,b,result)
	implicit none
	real(kind=8),intent(in)::a,b
	real(kind=8),intent(out)::result

	result=a*b
end subroutine

subroutine fort_floor(input,output)
	implicit none
	real(kind=8),intent(in)::input
	integer,intent(out)::output

	output=floor(input)
end subroutine

subroutine distance(n,vector_1,vector_2,sum)
	implicit none
	integer::i
	real::temp
	integer,intent(in)::n
	real,intent(in),dimension(n)::vector_1,vector_2
	real,intent(out)::sum

	sum=0
	do i=1,n
		temp=(vector_1(i)-vector_2(i))**2
		sum=sum+temp
	end do
end subroutine

subroutine target(N,f_vector,D_matrix,len)
	!TSP问题路径求和函数
	implicit none
	integer::i
	integer,intent(in)::N
	integer,intent(in),dimension(0:N-1)::f_vector
	real(kind=8),intent(in),dimension(0:N-1,0:N-1)::D_matrix
	real(kind=8),intent(out)::len

	len=0.
	len=D_matrix(f_vector(N-1),f_vector(0))
	do i=0,N-2
		len=len+D_matrix(f_vector(i),f_vector(i+1))
	end do
end subroutine