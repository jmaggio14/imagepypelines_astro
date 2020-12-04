import imagepypelines as ip

# Define the base class for all Astronomy
################################################################################
class AstroBlock(ip.Block):
    """Special Block made for astronomy with a predefined IO inputs and useful
    properties

    """
    def __init__(self,**kwargs):
        """instantiates the AstroBlock"""
        # NOTE: add default input types
        kwargs.update({'batch_type':'each'})
        super().__init__(**kwargs)
        self.tags.add("astronomy")



class AstroBlockAll(ip.Block):
    """Special Block made for astronomy with a predefined IO inputs and useful
    properties

    """
    def __init__(self,**kwargs):
        """instantiates the AstroBlock"""
        # NOTE: add default input types
        kwargs.update({'batch_type':'all'})
        super().__init__(**kwargs)
        self.tags.add("astronomy")
