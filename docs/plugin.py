# TODO: remove after sphinx_autodoc_typehints is released

def processe_docstring(  # noqa: WPS211
    app, what, name, object_, options, lines,
):
    """
    This function will process a docstring.

    Currently we have a problem using `sphinx_autodoc_typehints` plugin,
    it does not add a blank line after the content insertion.
    This function will insert the blank line if the last processed line has
    some content.
    An important thing, our plugin has to be added right after
    `sphinx_autodoc_typehints` in the extensions list!
    """
    if lines:
        last_line_has_content = bool(lines[-1])
        if last_line_has_content:
            lines.append('')


def setup(app):
    """Register a function to receive an event from sphinx."""
    app.connect('autodoc-process-docstring', processe_docstring)
    return dict(parallel_read_safe=True)
