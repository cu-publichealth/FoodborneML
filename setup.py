from distutils.core import setup
setup(name='pyhealth',
      version='0.1',
      description='Python DOHMH Foodborne Illness Software',
      author='Tom Effland',
      author_email='teffland@cs.columbia.edu',
      #url='',
      packages=['pyhealth', 
                'pyhealth.models',
                'pyhealth.sources',
                'pyhealth.pipelines',
                'pyhealth.pipes',
                'pyhealth.util',
                'pyhealth.methods',
                'pyhealth.experiments',
                'pyhealth.deployment'
               ],
      )
