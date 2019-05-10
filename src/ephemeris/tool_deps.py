#!/usr/bin/env python
'''Tool to install tool dependencies on a Galaxy instance.'''
import argparse
import os
import xml.etree.ElementTree as ET

from bioblend.galaxy.tools import ToolClient

from ephemeris import get_galaxy_connection
from ephemeris.common_parser import get_common_args


def _parser():
    parent = get_common_args()
    parser = argparse.ArgumentParser(parents=[parent])
    parser.add_argument("-t", "--tool", help='Path to a tool file or tool_conf file')
    parser.add_argument("-i", "--id", help='Comma seperated list of tool ids')

    return parser


def main():
    """
        This script uses bioblend to trigger dependencies installations for the provided tools
    """
    args = _parser().parse_args()
    gi = get_galaxy_connection(args)
    tool_client = ToolClient(gi)

    if 'tool' in args:
        # install all
        root = ET.ElementTree(file=args.tool).getroot()
        if root.tag == "toolbox":
            # Install all from tool_conf
            tool_path = root.get('tool_path', '')
            tool_path.replace('${tool_conf_dir}', os.path.abspath(args.tool))
            for tool in root.findall("tool[@file]"):
                tool_id = ET.ElementTree(file=tool.get('file')).getroot().get('id')
                if tool_id:
                    tool_client.install_dependencies(tool_id)
        elif root.tag == "tool" and root.get('id'):
            # Install from single tool file
            tool_client.install_dependencies(root.get('id'))

    if 'id' in args:
        for tool_id in args.id.split(','):  # type: str
            tool_client.install_dependencies(tool_id.strip())


if __name__ == '__main__':
    main()
