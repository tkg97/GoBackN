class Queue:
    ''' 
    A basic queue implementation, which is thread safe as list is threadsafe but not safe to random operations done by user
    It assumes a judicial usage by the user
    Purposefully made for this assignment only, should not be used for general purpose
    To extend to general purpose, will need to implement some exceptions and handle corner cases
    '''
    def __init__(self, max_size):
        self.max_size = max_size
        self.list = list()

    def put(self, element):
        self.list.append(element)

    def get(self):
        temp = self.top()
        self.list.pop(0)
        return temp

    def empty(self):
        if(len(self.list) == 0):
            return True
        return False

    def full(self):
        if(len(self.list) == self.max_size):
            return True
        return False

    def top(self):
        return self.list[0]

    def clear(self):
        self.list.clear()

    def size(self) :
        return len(self.list)