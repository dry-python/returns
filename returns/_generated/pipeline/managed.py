def _managed(use, release):
    def factory(acquire):
        return acquire.bind(
            lambda a: use(a).compose_result(
                lambda e: release(a, e).bind(
                    lambda _: acquire.from_result(e),
                ),
            ),
        )
    return factory
