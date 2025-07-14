from copy import copy


class Variable:

    def __init__(self, name, sid, var_type, index=0):
        self.name = name
        self.sid = sid
        self.index = index
        self.type = var_type


class VarsManager:

    def __init__(self):
        self.vars_dict = {}
        self.cur_index = 0

    def add_var(self, var: Variable):
        var.index = self.cur_index
        self.cur_index += 1
        if var.name not in self.vars_dict:
            self.vars_dict[var.name] = []
        self.vars_dict[var.name].append(var)

    def get_var(self, name) -> Variable | None:
        if name not in self.vars_dict:
            return None
        return self.vars_dict[name][-1]

    def pop_suf(self, border):
        keys = self.vars_dict.keys()
        rem_keys = []
        for k in keys:
            while len(self.vars_dict[k]) > 0 and self.vars_dict[k][-1].index >= border:
                self.vars_dict[k].pop()
            if len(self.vars_dict[k]) == 0:
                rem_keys.append(k)

        for k in rem_keys:
            self.vars_dict.pop(k)

    def get_stamp(self):
        res = {}
        for k, v in self.vars_dict.items():
            res[k] = copy(v[-1])
        return res
