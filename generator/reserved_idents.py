import builder.nodes.nodes as ns


class ReservedIdent:
    def __init__(self, name, node, port, type_var):
        self.name = name
        self.node = node
        self.type = type_var
        self.SID = node.ports[port]


class ReservedRegister:
    _registry = {}
    _existing_nodes = {}
    _registry_out = {}

    @classmethod
    def register(cls, name, node, port, type_var):
        if name in cls._registry:
            raise KeyError(f'Duplicate identifier name {name}')
        cls._registry[name] = ReservedIdent(name, node, port, type_var)
        if node not in cls._existing_nodes:
            cls._existing_nodes[node.id] = False

    @classmethod
    def get(cls, name, graph):
        if name not in cls._registry:
            raise KeyError(f'Identifier {name} does not exist')
        ident = cls._registry[name]
        if not cls._existing_nodes[ident.node.id]:
            graph.add_node(ident.node)
            cls._existing_nodes[ident.node.id] = True
        return ident

    @classmethod
    def register_out(cls, name, node, port, type_var):
        if name in cls._registry_out:
            raise KeyError(f'Duplicate identifier name {name}')
        cls._registry_out[name] = ReservedIdent(name, node, port, type_var)
        if node not in cls._existing_nodes:
            cls._existing_nodes[node.id] = False

    @classmethod
    def get_out_list(cls):
        result = []
        for k, v in cls._registry_out.items():
            result.append({'name': k, 'type': v.type})
        return result

    @classmethod
    def fill_out(cls, vars_dict, graph):
        for name, sid in vars_dict.items():
            if name not in cls._registry_out:
                raise KeyError(f'Identifier {name} does not exist')
            var = cls._registry_out[name]
            if not cls._existing_nodes[var.node.id]:
                graph.add_node(var.node)
                cls._existing_nodes[var.node.id] = True
            graph.add_edge(sid, var.SID)


# ======= BOOL =======
ReservedRegister.register('$self_can_jump', ns.VolleyballGetBoolNode('$self_can_jump'), 'out', 'bool')
ReservedRegister.register('$opponent_can_jump', ns.VolleyballGetBoolNode('$opponent_can_jump'), 'out', 'bool')
ReservedRegister.register('$ball_is_self_side', ns.VolleyballGetBoolNode('$ball_is_self_side'), 'out', 'bool')


# ======= FLOAT =======
ReservedRegister.register('$delta_time', ns.VolleyballGetFloatNode('$delta_time'), 'out', 'number')
ReservedRegister.register('$fixed_delta_time', ns.VolleyballGetFloatNode('$fixed_delta_time'), 'out', 'number')
ReservedRegister.register('$gravity', ns.VolleyballGetFloatNode('$gravity'), 'out', 'number')
ReservedRegister.register('$pi', ns.VolleyballGetFloatNode('$pi'), 'out', 'number')
ReservedRegister.register('$simulation_duration', ns.VolleyballGetFloatNode('$simulation_duration'), 'out', 'number')
ReservedRegister.register('$team_score', ns.VolleyballGetFloatNode('$team_score'), 'out', 'number')
ReservedRegister.register('$opponent_score', ns.VolleyballGetFloatNode('$opponent_score'), 'out', 'number')
ReservedRegister.register('$touches_remain', ns.VolleyballGetFloatNode('$touches_remain'), 'out', 'number')


# ======= VEC3 =======
ReservedRegister.register('$self_position', ns.VolleyballGetVec3Node('$self_position'), 'out', 'vec3')
ReservedRegister.register('$self_velocity', ns.VolleyballGetVec3Node('$self_velocity'), 'out', 'vec3')
ReservedRegister.register('$ball_position', ns.VolleyballGetVec3Node('$ball_position'), 'out', 'vec3')
ReservedRegister.register('$ball_velocity', ns.VolleyballGetVec3Node('$ball_velocity'), 'out', 'vec3')
ReservedRegister.register('$opponent_position', ns.VolleyballGetVec3Node('$opponent_position'), 'out', 'vec3')
ReservedRegister.register('$opponent_velocity', ns.VolleyballGetVec3Node('$opponent_velocity'), 'out', 'vec3')


# ======== OUT ========
tmp = ns.SlimeControllerNode()
ReservedRegister.register_out('$slime_move_to', tmp, 'move', 'vec3')
ReservedRegister.register_out('$slime_jump', tmp, 'jump', 'bool')
