.. Dev Forum documentation master file

Welcome to Dev Forum's documentation!
====================================

Dev Forum is a comprehensive community forum for developers to discuss and share knowledge about various programming topics. This platform provides a structured environment for technical discussions, knowledge sharing, and community building among developers.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Application Overview
===================

Dev Forum is a Flask-based web application that provides the following features:

* User registration and authentication
* Forum categories, topics, and posts
* Comments on posts
* Private messaging between users
* Admin dashboard for forum management
* Search functionality
* Code snippet formatting with syntax highlighting

Database Models
==============

The application uses SQLAlchemy ORM with the following models:

* User: Represents forum members
* Category: Represents forum sections
* Topic: Represents discussion threads
* Post: Represents individual messages in a topic
* Comment: Represents responses to posts
* Message: Represents private communications between users

API Documentation
===============

.. automodule:: app
   :members:
   :undoc-members:
   :show-inheritance: