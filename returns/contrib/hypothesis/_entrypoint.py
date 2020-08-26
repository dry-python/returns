from returns.result import Result


def hypothesis_setup_hook():
    from hypothesis import strategies as st

    # TODO: add all other container defs
    st.register_type_strategy(Result, st.one_of(
        st.builds(Result.from_value),
        st.builds(Result.from_failure),
    ))
