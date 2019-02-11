from setuptools import setup

setup(
    name='taxbit-gemini-python',
    version='0.0.1',
    packages=['taxbit_gemini'],
    url='https://github.com/taxbit-open-source/gemini-python',
    license='MIT',
    author='Mohammad Usman',
    author_email='m.t.usman@hotmail.com',
    maintainer='Chris Gunnels',
    maintainer_email='chris@taxbit.com',
    description='A python client for the Gemini API and Websocket',
    python_requires='>=3',
    install_requires=['requests', 'pytest', 'websocket', 'websocket-client'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords=['gemini', 'bitcoin', 'bitcoin-exchange', 'ethereum', 'ether', 'BTC', 'ETH', 'gemini-exchange'],
)
