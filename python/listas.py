# Lists are mutable
lst = [10, 20]
print(lst[0])  # Output: 10
print(lst[1])  # Output: 20
print(lst)     # Output: [10, 20]
print(type(lst))  # Output: <class 'list'> 
print(len(lst))   # Output: 2

#Tuplas are immutable
b = (12345, "hello  world", 3,14, 5.0)
b[2] = 100  # This will raise a TypeError because tuples are immutable
print(b[2])   # Output: 3
print(b)      # Output: (12345, 'hello  world', 3, 14, 5.0)
print(type(b))  # Output: <class 'tuple'>
print(len(b))   # Output: 5