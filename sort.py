#!/usr/bin/env python3
from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Optional, cast
import os
import networkx as nx
import matplotlib.pyplot as plt


class Mod:
    def __init__(
        self,
        packageid: str,
        before: Optional[list[str]],
        after: Optional[list[str]],
        incompatible: Optional[list[str]],
        path: Optional[str]
    ):
        self.packageid = packageid
        self.before = before
        self.after = after
        self.incompatible = incompatible
        self.path = path

    @staticmethod
    def create_from_path(dirpath) -> Optional[Mod]:
        try:
            tree = ET.parse(os.path.join(dirpath, "About/About.xml"))
            root = tree.getroot()

            try:
                packageid = cast(str, cast(ET.Element, root.find("packageId")).text)
            except AttributeError:
                return None

            def xml_list_grab(element: str) -> Optional[list[str]]:
                try:
                    return cast(
                        Optional[list[str]],
                        [
                            n.text
                            for n in cast(ET.Element, root.find(element)).findall("li")
                        ],
                    )
                except AttributeError:
                    return None

            return Mod(
                packageid,
                xml_list_grab("loadAfter"),
                xml_list_grab("loadBefore"),
                xml_list_grab("incompatibleWith"),
                dirpath,
            )

        except FileNotFoundError as e:
            print(e)
            print(os.path.basename(dirpath) + " is not a mod. Ignoring.")

    def __eq__(self, other):
        if isinstance(other, Mod):
            return self.packageid == other.packageid
        if isinstance(other, str):
            return self.packageid == other
        return NotImplemented

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"pid: {self.packageid}"


class ModFolderReader:
    @staticmethod
    def create_mods_list(path) -> list[Mod]:
        return list(
            filter(
                None,
                map(
                    lambda m: Mod.create_from_path(os.path.join(path, m)),
                    os.listdir(path),
                ),
            )
        )


class Edge:
    def __init__(self, vertex, child):
        self.parent = vertex
        self.child = child


if __name__ == "__main__":
    mods = ModFolderReader.create_mods_list(
        os.path.expanduser("~/apps/rimworld/game/Mods")
    )
    DG = nx.DiGraph()

    for m in mods:
        if m.after:
            for a in m.after:
                if a in mods:
                    DG.add_edge(a, m.packageid)
        if m.before:
            for b in m.before:
                if b in mods:
                    DG.add_edge(m.packageid, b)

    pos = nx.spring_layout(DG, seed=56327, k=0.8, iterations=15)
    nx.draw(
        DG, pos, node_size=100, alpha=0.8, edge_color="r", font_size=8, with_labels=True
    )
    ax = plt.gca()
    ax.margins(0.08)
    plt.show()
