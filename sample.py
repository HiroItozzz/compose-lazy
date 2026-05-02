import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--test")
print(parser.parse_args())
group = parser.add_argument_group("group")
print(type(group))
print(type(parser))
print(type(group).__mro__)
print(type(parser).__mro__)


class FooAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print("%r %r %r" % (namespace, values, option_string))
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser()
parser.add_argument("--foo", action=FooAction)
parser.add_argument("bar", action=FooAction)
args = parser.parse_args("1 --foo 2".split())
