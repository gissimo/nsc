# Nearest Subclass Classifier

Python implementation of the Nearest Subclass Classifier (NSC), based on Maximum Variance Clusters (MVC).

The classification algorithm is based on the work published in the papers:

* The nearest subclass classifier: a compromise between the nearest mean and nearest neighbor classifier ([Veenman and Reinders, 2005](https://doi.org/10.1109/TPAMI.2005.187)).

* A maximum variance cluster algorithm ([Veenman, Reinders, Backer, 2002](https://doi.org/10.1109/TPAMI.2002.1033218)).

Follows a brief description of how the scripts work, however probably nothing of this is going to help you much unless you are already familiar with the algorithm.

- **do_mvc.py** creates the prototypes from a text file. Requires as inputs:
	1. filename
	2. value of *sigma-square-max*
	3. column separator
	4. position of class identifier within the line
- **do_nsc.py** classifies points from a file, given a file with prototypes. Requires as inputs:
	1. file of non-classified points
	2. prototypes file
	3. column separator
- **do_cross.py** finds the optimal value of *sigma-square-max*. Requires as inputs:
	1. file with points
	2. number of iterations
	3. column separator
	4. position of class identifier within the line
- **do_test.py** tests NSC/MVC on a set of already-classified points. Requires as inputs:
	1. file with points
	2. value of *sigma-square-max*
	3. column separator
	4. position of class identifier within the line

More details (in Italian) [here](http://spotted.cat/web.giorgiostampa.eu/Classificazione_per_prossimita.html).
