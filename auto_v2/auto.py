


from .common import Descriptor


from auto.selenium import Page

# wait
import time
from typing import Tuple, Union, List
from abc import ABC, abstractmethod
import random

# from.selenium.context import Context

def module_name(obj):
    return obj.__class__.__module__

class Auto:
    def __init__(self, contexts):
        self.__contexts = contexts

    def _context(self, desc:Descriptor):
        for ctx in self.__contexts:
            if module_name(desc) == module_name(ctx):
                return ctx
        return None

    def _activate(self, context, target:Descriptor):
        parent = target.parent()
        if parent:
            if not self._activate(context, parent):
                return False
            return context.activate(target)

        return True

    def _get(self, context, target:Descriptor):
        if not context:
            # NoContextException
            return False

        if not self._activate(context, target):
            # Failed To activate
            return False

        return  context.get(target)


    def _get_all(self, context, target:Descriptor):
        if not context:
            # NoContextException
            return False

        if not self._activate(context, target):
            # Failed To activate
            return False

        return context.get_all(target)

    def _dispatch(self, context, op, elem, *args):
        if not context:
            # NoContextException
            return False
        op = getattr(context, op, None)
        if not op:
            # NotSupportedOperation
            return False

        return op(elem, *args)


    def go(self, target:Descriptor):
        ctx = self._context(target)
        if not ctx:
            return False
        return ctx.go(target)


    def do(self, op, target:Descriptor, *args):
        ctx = self._context(target)
        if not ctx:
            # NoContextException
            return False

        elem = self._get(ctx, target)
        if not elem:
            # NotFound
            return False

        return self._dispatch(ctx, op, elem, *args)


    def do_all(self, op, target:Descriptor, *args, num_samples):
        ctx = self._context(target)
        if not ctx:
            # NoContextException
            return False

        if num_samples:
            elems = random.sample(elems, k=num_samples)


        success = True
        for elem in elems:
            success = self._dispatch(op, elem, *args,)
        return success


    def exist(self, target:Descriptor):
        ctx = self._context(target)
        if not ctx:
            # NoContextException
            return False

        elem = self._get(ctx, target)
        if not elem:
            # NotFound
            return False

        return True


    def click(self, target:Descriptor):
        return self.do("click", target)


    def clicks(self, target:Descriptor, *, num_samples=None):
        return self.do_all("click", target, num_samples=num_samples)


    def accept(self, target:Descriptor):
        return self.do("accept", target )
