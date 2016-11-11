#!/usr/bin/env python
# coding=utf-8

#   Copyright (C) 2016 by Serge Poltavski                                 #
#   serge.poltavski@gmail.com                                             #
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 3 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
#   This program is distributed in the hope that it will be useful,       #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#   GNU General Public License for more details.                          #
#                                                                         #
#   You should have received a copy of the GNU General Public License     #
#   along with this program. If not, see <http://www.gnu.org/licenses/>   #
"""
    pddoc.sphinx
    ~~~~~~~~~~~~~~~~~~~

    Allow puredata-formatted graphs to be included in Sphinx-generated
    documents inline.
"""

import posixpath
from os import path
from subprocess import Popen, PIPE
from hashlib import sha1

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList

import sphinx
from sphinx.errors import SphinxError
from sphinx.util.osutil import ensuredir, ENOENT, EPIPE, EINVAL
from sphinx.util.compat import Directive


class PdError(SphinxError):
    category = 'Pd error'


class PdNode(nodes.General, nodes.Inline, nodes.Element):
    pass


def figure_wrapper(directive, node, caption):
    figure_node = nodes.figure('', node)
    if 'align' in node:
        figure_node['align'] = node.attributes.pop('align')

    parsed = nodes.Element()
    directive.state.nested_parse(ViewList([caption], source=''),
                                 directive.content_offset, parsed)
    caption_node = nodes.caption(parsed[0].rawsource, '',
                                 *parsed[0].children)
    caption_node.source = parsed[0].source
    caption_node.line = parsed[0].line
    figure_node += caption_node
    return figure_node


def align_spec(argument):
    return directives.choice(argument, ('left', 'center', 'right'))


class PureData(Directive):
    """
    Directive to insert arbitrary ascii puredata markup.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'caption': directives.unchanged,
    }

    def run(self):
        pd_ascii_code = '\n'.join(self.content)
        if not pd_ascii_code.strip():
            return [self.state_machine.reporter.warning(
                'Ignoring "pd" directive without content.',
                line=self.lineno)]

        node = PdNode()
        node['code'] = pd_ascii_code
        node['options'] = {}
        if 'alt' in self.options:
            node['alt'] = self.options['alt']
        if 'align' in self.options:
            node['align'] = self.options['align']

        caption = self.options.get('caption')
        if caption:
            node = figure_wrapper(self, node, caption)

        return [node]


def render_pd(self, code, options, format, prefix='pd'):
    """Render puredata code into a PNG or PDF output file."""
    pdgraph = options.get('pdascii', self.builder.config.pdgraph)
    hashkey = (code + str(options) +
               str(self.builder.config.pdgraph_args)).encode('utf-8')
    fname = '{0:s}-{1:s}.{2:s}'.format(prefix, sha1(hashkey).hexdigest(), format)
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = path.join(self.builder.outdir, self.builder.imagedir, fname)
    tmp_txt = '{0:s}-{1:s}-pdascii.txt'.format(prefix, sha1(hashkey).hexdigest())
    tmp_path = path.join(self.builder.outdir, self.builder.imagedir, tmp_txt)

    ensuredir(path.dirname(outfn))
    ensuredir(path.dirname(tmp_path))

    if not path.exists(tmp_path):
        f = open(tmp_path, 'w')
        f.writelines(code)
        f.close()
    else:
        if path.isfile(outfn):
            return relfn, outfn

    if hasattr(self.builder, '_pdgraph_warned') and self.builder._pdgraph_warned.get(pdgraph):
        return None, None

    pd_args = [pdgraph]
    pd_args.extend(self.builder.config.pdgraph_args)
    pd_args.extend(['--format', format, tmp_path, outfn])

    try:
        p = Popen(pd_args, stdout=PIPE, stdin=PIPE, stderr=PIPE)
    except OSError as err:
        if err.errno != ENOENT:   # No such file or directory
            raise
        self.builder.warn('pdascii command cannot be run (needed for pd '
                          'output), check the pdgraph setting')
        if not hasattr(self.builder, '_pdgraph_warned'):
            self.builder._pdgraph_warned = {}
        self.builder._pdgraph_warned[pdgraph] = True
        return None, None

    try:
        # resulting in a broken pipe on communicate()
        stdout, stderr = p.communicate(code)
    except (OSError, IOError) as err:
        if err.errno not in (EPIPE, EINVAL):
            raise
        # in this case, read the standard output and standard error streams
        # directly, to get the error message(s)
        stdout, stderr = p.stdout.read(), p.stderr.read()
        p.wait()
    if p.returncode != 0:
        raise PdError('pdascii exited with error:\n[stderr]\n{0:s}\n'
                      '[stdout]\n{0:s}'.format(stderr, stdout))
    if not path.isfile(outfn):
        raise PdError('pdascii did not produce an output file:\n[stderr]\n{0:s}\n'
                      '[stdout]\n{0:s}'.format(stderr, stdout))
    return relfn, outfn


def render_pd_html(self, node, code, options, prefix='puredata', imgcls=None, alt=None):
    format = self.builder.config.pdgraph_format

    try:
        if format not in ('png', 'svg'):
            raise PdError("pdgraph_format must be one of 'png', 'svg', but is {0!r:s}".format(format))
        fname, outfn = render_pd(self, code, options, format, prefix)
    except PdError as exc:
        self.builder.warn('pd code %r: ' % code + str(exc))
        raise nodes.SkipNode

    if fname is None:
        self.body.append(self.encode(code))
    else:
        if alt is None:
            alt = node.get('alt', self.encode(code).strip())
        imgcss = imgcls and 'class="{0:s}"'.format(imgcls) or ''
        if format == 'svg':
            svgtag = '''<object data="{0:s}" type="image/svg+xml">
            <p class="warning">{1:s}</p></object>\n'''.format(fname, alt)
            self.body.append(svgtag)
        else:
            if 'align' in node:
                self.body.append('<div align="{0:s}" class="align-{1:s}">'
                                 .format(node['align'], node['align']))

            self.body.append('<img src="{0:s}" alt="{1:s}" {2:s}/>\n'.format(fname, alt, imgcss))
            if 'align' in node:
                self.body.append('</div>\n')

    raise nodes.SkipNode


def html_visit_pd(self, node):
    render_pd_html(self, node, node['code'], node['options'])


def render_pd_latex(self, node, code, options, prefix='puredata'):
    try:
        fname, outfn = render_pd(self, code, options, 'pdf', prefix)
    except PdError as exc:
        self.builder.warn('pd code %r: ' % code + str(exc))
        raise nodes.SkipNode

    is_inline = self.is_inline(node)
    if is_inline:
        para_separator = ''
    else:
        para_separator = '\n'

    if fname is not None:
        post = None
        if not is_inline and 'align' in node:
            if node['align'] == 'left':
                self.body.append('{')
                post = '\\hspace*{\\fill}}'
            elif node['align'] == 'right':
                self.body.append('{\\hspace*{\\fill}')
                post = '}'
        self.body.append('%s\\includegraphics{%s}%s' %
                         (para_separator, fname, para_separator))
        if post:
            self.body.append(post)

    raise nodes.SkipNode


def latex_visit_graphviz(self, node):
    render_pd_latex(self, node, node['code'], node['options'])


def setup(app):
    app.add_node(PdNode,
                 html=(html_visit_pd, None),
                 latex=(latex_visit_graphviz, None))
    app.add_directive('pd', PureData)
    app.add_config_value('pdgraph', 'pdascii', 'html')
    app.add_config_value('pdgraph_args', [], 'html')
    app.add_config_value('pdgraph_format', 'png', 'html')
    return {'version': sphinx.__display_version__, 'parallel_read_safe': False}
