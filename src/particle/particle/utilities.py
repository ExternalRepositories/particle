# -*- coding: utf-8 -*-
# Copyright (c) 2018-2021, Eduardo Rodrigues and Henry Schreiner.
#
# Distributed under the 3-clause BSD license, see accompanying file LICENSE
# or https://github.com/scikit-hep/particle for details.

import math
import re
import sys
import unicodedata
from typing import Optional


def programmatic_name(name):
    # type: (str) -> str
    "Return a name safe to use as a variable name."
    name = re.sub("0$", "_0", name)
    # Deal first with antiparticles of sparticles, e.g. "~d(R)~" antiparticle of "~d(R)"
    name = re.sub("^~", "tilde_", name)
    # The remaining "~" now always means it's an antiparticle
    name = name if "~" not in name else "".join(name.split("~")) + "_bar"
    name = (
        name.replace(")(", "_")
        .replace("(", "_")
        .replace(")", "")
        .replace("*", "st")
        .replace("'", "p")
        .replace("::", "_")
        .replace("/", "")
        .replace("--", "_mm")
        .replace("++", "_pp")
        .replace("-", "_minus")
        .replace("+", "_plus")
    )
    # Strip off the ugly "_" at beginning of a name, such as when dealing with name="(bs)(0)""
    return name.lstrip("_")


def str_with_unc(value, upper, lower=None):
    # type: (float, Optional[float], Optional[float]) -> str
    """
    Utility to print out an uncertainty with different or
    identical upper/lower bounds. Nicely formats numbers using PDG rule.
    """

    # If no errors are available, simply return the value alone
    if upper is None:
        return str(value)

    # If no lower passed, make them the same
    if lower is None:
        lower = upper

    # Uncertainties are always positive
    upper = abs(upper)
    lower = abs(lower)

    error = min(upper, lower)

    if error == 0:
        return str(value)

    value_digits = int(math.floor(math.log10(value)))
    error_digits = int(math.floor(math.log10(error) - math.log10(2.5)))
    # This is split based on the value being larger than 1000000 or smaller than 0.001 - scientific notation split

    # This is normal notation
    if -3 < value_digits < 6:
        if error_digits < 0:
            fsv = fse = ".{}f".format(-error_digits)
        else:
            fsv = fse = ".0f"

    # This is scientific notation - a little odd, but better than the other options.
    else:
        fsv = ".{}e".format(abs(error_digits - value_digits))
        pure_error_digits = int(math.floor(math.log10(error)))

        fse = ".0e" if error_digits == pure_error_digits else ".1e"

    # Now, print values based on upper=lower being true or not (even if they print the same)
    if upper != lower:
        return "{value:{fsv}} + {upper:{fse}} - {lower:{fse}}".format(
            value=value, upper=upper, lower=lower, fsv=fsv, fse=fse
        )

    # Only bother with unicode if this is Python 3.
    pm = u"±" if sys.version_info >= (3,) else "+/-"

    return "{value:{fsv}} {pm} {upper:{fse}}".format(
        value=value, pm=pm, upper=upper, fsv=fsv, fse=fse
    )


# List of greek letter names as used in Unicode (see unicodedata package)
_list_name_greek_letters = [
    "Alpha",
    "Beta",
    "Chi",
    "Delta",
    "Epsilon",
    "Eta",
    "Gamma",
    "Iota",
    "Kappa",
    "Lamda",  # Unicodedata library uses "lamda" for "lambda" :S!
    "Lambda",
    "Mu",
    "Nu",
    "Omega",
    "Omicron",
    "Phi",
    "Pi",
    "Psi",
    "Rho",
    "Sigma",
    "Tau",
    "Theta",
    "Upsilon",
    "Xi",
    "Zeta",
]
_list_name_greek_letters += [item.lower() for item in _list_name_greek_letters]


def greek_letter_name_to_unicode(letter):
    # type: (str) -> str
    """
    Return a greek letter name as a Unicode character,
    the same as the input if no match is found.

    Examples
    --------
    Lamda -> Λ    (Unicodedata library uses "lamda" for "lambda" :S!)
    Omega -> Ω
    omega -> ω
    """
    try:
        return unicodedata.lookup(
            "GREEK {case} LETTER {name}".format(
                case="SMALL" if letter == letter.lower() else "CAPITAL",
                name=letter.upper(),
            )
        )
    except KeyError:  # Unicodedata library uses "lamda" for "lambda", so that's an obvious miss
        return letter


def latex_name_unicode(name):
    # type: (str) -> str
    r"""
    Convert in particle names in LaTeX all greek letters by their unicode.

    Examples
    --------
    >>> from particle import Particle
    >>> n = Particle.from_pdgid(3124).latex_name
    >>> print(n)
    \Lambda(1520)
    >>> latex_name_unicode(n)
    'Λ(1520)'
    """
    # Make sure "Lambda" and "lambda" are naturally deal with given that the
    # unicodedata library uses "lamda" for "lambda" :S!
    if "ambda" in name:
        name = name.replace("ambda", "amda")
    for gl in _list_name_greek_letters:
        name = name.replace(r"\{}".format(gl), greek_letter_name_to_unicode(gl))
    return name


def latex_to_html_name(name):
    # type:(str) -> str
    """Conversion of particle names from LaTeX to HTML."""
    name = re.sub(r"\^\{(.*?)\}", r"<SUP>\1</SUP>", name)
    name = re.sub(r"\_\{(.*?)\}", r"<SUB>\1</SUB>", name)
    name = re.sub(r"\\prime(.*?)", r"&#8242;", name)
    name = re.sub(r"\\mathrm\{(.*?)\}", r"\1", name)
    name = re.sub(r"\\left\[(.*?)\\right\]", r"[\1] ", name)
    for gl in _list_name_greek_letters:
        name = name.replace(r"\%s" % gl, "&%s;" % gl)
    name = re.sub(r"\\tilde\{(.*?)\}", r"\1&#771;", name)
    name = re.sub(r"\\overline\{(.*?)\}", r"\1&#773;", name)
    name = re.sub(r"\\bar\{(.*?)\}", r"\1&#773;", name)
    return name
