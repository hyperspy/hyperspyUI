import hyperspy

c = get_config()  # noqa: F821
c.FrontendWidget.banner = """
    H y p e r S p y
    Version {0}

    https://www.hyperspy.org
    
    """.format(hyperspy.__version__)
