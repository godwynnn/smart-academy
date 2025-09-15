# from django.test import TestCase

# Create your tests here.
users = [
  { 'id': 1, 'name': 'Alice', 'age': 30 },
  { 'id': 2, 'name': 'Bob', 'age': 25 }
]

def pluck(arr, item):
    array=[]
    for user in arr:
        array.append(user[item])
    return array

print(pluck(users,'age'))
        

