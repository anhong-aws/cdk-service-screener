from frameworks.FrameworkPageBuilder import FrameworkPageBuilder

class MSRPageBuilder(FrameworkPageBuilder):
    def init(self):
        super().__init__()
        self.template = 'default'
        
    