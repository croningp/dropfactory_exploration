## Dropfactory Exploration

This code is associated to the paper "A soft matter discovery robot driven by child-like curiosity" by Jonathan Grizou, Laurie J. Points, Abhishek Sharma and Leroy Cronin. It contains the code used to run closed-loop droplet experiments using the curiosity algorithm.

All experiments are performed under the [real_experiments](/realworld_experiments) folder.

## Associated repositories

- The robotic platform is fully described in https://github.com/croningp/dropfactory

- The code to analyse the expeirment and reproduce the plots in the paper and SI are available in https://github.com/croningp/dropfactory_analysis


## Dependencies

This code has been tested under Python 2.7.6 on Ubuntu 14.04 LTS. Despite all our efforts, we cannot guarantee everything will be executable on other OS or Python version.

Aside from the standard libraries, we are using the following libraries. You do not have to install them all, it depends on the task you are performing.

- [opencv](http://opencv.org/): Image analysis with python binding.
Version: cv2.__version__ is '2.4.8'

- [numpy](http://www.numpy.org/): Scientific computing in Python.
Version: numpy.__version__ is '1.10.4'

- [scipy](http://www.scipy.org/scipylib/index.html): More scientific computing in Python.
Version: scipy.__version__ is '0.16.1'

- [sklearn](http://scikit-learn.org/): Machine Learning in Python.
Version: sklearn.__version__ is '0.16.1'

- [explauto](https://github.com/jgrizou/explauto) is the modified version of the explauto library from the Flowers Team (https://github.com/flowersteam/explauto) for the prupose of this research.

- [filetools](https://github.com/jgrizou/filetools) is a simple file management library

- [dropfactory](https://github.com/croningp/dropfactory) should be installed and placed at the same level as the repository
