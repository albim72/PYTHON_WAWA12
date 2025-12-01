#przykład 1 - rekurencja

def factiorial(n):
    if n==0 or n==1:
        return 1
    return n*factiorial(n-1)
print(factiorial(200))
