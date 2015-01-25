import handicaps

class Ruleset(object):

    def __init__(self, name, handicaper, **kwargs):
        self.name = name
        self.handicaper = handicaper

        for key in kwargs:
            if self[key] != None:
                self[key] = kwargs[key]

    def handicap(*args):
        if args.length >= 2:
            return self.handicaper(args)
        else:
            raise TypeError


RULESETS = {
    "APA8BALL": Ruleset(
                    "APA8BALL",
                    handicaps.APA8BALL
                )
}