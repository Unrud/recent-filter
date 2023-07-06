# Copyright 2023 Unrud <unrud@outlook.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import re
from typing import Optional


class Pattern:
    negate: bool

    def __init__(self, pattern: str, negate: bool, source: str):
        self._pattern = pattern
        self.negate = negate
        self._source = source
        self._compiled = re.compile(pattern, flags=re.DOTALL)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}[{self._source!r} => '
                f'{"!" if self.negate else ""}{self._pattern!r}]')

    def __call__(self, s: str) -> bool:
        return self._compiled.match(s) is not None


def escape(s: str) -> str:
    if not s:
        raise ValueError('input must not be empty')
    return re.sub(r'(^[!#]|[\[\\?*]| $)', r'\\\1', s)


def convert_to_re(input: str) -> Optional[Pattern]:
    def consume(quote=True):
        nonlocal input
        while input:
            value, input = input[:1], input[1:]
            quoted = quote and value == '\\'
            if quoted:
                value, input = input[:1], input[1:]
            yield value, quoted
    if '\n' in input:
        raise ValueError('input must contain single line')
    orig_source = input
    output = r''
    negate = False
    for i, (char, quoted) in enumerate(consume()):
        if not char:
            return None
        if i == 0 and not quoted and char == '#':
            return None
        if not input.lstrip(' '):
            input = ''
        if not quoted and char == ' ' and not input:
            break
        if not quoted and char == '!':
            negate = True
            continue
        if char == '/':
            output += r'/'
            if not output.startswith(r'/') and input:
                output = rf'/{output}'
            if input[:3] in ('**', '**/'):
                while input[:3] in ('**', '**/'):
                    last_input = input
                    input = input[3:]
                if last_input == '**/':
                    output += '.*/'
                else:
                    output += r'(?:.*/)?'
            continue
        if not quoted and char == '*':
            if not output and (char + input[:2]) in ('**', '**/'):
                output += r'/'
                last_input = char + input
                input = input[2:]
                while input[:3] in ('**', '**/'):
                    last_input = input
                    input = input[3:]
                if last_input == '**/':
                    output += '.*/'
                else:
                    output += r'(?:.*/)?'
            else:
                output += r'[^/]*'
                while input[:1] == '*':
                    input = input[1:]
            continue
        if not quoted and char == '?':
            output += r'[^/]'
        elif not quoted and char == '[':
            negate_class = False
            range_start = None
            in_range = False
            class_output = r''
            for i, (char, _) in enumerate(consume(quote=False)):
                if i > (1 if negate_class else 0) and char == ']':
                    break
                if i == 0 and char == '!':
                    negate_class = True
                    continue
                if negate_class and not class_output:
                    class_output += r'^/'
                if in_range:
                    range_end = max(range_start, char)
                    if range_start <= '/' and '/' <= range_end:
                        if range_start != '/':
                            range_half_end = chr(ord('/') - 1)
                            class_output += re.escape(range_start)
                            if range_start != range_half_end:
                                class_output += \
                                    rf'-{re.escape(range_half_end)}'
                        if range_end != '/':
                            range_half_start = chr(ord('/') + 1)
                            class_output += re.escape(range_half_start)
                            if range_half_start != range_end:
                                class_output += rf'-{re.escape(range_end)}'
                    else:
                        class_output += re.escape(range_start)
                        if range_start != range_end:
                            class_output += rf'-{re.escape(range_end)}'
                    range_start = None
                    in_range = False
                elif range_start and char == '-':
                    in_range = True
                else:
                    if range_start and range_start != '/':
                        class_output += re.escape(range_start)
                    range_start = char
            else:
                return None
            if range_start and range_start != '/':
                class_output += re.escape(range_start)
            if in_range:
                class_output += re.escape('-')
            if not class_output:
                return None
            output += rf'[{class_output}]'
        else:
            output += re.escape(char)
        if not input:
            output += r'(?:/|$)'
    if not output:
        return None
    if not output.startswith(r'/'):
        output = rf'/(?:.*/)?{output}'
    return Pattern(output, negate, orig_source)
