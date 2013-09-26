
from os.path import abspath, dirname, join
from ansi2html import Ansi2HTMLConverter
from ansi2html.converter import main, \
    ANSI_VISIBILITY_ON, ANSI_VISIBILITY_OFF, \
    ANSI_BLINK_SLOW, ANSI_BLINK_FAST, ANSI_BLINK_OFF, \
    ANSI_NEGATIVE_ON, ANSI_NEGATIVE_OFF, \
    ANSI_INTENSITY_INCREASED, ANSI_INTENSITY_REDUCED, ANSI_INTENSITY_NORMAL
from ansi2html.util import read_to_unicode

from mock import patch
from nose.tools import eq_

import cgi
import unittest
import six
import textwrap

_here = dirname(abspath(__file__))


class TestAnsi2HTML(unittest.TestCase):

    def test_linkify(self):
        ansi = "http://threebean.org"
        target = '<a href="http://threebean.org">http://threebean.org</a>'
        html = Ansi2HTMLConverter(linkify=True).convert(ansi)
        assert(target in html)

    def test_not_linkify(self):
        ansi = "http://threebean.org"
        target = '<a href="http://threebean.org">http://threebean.org</a>'
        html = Ansi2HTMLConverter().convert(ansi)
        assert(target not in html)

    def test_conversion(self):
        with open(join(_here, "ansicolor.txt"), "rb") as input:
            test_data = "".join(read_to_unicode(input))

        with open(join(_here, "ansicolor.html"), "rb") as output:
            expected_data = read_to_unicode(output)

        html = Ansi2HTMLConverter().convert(test_data).split("\n")

        eq_(len(html), len(expected_data))

        for idx in range(len(expected_data)):
            expected = expected_data[idx].strip()
            actual = html[idx].strip()
            self.assertEqual(expected, actual)

    @patch("sys.argv", new_callable=lambda: ["ansi2html"])
    @patch("sys.stdout", new_callable=six.StringIO)
    def test_conversion_as_command(self, mock_stdout, mock_argv):
        with open(join(_here, "ansicolor.txt"), "rb") as input:
            test_data = "".join(read_to_unicode(input))

        with open(join(_here, "ansicolor.html"), "rb") as output:
            expected_data = "".join(read_to_unicode(output))

        if six.PY3:
            f = lambda: six.StringIO(test_data)
        else:
            f = lambda: six.StringIO(test_data.encode('utf-8'))

        with patch("sys.stdin", new_callable=f):
            main()

        html = mock_stdout.getvalue()

        eq_(len(html), len(expected_data), "Strings are not the same length.")
        eq_(html, expected_data, "Strings are not the same.")

    def test_unicode(self):
        """ Ensure that the converter returns unicode(py2)/str(py3) objs. """

        with open(join(_here, "ansicolor.txt"), "rb") as input:
            test_data = "".join(read_to_unicode(input))

        html = Ansi2HTMLConverter().convert(test_data).split("\n")

        for chunk in html:
            assert isinstance(chunk, six.text_type)

    @patch("sys.argv", new_callable=lambda: ["ansi2html", "--inline"])
    @patch("sys.stdout", new_callable=six.StringIO)
    def test_inline_as_command(self, mock_stdout, mock_argv):
        test_input = textwrap.dedent(six.u("""
        this is
        a test
        """))

        with patch("sys.stdin", new_callable=lambda: six.StringIO(test_input)):
            main()

        eq_(mock_stdout.getvalue(), test_input)

    @patch("sys.argv", new_callable=lambda: ["ansi2html", "--partial"])
    @patch("sys.stdout", new_callable=six.StringIO)
    def test_partial_as_command(self, mock_stdout, mock_argv):
        rainbow = '\x1b[1m\x1b[40m\x1b[31mr\x1b[32ma\x1b[33mi\x1b[34mn\x1b[35mb\x1b[36mo\x1b[37mw\x1b[0m\n'
        with patch("sys.stdin", new_callable=lambda: six.StringIO(rainbow)):
            main()

        html = mock_stdout.getvalue().strip()

        if hasattr(html, 'decode'):
            html = html.decode('utf-8')

        expected = (six.u('<span class="ansi1"></span>') +
                    six.u('<span class="ansi1 ansi40"></span>') +
                    six.u('<span class="ansi1 ansi31 ansi40">r</span>') +
                    six.u('<span class="ansi1 ansi32 ansi40">a</span>') +
                    six.u('<span class="ansi1 ansi33 ansi40">i</span>') +
                    six.u('<span class="ansi1 ansi34 ansi40">n</span>') +
                    six.u('<span class="ansi1 ansi35 ansi40">b</span>') +
                    six.u('<span class="ansi1 ansi36 ansi40">o</span>') +
                    six.u('<span class="ansi1 ansi37 ansi40">w</span>'))
        assert isinstance(html, six.text_type)
        assert isinstance(expected, six.text_type)
        self.assertEqual(expected, html)

    def test_partial(self):
        rainbow = '\x1b[1m\x1b[40m\x1b[31mr\x1b[32ma\x1b[33mi\x1b[34mn\x1b[35mb\x1b[36mo\x1b[37mw\x1b[0m\n'

        html = Ansi2HTMLConverter().convert(rainbow, full=False).strip()
        expected = (six.u('<span class="ansi1"></span>') +
                    six.u('<span class="ansi1 ansi40"></span>') +
                    six.u('<span class="ansi1 ansi31 ansi40">r</span>') +
                    six.u('<span class="ansi1 ansi32 ansi40">a</span>') +
                    six.u('<span class="ansi1 ansi33 ansi40">i</span>') +
                    six.u('<span class="ansi1 ansi34 ansi40">n</span>') +
                    six.u('<span class="ansi1 ansi35 ansi40">b</span>') +
                    six.u('<span class="ansi1 ansi36 ansi40">o</span>') +
                    six.u('<span class="ansi1 ansi37 ansi40">w</span>'))
        self.assertEqual(expected, html)

    def test_inline(self):

        rainbow = '\x1b[1m\x1b[40m\x1b[31mr\x1b[32ma\x1b[33mi\x1b[34mn\x1b[35mb\x1b[36mo\x1b[37mw\x1b[0m'

        html = Ansi2HTMLConverter(inline=True).convert(rainbow, full=False)
        expected = (six.u('<span style="font-weight: bold"></span>') +
                    six.u('<span style="font-weight: bold; background-color: #000316"></span>') +
                    six.u('<span style="font-weight: bold; color: #aa0000; background-color: #000316">r</span>') +
                    six.u('<span style="font-weight: bold; color: #00aa00; background-color: #000316">a</span>') +
                    six.u('<span style="font-weight: bold; color: #aa5500; background-color: #000316">i</span>') +
                    six.u('<span style="font-weight: bold; color: #0000aa; background-color: #000316">n</span>') +
                    six.u('<span style="font-weight: bold; color: #E850A8; background-color: #000316">b</span>') +
                    six.u('<span style="font-weight: bold; color: #00aaaa; background-color: #000316">o</span>') +
                    six.u('<span style="font-weight: bold; color: #F5F1DE; background-color: #000316">w</span>'))

        self.assertEqual(expected, html)

    def test_produce_headers(self):
        conv = Ansi2HTMLConverter()
        headers = conv.produce_headers().split("\n")

        inputfile = join(_here, "produce_headers.txt")
        with open(inputfile, "rb") as produce_headers:
            expected_data = read_to_unicode(produce_headers)

        for idx in range(len(expected_data)):
            expected = expected_data[idx].strip()
            actual = headers[idx].strip()
            self.assertEqual(expected, actual)

    def test_escaped_implicit(self):
        test = "<p>awesome</p>"
        expected = "&lt;p&gt;awesome&lt;/p&gt;"
        html = Ansi2HTMLConverter().convert(test, full=False)
        self.assertEqual(expected, html)

    def test_escaped_explicit(self):
        test = "<p>awesome</p>"
        expected = "&lt;p&gt;awesome&lt;/p&gt;"
        html = Ansi2HTMLConverter(escaped=True).convert(test, full=False)
        self.assertEqual(expected, html)

    def test_unescaped(self):
        test = "<p>awesome</p>"
        expected = "<p>awesome</p>"
        html = Ansi2HTMLConverter(escaped=False).convert(test, full=False)
        self.assertEqual(expected, html)

    def test_markup_lines(self):
        test = "  wat  \n "
        expected = '<span id="line-0">  wat  </span>\n<span id="line-1"> </span>'
        html = Ansi2HTMLConverter(markup_lines=True).convert(test, full=False)
        self.assertEqual(expected, html)

    def test_no_markup_lines(self):
        test = "  wat  \n "
        expected = test
        html = Ansi2HTMLConverter().convert(test, full=False)
        self.assertEqual(expected, html)

    def test_issue_25(self):
        sample = '\x1b[0;38;5;238;48;5;231mTEXT\x1b[0m'

        html = Ansi2HTMLConverter(inline=False).convert(sample, full=False)
        expected = six.u('<span class="ansi38-238 ansi48-231">TEXT</span>')

        self.assertEqual(expected, html)

    def test_italic(self):
        sample = '\x1b[3mITALIC\x1b[0m'

        html = Ansi2HTMLConverter(inline=True).convert(sample, full=False)
        expected = six.u('<span style="font-style: italic">ITALIC</span>')

        self.assertEqual(expected, html)

    def test_hidden_text(self):
        sample = '\x1b[%dmHIDDEN\x1b[%dmVISIBLE\x1b[0m' % (ANSI_VISIBILITY_OFF, ANSI_VISIBILITY_ON)

        html = Ansi2HTMLConverter(inline=True).convert(sample, full=False)
        expected = six.u('<span style="visibility: hidden">HIDDEN</span>VISIBLE')

        self.assertEqual(expected, html)

    def test_lighter_text(self):
        sample = 'NORMAL\x1b[%dmLIGHTER\x1b[%dmBOLD\x1b[%dmNORMAL' % (ANSI_INTENSITY_REDUCED, ANSI_INTENSITY_INCREASED, ANSI_INTENSITY_NORMAL)

        html = Ansi2HTMLConverter(inline=True).convert(sample, full=False)
        expected = six.u('NORMAL<span style="font-weight: lighter">LIGHTER</span><span style="font-weight: bold">BOLD</span>NORMAL')

        self.assertEqual(expected, html)

    def test_blinking_text(self):
        sample = '\x1b[%dm555\x1b[%dm666\x1b[%dmNOBLINK\x1b[0m' % (ANSI_BLINK_SLOW, ANSI_BLINK_FAST, ANSI_BLINK_OFF)

        html = Ansi2HTMLConverter(inline=True).convert(sample, full=False)
        expected = six.u('<span style="text-decoration: blink">555</span><span style="text-decoration: blink">666</span>NOBLINK')
        self.assertEqual(expected, html)

        html = Ansi2HTMLConverter(inline=False).convert(sample, full=False)
        expected = six.u('<span class="ansi5">555</span><span class="ansi6">666</span>NOBLINK')
        self.assertEqual(expected, html)

    def test_inverse_text(self):
        sample = 'NORMAL\x1b[%dmINVERSE\x1b[%dmNORMAL\x1b[0m' % (ANSI_NEGATIVE_ON, ANSI_NEGATIVE_OFF)
        html = Ansi2HTMLConverter(inline=False).convert(sample, full=False)
        expected = six.u('NORMAL<span class="inv_background inv_foreground">INVERSE</span>NORMAL')
        self.assertEqual(expected, html)

        sample = 'NORMAL\x1b[%dm303030\x1b[%dm!30!30!30\x1b[%dm303030\x1b[0m' % (30, ANSI_NEGATIVE_ON, ANSI_NEGATIVE_OFF)
        html = Ansi2HTMLConverter(inline=False).convert(sample, full=False)
        expected = six.u('NORMAL<span class="ansi30">303030</span><span class="inv30 inv_foreground">!30!30!30</span><span class="ansi30">303030</span>')
        self.assertEqual(expected, html)

        sample = 'NORMAL\x1b[%dm313131\x1b[%dm!31!31!31\x1b[%dm!31!43\x1b[%dm31+43\x1b[0mNORMAL' % (31, ANSI_NEGATIVE_ON, 43, ANSI_NEGATIVE_OFF)
        html = Ansi2HTMLConverter(inline=False).convert(sample, full=False)
        expected = six.u('NORMAL<span class="ansi31">313131</span><span class="inv31 inv_foreground">!31!31!31</span><span class="inv31 inv43">!31!43</span><span class="ansi31 ansi43">31+43</span>NORMAL')
        self.assertEqual(expected, html)

if __name__ == '__main__':
    unittest.main()
