#przykład 2 - funlcja przetwarzająca listę - filtorwamnie liczb parzystych
import numpy as np
def filter_even(numbers):
    return [num for num in numbers if num%2==0]

liczby = [86,5,56,3,6,89,0,-5,234,6,90,64,0,64,544,-334]
print(filter_even(liczby))

arr = np.array(liczby)
ap = arr[arr%2==0]
print(ap)
print(type(ap))
