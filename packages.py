async def NULL_HOOK(package):
    pass


class BasePackage:
    def __init__(self, core, hook: callable):
        self.core = core
        self.hook = hook
        self.data = {}
        self.completed = False

    async def run_hook(self):
        if not self.completed:
            await self.hook(self)
            self.completed = True


class TextPackage(BasePackage):
    def __init__(self, input_text, core, hook, for_filter=None):
        super().__init__(core, hook)
        self.input_text = input_text
        self.for_filter = for_filter or input_text

    @property
    def text(self):
        if "text" in self.data:
            return self.data["text"]
        return None

    @text.setter
    def text(self, value):
        if isinstance(value, str):
            self.data["text"] = value
        else:
            raise TypeError(f".text must be str, got {type(value)}")


class TelegramAnswerPackage(TextPackage):
    def __init__(self, input_text, core, answer: callable, for_filter=None):
        self.answer = answer
        super(TelegramAnswerPackage, self).__init__(input_text, core, for_filter=for_filter)


class HookExtendPackage(BasePackage):
    """
    Расширяет вызов основного крюка двумя вызовами перед и после основного.
    """

    def __init__(self, input_text, core, hook):
        super().__init__(core, hook)
        self.input_text = input_text

    @property
    def pre_hook(self):
        if "pre_hook" in self.data:
            return self.data["pre_hook"]
        return None

    @pre_hook.setter
    def pre_hook(self, value):
        if isinstance(value, callable):
            self.data["pre_hook"] = value
        else:
            raise TypeError(f".pre_hook must be callable, got {type(value)}")

    @property
    def post_hook(self):
        if "post_hook" in self.data:
            return self.data["post_hook"]
        return None

    @post_hook.setter
    def post_hook(self, value):
        if isinstance(value, callable):
            self.data["post_hook"] = value
        else:
            raise TypeError(f".post_hook must be callable, got {type(value)}")

    async def run_hook(self):
        if not self.completed:
            await self.pre_hook(self)
            await self.hook(self)
            await self.post_hook(self)
            self.completed = True
