import pdb

def buggy_function(x):
    #pdb.set_trace()

    x = x + 0
    x = x + 1
    y = x * 5

    return y

result = buggy_function(5)
print(result)

