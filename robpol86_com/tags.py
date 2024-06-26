"""Blog-style tagging."""

from typing import List

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.domains.index import IndexDirective
from sphinx.errors import SphinxError


class TagsDirective(IndexDirective):
    """Enhanced Sphinx index directive so it acts more like a tag manager."""

    def run(self) -> List:
        """Called by Sphinx."""
        index_node, target_node = super().run()
        tags = [t[1] for t in index_node["entries"]]
        if not tags:
            return [index_node, target_node]
        if tags != sorted(tags):
            raise SphinxError(f"Tags not in alphabetical order in document {self.env.docname}")

        # Build nodes.
        env = self.env
        builder = env.app.builder
        human_readable_tag_list = nodes.emphasis("Tags: ", "Tags: ")
        idx_last = len(tags) - 1
        for idx, tag in enumerate(tags):
            tag_node = nodes.inline(tag, tag, classes=["guilabel"])
            uri = f"{builder.get_relative_uri(env.docname, 'genindex')}#{tag[0].upper()}"
            linked_tag_node = nodes.reference("", "", tag_node, refuri=uri, internal=True)
            # Insert.
            human_readable_tag_list.append(linked_tag_node)
            if idx != idx_last:
                human_readable_tag_list.append(nodes.Text(", ", ", "))

        return [index_node, target_node, nodes.paragraph("", "", human_readable_tag_list)]


def setup(app: Sphinx):
    """Called by Sphinx.

    :param app: Sphinx application object.
    """
    app.add_directive("tags", TagsDirective)
