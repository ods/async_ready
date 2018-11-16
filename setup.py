from setuptools import setup


if __name__ == "__main__":
    setup(
        name='async_ready',
        version='1.1.0',
        description='Primitives to simplify writing code that works in both '
                    'sync and async environments',
        license='MIT license',
        python_requires='>=3.6',
        py_modules=['async_ready'],
    )
