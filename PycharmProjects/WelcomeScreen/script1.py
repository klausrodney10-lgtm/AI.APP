# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
class Dog:
    def __init__(self, name) :
        self.name = name
    def bark(self):
        return self.name + " wouf "
    def treat(self):
        return self.name + " miam "
    def bark(self):
        return self.name + " wouf "


d = Dog("Rex(Chiwawa)")
t = Dog("Tex(malinois)")
print(d.bark())
print(d.treat())
print(t.bark())
print(d.bark())
print(t.treat())









