ids = [2,4,18,33,41]
mask = 0
for i in ids:
    mask |= (1 << i)
print('ids:', ids)
print('mask decimal:', mask)
print('mask hex: 0x{0:X}'.format(mask))
print('bits set:', [i for i in range(0,128) if (mask>>i)&1])
