Overview
========

Memini helps teachers and students to manage vocabulary tables and generate training or test sheets.

`License <https://gitlab.com/nicolas.hainaux/memini/blob/dev/LICENSE>`__

Install
=======

OS requirement: Linux, FreeBSD or Windows.

Ubuntu package
--------------
Yet to be built.

Using pip
---------
The required python version to use Memini is python>=3.6.
You'll need to install it if it's not already on your system.

::

    $ pip3 install memini


Workflow
========

.. image:: pics/workflow.svg

Mini tutorial
=============

Say you want to learn a series of german verbs.
You'll need to have a list of your words and translations. Either you copy it or type it yourself (you'll be able to enrich your list later, if need be). For instance, you have a list typed as:

::

  sein	to be
  werden	to become
  haben	to have
  können	to can, to be able to
  müssen	to must, to have to
  geben	to give
  sollen	to should, to ought
  sagen	to say
  wollen	to want
  kommen	to come
  gehen	to go, to walk
  machen	to do
  stehen	to stand
  sehen	to see
  finden	to find
  bleiben	to stay
  liegen	to lie
  stellen	to put
  nehmen	to take
  dürfen	to be allowed
  bringen	to bring
  halten	to hold
  spielen	to play
  heißen	to be called
  wissen	to know

in a text file named "german_verbs.txt".

Each line of the list needs to contain data formatted in the same way, for instance here there's a german verb, then a separator (this is a tab, but it could be anything else, like a semicolon), then the english translation.

First, create a table named "german_verbs" using this list, this way:

.. code:: sh

  memini create german_verbs german_verbs.txt "<German>\t<English>"

This instructs ``memini`` to create a table named ``german_verbs`` and fill it with the data parsed from the file ``german_verbs.txt`` using the pattern ``<German>\t<English>``. This pattern tells that two data must be found on each line, the first one will be in the column named ``<German>``, the second one in the ``<English>`` column. Between these two labels, the separator is written. Here this is a tab character (``\t``) but if you use a semicolon, for instance, you write: ``<German>:<English>`` instead.

You can check the table has been created

.. code:: sh

  $ memini list tables
  german_verbs


And also check its content:

.. code:: sh

  $ memini show german_verbs
   id |  German |        English
  ----+---------+-----------------------
    1 |   sein  |         to be
    2 |  werden |       to become
    3 |  haben  |        to have
    4 |  können | to can, to be able to
    5 |  müssen |  to must, to have to
    6 |  geben  |        to give
    7 |  sollen |  to should, to ought
    8 |  sagen  |         to say
    9 |  wollen |        to want
   10 |  kommen |        to come
   11 |  gehen  |     to go, to walk
   12 |  machen |         to do
   13 |  stehen |        to stand
   14 |  sehen  |         to see
   15 |  finden |        to find
   16 | bleiben |        to stay
   17 |  liegen |         to lie
   18 | stellen |         to put
   19 |  nehmen |        to take
   20 |  dürfen |     to be allowed
   21 | bringen |        to bring
   22 |  halten |        to hold
   23 | spielen |        to play
   24 |  heißen |      to be called
   25 |  wissen |        to know

``memini`` has automatically created a default template matching the ``german_verbs`` table, you can edit it:

.. code:: sh

  $ memini edit german_verbs

This starts the editor (by default it's LibreOffice). You can modify the template, just do not modify the contents of the table.

When you're done, you can generate as many training sheets as you wish running:

.. code:: sh

  memini generate german_verbs

The answers are on the second page.

By default, your table will be filled with 20 lines, but you can specify another number of lines, for instance 10, this way:

.. code:: sh

  memini generate german_verbs -n 10

Also, you can instruct ``memini`` to always hide the same column using schemes (see explanations in the Commands section):

.. code:: sh

  memini generate german_verbs -n 10 -s "*_"

will generate a sheet with a table of 10 lines where the german verbs are always given, and the translations remain blank.



.. code:: sh

  memini generate german_verbs -n 10 -s "_*"

will generate a sheet with a table of 10 lines where the translations in english, this time, are always given, and the german verbs' column remain blank.



Commands
========

You can get help using the ``--help`` option after any command.

Parsing a text file
-------------------

- ``parse myfile.txt "pattern"`` allows to check how a provided text file would be parsed. The pattern will instruct Memini how to separate the different fields in each line of your text file. For instance, say you have a file with latin words and their english translation, separated by a semicolon, like this: `amicitia,  ae, f.: friendship` then you could use this command to parse the file: ``parse myfile.txt "<Latin>:<English>"``. ``parse`` will show possible parsing errors (lines not matching the pattern). To get them all in a clean way, run ``parse --errors-only myfile.txt "<Latin>:<English>"``.

Manage tables
-------------

TABLE represents a table's name.

- ``add TABLE myfile.txt "pattern"`` adds lines to an existing table. The lines are read from myfile.txt that will be parsed using the provided pattern. See the ``parse`` command above about how to write the pattern.
- ``create TABLE myfile.txt "pattern"`` creates a new table and fill it with lines from myfile.txt. See the ``parse`` command above about how to write the pattern.
- ``delete TABLE`` deletes TABLE. Confirmation will be asked before deletion occurs. If the default template still exists, it may be deleted too (confirmation will be asked before).
- ``duplicate TABLE1 TABLE2`` duplicates TABLE1 as TABLE2. The template file matching TABLE1 will be duplicated too.
- ``list tables`` lists all tables.
- ``merge TABLE1 TABLE2 ... TABLEN`` merges TABLE1, TABLE2 etc. to TABLEN. The lines of each table are appended to TABLEN. If TABLEN does not exist yet, it is automatically created.
- ``remove TABLE SPAN`` removes from TABLE all lines matching the provided SPAN. The SPAN refers to the ids of the lines to be removed. It can be provided as a single integer or like a range: 3-6,10 meaning all ids from 3 to 6, plus 10.
- ``rename TABLE1 TABLE2`` renames TABLE1 as TABLE2. The template file matching TABLE1 gets renamed too.
- ``show TABLE`` prints content of TABLE to standard output. The option ``-s`` (or ``--sort``) can be used to print the rows sorted against a particular column. For instance, ``show -s 3 TABLE`` prints TABLE with lines sorted against column number 3.
- ``sort TABLE`` sorts the content of a table. Use the option ``-n`` (or ``--col-nb``) to set the column number against which the sorting should be done. For instance ``sort -n 2 TABLE`` will sort TABLE against column number 2.
- ``update TABLE 'ID | content1 | content2'`` updates the row identified by ID in TABLE. The contents of the cells have to be separated by pipes (the | character) and of course the number of cells must match the number of columns of the table.

Manage templates
----------------

TEMPLATE represents a template's name.

- ``edit TEMPLATE`` opens TEMPLATE in the editor (e.g. LibreOffice).
- ``list templates`` lists all templates.
- ``delete TEMPLATE`` deletes TEMPLATE. Confirmation will be asked before deletion occurs. If a table having the same name does exist too, it may be deleted too (confirmation will be asked before).

Generate a document
-------------------

TABLE represents a table's name, TEMPLATE represents a template's nam and eSW represents a sweepstake's name (see below about sweepstakes).

``generate TABLE`` generates a new document. The lines are drawn randomly from TABLE and the template used is the default one, matching TABLE. By default, after the new document generation, this command will open it with the editor (e.g. LibreOffice).

You can use something called "schemes" in order to control which columns may be left blank. A scheme consists of underscore (_) and star (\*) characters (one of them for each column) and ends with a number. A _ tells the column may be blank, a * tells it will never be blank. The number tells how many  cells per row, at most, will be blank. The exact default scheme depends on the number of columns: for 2 columns it's ``__1``, for 3 columns it's ``___2`` and for 4 columns it's ``____3``. They all mean any cell in a row may be blank; all cells but one will be blank.

Scheme examples:

- if you have a table of 3 columns and you wish the two last columns to always be blank, use ``*__2``.
- if you have 2 columns and you wish the first one to be always blank and the second one always filled, then use ``_*1``.

A number of options gives you more control on the document generation:

- ``-n, --questions-number`` lets you define the number of lines of the new document's table.
- ``-o, --output`` lets you define the output document's path. By default it is in the current directory and the name will be the same as the default template.
- ``-f, --force`` lets the output file be overwritten without asking, if is already exists.
- ``-e, --edit`` defines whether the editor will be run after document generation.
- ``-t, --template`` lets you use another template than the default one. Any template will do, provided it has as many columns as the table to be used.
- ``-s, --scheme`` defines the scheme to be used.
- ``--use-previous`` lets you use the data from a previous sweepstake. It is useful to generate a new document from another template than the first one, but with the same data.

Examples of document generation:

- ``generate -n 10 -o test_2020_regular.odt latin_vocabulary_nth_grade`` will generate a document with a table of 10 lines. The scheme will be the default one: in each row, all cells will be blank, but one. The table to be used is ``latin_vocabulary_nth_grade``. The output file is ``test_2020_regular.odt``.

- ``generate -s *_1 -o test_2020_easier.odt --use-previous`` will generate a document using the previous data drawn, but this time, the first cell at left will always be written and the second right, at right, always blank. The output file is ``test_2020_easier.odt``. No name for a table to use is provided as the ``--use-previous`` flag is on. As no value at all is provided, the most recent sweepstake is used (the data generated from previous call). It would be possible to specify another swwepstake to use then the most recent one, like in ``generate -s *_1 -o test_2020_easier.odt --use-previous 3``.

- ``generate -n 5 -o exam_2020.odt -t exam_sheet -s *_1 exam_1st_year`` will generate a document with a table of 5 lines, the first cell at left will always be written and the second right, at right, always blank. The table to be used is ``exam_1st_year`` while the template is named ``exam_sheet``. The output file is ``exam_2020.odt``.

- ``generate -n 30 -s __*1 german_verbs`` will generate a document with a table of 30 lines, the last cell at right will always be given and one among the two left cells will be blanked. The table to be used is ``german_verbs`` and as the template's name is not defined, it will be ``german_verbs`` too. The output file, not defined either, will be ``german_verbs.odt``.


Consult sweepstakes
-------------------

Any time a new document is created, the associated drawn lines are stored in something called a "sweepstake". By default 9 sweepstakes maximum are recorded, numbered from 1 (the most recent) to 9 (the older one). It is possible to reuse a sweepstake when generating a new document. This makes possible, for instance, to generate the same sheet with different schemes, layouts or fonts (e.g. one with the regular font, another one with OpenDyslexic). The sweepstakes commands only allow to consult them.

SW represents a sweepstake's name.

- ``dump SW`` prints content of a sweepstake to standard output.
- ``list sweepstakes`` lists all sweepstakes.


Contribute
==========

Any question can be sent to nh dot techn (hosted at gmail dot com).

.. include:: ../CHANGELOG.rst
