"""Old code that needs to be revisited and reorganized."""
from pathlib import Path
from typing import List

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.domains.index import IndexDirective
from sphinx.errors import SphinxError


def render_robots_txt(app: Sphinx, _):
    """Parse Jinja2 templating in robots.txt file.

    :param app: Sphinx application object.
    :param _: Unused.
    """
    robots_txt_path = Path(app.outdir) / "robots.txt"
    if robots_txt_path.is_file():
        contents = robots_txt_path.read_text(encoding="utf8")
        context = dict(app.config.html_context, config=app.config)
        rendered = app.builder.templates.render_string(contents, context)
        robots_txt_path.write_text(rendered, encoding="utf8")


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
        human_readable_tag_list = nodes.emphasis("Tags: ", "Tags: ")
        idx_last = len(tags) - 1
        for idx, tag in enumerate(tags):
            tag_node = nodes.inline(tag, tag, classes=["guilabel"])
            uri = f"{self.config.html_baseurl}genindex.html#{tag[0].upper()}"
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
    app.connect("build-finished", render_robots_txt)
    app.add_directive("tags", TagsDirective)
