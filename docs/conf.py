# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os     # модуль для работы с файловой системой
import sys    # модуль для работы с системными путями
sys.path.insert(0, os.path.abspath('../'))  # добавляет путь на один уровень выше

project = 'Шашки на PyGame'
copyright = '2025, Команда разработчиков: Матвеев, Мисюченко, Жданова, Овчинникова, Бубнов'
author = 'Команда разработчиков: Матвеев, Мисюченко, Жданова, Овчинникова, Бубнов'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# список расширений Sphinx
extensions = [
    'sphinx.ext.autodoc',   # автоматически извлекает документацию из docstrings
    'sphinx.ext.napoleon',  # понимает Google Style и NumPy Style docstrings
]

templates_path = ['_templates']  # путь к пользовательским шаблонам HTML
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']  # файлы и папки, которые Sphinx будет игнорировать

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # тема оформления
html_static_path = ['_static']
