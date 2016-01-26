from distutils.core import setup
setup(name='foodbornenyc',
      version='0.1',
      description='Python DOHMH Foodborne Illness Software',
      author='Tom Effland',
      author_email='teffland@cs.columbia.edu',
      #url='',
      packages=['foodbornenyc', 
                'foodbornenyc.models',
                'foodbornenyc.sources',
                'foodbornenyc.pipelines',
                'foodbornenyc.pipes',
                'foodbornenyc.util',
                'foodbornenyc.methods',
                'foodbornenyc.experiments',
                'foodbornenyc.deployment'
               ],
      )
