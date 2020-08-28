def hypothesis_setup_hook():
    """
    Used to register all our types as hypothesis strategies.

    See: https://hypothesis.readthedocs.io/en/latest/strategies.html

    But, beware that we only register concrete types here,
    interfaces won't be registered!
    """
