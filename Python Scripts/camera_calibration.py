import ctypes

# Load the shared library containing the C++ function
my_lib = ctypes.cdll.LoadLibrary('./my_lib.so')

# Define the argument and return types for the C++ function
my_func = my_lib.my_func
my_func.argtypes = [ctypes.c_int, ctypes.c_int]
my_func.restype = ctypes.c_int

# Call the C++ function from Python
result = my_func(2, 3)

print(result)