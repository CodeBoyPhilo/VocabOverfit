from setuptools import setup, find_packages


setup(
    name='toolkit',
    version='1.0.0',
    packages=find_packages(),
    package_data={'censoring': ['VocabCloud/built-in-data/*']},
    include_package_data=True,
    author='Philo Wu',
    install_requires=[
        'dgl==2.0.0',
        'numpy==1.24.1',
        'pandas==2.1.4',
        'scikit_learn==1.3.2',
        'torch==2.0.0',
        'tqdm==4.66.1',
        'transformers==4.31.0',
    ]
)
