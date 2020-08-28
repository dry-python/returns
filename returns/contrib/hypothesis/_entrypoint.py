from returns.result import Result


def hypothesis_setup_hook():
    """
    Used to register all our types as hypothesis strategies.

    See: https://hypothesis.readthedocs.io/en/latest/strategies.html

    But, beware that we only register concrete types here,
    interfaces won't be registered!
    """
    from hypothesis import strategies as st

    # TODO: add all other container defs
    st.register_type_strategy(Result, st.one_of(
        st.builds(Result.from_value),
        st.builds(Result.from_failure),
    ))
