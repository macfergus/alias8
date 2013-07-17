#!/usr/bin/env python
import alias
def create_instance(c_instance):
  reload(alias)
  return alias.Alias8(c_instance)
