import setuptools

setuptools.setup(name='nublar_example_python_flask',
      version='0.1.0',
      description='Nublar - Flask example',
      url='https://github.com/lex00/nublar/python/flask',
      author='Albert Artigues',
      author_email='',
      license='MIT',
      packages=['nublar_example_python_flask'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'flask',
          'requests'
      ],
)
