from distutils.core import setup

setup(name='ogent-COVID19',
      version='1.0',
      description='Some data analysis on COVID19',
      author='Oliver Gent',
      author_email='github.com/o-gent',
      url='https://www.github.com/o-gent',
      packages=[
          'flask', 
          'bokeh', 
          'numpy', 
          'pandas',
          'matplotlib',
          'waitress'
          ],
     )