범위 = range

def 점_그리기():
    pass

a = 10
b = 5

r = 3

for x in 범위(0, 100):
    for y in 범위(0, 100):
        if (x-a)**2 + (y-b)**2 < r**2:
            점_그리기()