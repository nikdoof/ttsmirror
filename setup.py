from setuptools import setup

setup(
    name='ttsmirror',
    version='0.1',
    py_modules=['ttsmirror'],
    url='https://github.com/nikdoof/ttsmirror',
    license='MIT',
    author='Andrew Williams',
    author_email='andy@tensixtyone.com',
    description='Parses a TTS JSON save and mirrors assets locally.',
    entry_points={
        "console_scripts": [
            "ttsmirror=ttsmirror:main",
        ],
    },
    install_requires=[
        'todoist-python',
    ]
)
