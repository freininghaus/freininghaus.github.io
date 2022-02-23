# Copyright (c) 2022 Frank Reininghaus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

import dateutil
import glob
import hashlib
import io
import os
import datetime
import shutil

import md4c  ## TODO requirements

import blinker
import nikola.nikola
from nikola import utils, metadata_extractors, post
from nikola.plugin_categories import CommentSystem, SignalHandler
from nikola.post import get_meta

try:
    import ruamel.yaml
    YAML = ruamel.yaml.YAML(typ='safe')
except ImportError:
    utils.req_missing(['ruamel.yaml'], 'read staticman comments')

try:
    import markdown
except ImportError:
    utils.req_missing(['markdown'], 'render markdown in staticman comments')

_LOGGER = utils.get_logger('staticman_comments')


class Comment:
    def __init__(self, yaml_data):
        # TODO: error handling
        data = YAML.load(yaml_data)
        self.author = data['author']
        self.url = data['url']
        self.date = data['date']

        if isinstance(self.date, str):
            self.date = dateutil.parser.parse(self.date)

        self.id = data['_id']
        self.replying_to_id = data.get('replying_to_id')
        self.message = data['message']

        # Set the options that are default for markdown-wasm, see https://github.com/rsms/markdown-wasm#api
        renderer = md4c.HTMLRenderer(collapse_whitespace=True,
                                     permissive_atx_headers=True,
                                     permissive_url_autolinks=True,
                                     strikethrough=True,
                                     tables=True,
                                     tasklists=True)
        self.html = renderer.parse(self.message)

        self.parent = None

    def sort_key(self):
        own_key = (self.date,)

        if self.parent is None:
            return own_key
        else:
            return self.parent.sort_key() + own_key

    def nesting_level(self):
        if self.parent is None:
            return 0
        else:
            return self.parent.nesting_level() + 1

class StaticmanCommentHandler(SignalHandler):
    def _load_comment(self, comment_file_path):
        # TODO: error handling
        with open(comment_file_path) as f:
            return Comment(f)

    def _process_comments(self, comments_directory):
        comments_by_id = {
            comment.id: comment
            for comment in (self._load_comment(comment_file_path)
                            for comment_file_path in glob.glob(os.path.join(comments_directory, '*.yml')))
        }

        for comment in comments_by_id.values():
            replying_to_id = comment.replying_to_id
            if replying_to_id is not None:
                comment.parent = comments_by_id[replying_to_id]

        return sorted(comments_by_id.values(), key=lambda comment: comment.sort_key())

    def _process_comments_for_posts_and_pages(self, site):
        """Add comments to all posts."""
        if site is self.site:
            for post in site.timeline:
                print(f"!!> adding comments to {post=}")
                path, post_source_file = os.path.split(post.source_path)
                comments_directory = os.path.join(path, post_source_file + '.comments')
                post.comments = self._process_comments(comments_directory)

                # TODO: error handling

        # Copy js to output folder
        # TODO: find a better way to do it
        subpath = ("assets", "js", "staticman_comments.js")
        src = os.path.join(os.path.dirname(__file__), "files", *subpath)
        dst = os.path.join(self.site.config['OUTPUT_FOLDER'], *subpath)
        dst_dir = os.path.dirname(dst)
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, dst)



    def set_site(self, site):
        """Set Nikola site object."""
        super().set_site(site)
        # site._GLOBAL_CONTEXT['site_has_static_comments'] = True
        blinker.signal("scanned").connect(self._process_comments_for_posts_and_pages)

