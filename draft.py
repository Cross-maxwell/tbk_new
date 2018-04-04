userlist = [
    {'name': 'jack', 'pwd': 123, 'loged': False, 'group': [1]},
    {'name': 'jhon', 'pwd': 123, 'loged': False, 'group': [1, 2, 3, 4]},
    {'name': 'Alice', 'pwd': 123, 'loged': False, 'group': [1, 2]},
    {'name': 'Catherine', 'pwd': 123, 'loged': False, 'group': [1, 2, 3]},
]




class Robot(object):
    __slots__ = ('logged', 'name', 'pwd' )
    def __init__(self, name, pwd):
        self.logged = False  # 这就相当于 Token
        self.name = name
        self.pwd = pwd

    def login(self, pwd):
        if pwd == self.pwd:
            self.logged = True
        return self.logged

    def logout(self):
        self.logged = False
        return not self.logged





class Ak47(object):
    pass



class TencentServer(object):
    __slots__ = ('logged', 'name', 'pwd')

    def __init__(self, name, pwd):
        self.logged = False  # 这就相当于 Token
        self.name = name
        self.pwd = pwd

    def login(self, pwd):
        if pwd == self.pwd:
            self.logged = True
        return self.logged

    def logout(self):
        self.logged = False
        return not self.logged
