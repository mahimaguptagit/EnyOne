a=int(input("Enter the number :"))
for i in range(1,a) :
    print('*'*i)

for n in range(a,0,-1):
    print('*'*n)


print('new design')
for v in range(1,a+1) :
    print(' '*(a-v)+'*'*v)

