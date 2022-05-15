import attr


@attr.s
class Switchable:
    is_stopped = attr.ib(type=bool, kw_only=True, default=False)

    def switch(self):
        self.is_stopped = not self.is_stopped
