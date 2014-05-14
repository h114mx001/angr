import logging

import networkx

l = logging.getLogger("angr.PathPrioritizer")

class PathPrioritizer(object):
    def __init__(self, cfg, target):
        self._cfg = cfg
        self._target = target
        self._shortest_path_length_dict = {}

        self._construct()

    def __getstate__(self):
        state = {}
        state['_shortest_path_length_dict'] = self._shortest_path_length_dict
        return state

    def _construct(self):
        g = self._cfg.get_graph()
        bbl_dict = self._cfg.get_bbl_dict()
        assert(self._target in g)
        assert(bbl_dict is not None)

        # Reverse the bbl_dict
        bbl_key_map = {}
        for k, v in bbl_dict.items():
            bbl_key_map[v] = k

        # Do a BFS from target, and save the length of shortest path to each
        # basic block
        shortest_path_length = networkx.single_source_shortest_path_length( \
                                                            g, self._target)
        for k, v in shortest_path_length.items():
            bbl_key = bbl_key_map[k]
            self._shortest_path_length_dict[bbl_key] = v

    def get_priority(self, path):
        MAX_INT = 0xffffffff
        # Get a list of tuples
        # Each tuple looks like (a, b), where b is the function address of a
        # basic block, and a is the IRSB addr where the function is called
        l.debug("Retrieving path priority of %s..." % path)
        call_stack = path.call_stack
        if len(call_stack) == 0:
            l.debug("Call stack is empty")
            return MAX_INT
        # FIXME: For now we are only supporting level 2 context-sensitivity
        # But we shouldn't hard code this anyway
        tpl = call_stack[-1] + (path.last_run.addr,)
        if tpl in self._shortest_path_length_dict:
            priority = self._shortest_path_length_dict[tpl]
            l.debug("The priority is %d", priority)
            return priority
        else:
            l.debug("Not in our dict")
            return MAX_INT
