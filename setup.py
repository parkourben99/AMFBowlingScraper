from setuptools import setup

setup(name='AMFBowlingScraper',
      version='0.1',
      description='AMF Bowling Scraper',
      url='http://github.com/parkourben99/AMFBowlingScraper',
      author='Benjamin Ayles',
      author_email='ben@ayles.com.au',
      license='MIT',
      install_requires=[
          'python-dotenv',
          'requests'
      ],
      zip_safe=False)