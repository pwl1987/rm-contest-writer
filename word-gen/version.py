#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version info for rm-contest-writer
"""

__version__ = '1.1.0'
__author__ = '临沂市融媒体中心'
__skill_name__ = 'rm-contest-writer'

FEATURES = [
    'description-driven-mockup',
    'user-uploaded-images',
    'gate-validation',
    'gb9704-compliance',
    '3-track-support',
]

def print_version():
    print(f'rm-contest-writer v{__version__}')
    print(f'Skill: {__skill_name__}')
    print(f'Features: {", ".join(FEATURES)}')

if __name__ == '__main__':
    print_version()
