# -*- coding: utf-8 -*-
# Version: 1.0.0
# Description: VIRAG's creamy RFdiffusion-like protein colour spectrum.
"""VIRAG RF Cream Spectrum -- a single-file PyMOL plugin.

INSTALL
    Plugin > Plugin Manager > Install New Plugin > Choose file...
    Select this file. Enable its startup/autoload option if needed.

    For installation from a website, host this unchanged file at a public
    HTTPS URL ending in /rf_spectrum.py. Paste that direct file URL into
    "Install from PyMOLWiki or any URL" and click Fetch.

USE (PyMOL command line)
    rf_spectrum
    rf_spectrum my_protein
    rf_spectrum sele
    rf_spectrum my_protein, per_chain=0
    rf_spectrum my_protein, reverse=1
    help rf_spectrum

    The Plugin menu also contains "VIRAG RF Cream Spectrum...".
    Alternatively, load this as a script with: run /path/to/rf_spectrum.py

BEHAVIOUR
    Uses the six original VIRAG pastel RGB stops, rf1 through rf6.
    Colours only selected protein atoms. Each selected residue receives
    one colour, interpolated in RGB through the six stops. Residues follow
    PyMOL's atom traversal order; insertion codes and segments are retained.
    The default restarts the gradient for each object/chain combination.
    With per_chain=0, one gradient spans all selected protein residues.
    A one-residue group receives the first colour (last when reversed).

    Makes selected cartoons follow atom colours and enables smooth cartoon
    colour transitions for affected objects. Coordinates, B factors,
    occupancies, representation visibility, and lighting are not changed.

    The palette is RFdiffusion-inspired; it is the custom VIRAG palette.
    No dependencies beyond PyMOL and Python's standard library are needed.
"""

from collections import OrderedDict
from math import gcd

from pymol import CmdException, cmd

__version__ = "1.0.0"

RF_PALETTE = (
    (0.60, 0.67, 0.92),  # rf1: periwinkle
    (0.67, 0.70, 0.90),  # rf2: soft lavender-blue
    (0.74, 0.70, 0.87),  # rf3: lavender
    (0.81, 0.69, 0.83),  # rf4: mauve
    (0.88, 0.68, 0.79),  # rf5: dusty pink
    (0.93, 0.70, 0.76),  # rf6: soft pink
)


def _register_colours(_self=cmd):
    for i, rgb in enumerate(RF_PALETTE, 1):
        _self.set_color("rf%d" % i, rgb, quiet=1)


def _flag(value, name):
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on"):
        return True
    if text in ("0", "false", "no", "off"):
        return False
    raise CmdException("%s must be 0 or 1" % name)


def _colour_index(numerator, denominator, cache, _self):
    divisor = gcd(numerator, denominator)
    numerator, denominator = numerator // divisor, denominator // divisor
    key = (numerator, denominator)
    if key not in cache:
        interval, remainder = divmod(5 * numerator, denominator)
        if remainder == 0:
            name = "rf%d" % (interval + 1)
        else:
            fraction = remainder / float(denominator)
            left, right = RF_PALETTE[interval:interval + 2]
            rgb = tuple(a + fraction * (b - a) for a, b in zip(left, right))
            name = "virag_rf_%d_%d" % key
            _self.set_color(name, rgb, quiet=1)
        cache[key] = _self.get_color_index(name)
    return cache[key]


def rf_spectrum(selection="all", per_chain=1, reverse=0, quiet=0, _self=cmd):
    """
DESCRIPTION
    Apply VIRAG's creamy periwinkle-to-pink spectrum to protein atoms.

USAGE
    rf_spectrum [selection [, per_chain [, reverse [, quiet]]]]

ARGUMENTS
    selection = PyMOL selection or object name {default: all}
    per_chain = 1: restart for each object/chain; 0: one shared gradient
    reverse = 1: pink to periwinkle; 0: periwinkle to pink
    quiet = 1: suppress the completion message

EXAMPLES
    rf_spectrum
    rf_spectrum my_protein
    rf_spectrum chain A and resi 10-80
    rf_spectrum my_protein, per_chain=0
    rf_spectrum my_protein, reverse=1

NOTES
    Colours only protein atoms inside the selection, with one colour per
    selected residue. Ligands and solvent are excluded. Residues are ordered
    as encountered by PyMOL, including insertion codes. B factors and
    occupancies are preserved. Returns the number of coloured residues.
    """
    per_chain = _flag(per_chain, "per_chain")
    reverse = _flag(reverse, "reverse")
    quiet = _flag(quiet, "quiet")
    expression = "(%s) and polymer.protein" % (str(selection).strip() or "all")
    target = _self.get_unused_name("_virag_rf_selection")
    try:
        # Snapshot selections such as `color red` before atom colours change.
        _self.select(target, expression, enable=0, quiet=1)
        return _apply_spectrum(target, per_chain, reverse, quiet, _self)
    finally:
        _self.delete(target)


def _apply_spectrum(target, per_chain, reverse, quiet, _self):
    rows = []
    _self.iterate(
        target,
        "rows.append((model, index, segi, chain, resi))",
        space={"rows": rows},
    )
    if not rows:
        raise CmdException("rf_spectrum: the selection contains no protein atoms")

    groups = OrderedDict()
    for model, index, segi, chain, resi in rows:
        group_key = (model, chain) if per_chain else None
        residues = groups.setdefault(group_key, OrderedDict())
        residue_key = (model, segi, chain, resi)
        residues.setdefault(residue_key, []).append((model, index))

    _register_colours(_self)
    colour_cache, atom_colours = {}, {}
    residue_count = 0
    for residues in groups.values():
        denominator = max(len(residues) - 1, 1)
        for ordinal, atom_keys in enumerate(residues.values()):
            numerator = denominator - ordinal if reverse else ordinal
            colour = _colour_index(numerator, denominator, colour_cache, _self)
            for atom_key in atom_keys:
                atom_colours[atom_key] = colour
        residue_count += len(residues)

    # Assign colour directly: custom-list cmd.spectrum can ignore byres=1.
    _self.alter(
        target,
        "color = atom_colours[(model, index)]",
        space={"atom_colours": atom_colours},
        quiet=1,
    )
    _self.set("cartoon_color", -1, target, quiet=1)
    # This setting belongs to an object, not to individual atoms.
    for model in dict.fromkeys(row[0] for row in rows):
        _self.set("cartoon_discrete_colors", 0, model, quiet=1)
    _self.rebuild(target)
    if not quiet:
        print("rf_spectrum: coloured %d residues in %d gradient(s)."
              % (residue_count, len(groups)))
    return residue_count


def _open_dialog():
    from pymol.Qt import QtWidgets

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("VIRAG RF Cream Spectrum")
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.addWidget(QtWidgets.QLabel("Protein object or selection:"))
    default = "sele" if "sele" in cmd.get_names("selections") else "all"
    selection = QtWidgets.QLineEdit(default)
    layout.addWidget(selection)
    per_chain = QtWidgets.QCheckBox("Restart the gradient for each chain")
    per_chain.setChecked(True)
    layout.addWidget(per_chain)
    reverse = QtWidgets.QCheckBox("Reverse: pink to periwinkle")
    layout.addWidget(reverse)
    apply_button = QtWidgets.QPushButton("Apply")
    close_button = QtWidgets.QPushButton("Close")
    buttons = QtWidgets.QHBoxLayout()
    buttons.addWidget(apply_button)
    buttons.addWidget(close_button)
    layout.addLayout(buttons)

    def apply():
        try:
            rf_spectrum(selection.text(), per_chain.isChecked(), reverse.isChecked())
        except CmdException as error:
            QtWidgets.QMessageBox.warning(dialog, "RF Cream Spectrum", str(error))

    apply_button.clicked.connect(apply)
    close_button.clicked.connect(dialog.accept)
    # Modal execution keeps the dialog alive; PyMOL's Qt wrapper handles bindings.
    if hasattr(dialog, "exec"):
        dialog.exec()
    else:
        dialog.exec_()


def __init_plugin__(app=None):
    from pymol.plugins import addmenuitemqt
    addmenuitemqt("VIRAG RF Cream Spectrum...", _open_dialog)


# Register on import so both installed plugins and `run rf_spectrum.py` work.
_register_colours()
cmd.extend("rf_spectrum", rf_spectrum)
