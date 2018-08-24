## Dropfactory Exploration

This repository is associated to the paper "A soft matter discovery robot driven by child-like curiosity" by Jonathan Grizou, Laurie J. Points, Abhishek Sharma and Leroy Cronin. A draft version of the paper is [available on Chemarxiv](https://chemrxiv.org/articles/A_Closed_Loop_Discovery_Robot_Driven_by_a_Curiosity_Algorithm_Discovers_Proto-Cells_That_Show_Complex_and_Emergent_Behaviours/6958334).

This repository contains the code used to run closed-loop droplet experiments using the curiosity algorithm.

## Repository Organization

All experiments are performed under the [real_experiments](/realworld_experiments) folder.

## Associated repositories

- The robotic platform hardware and code is described at https://github.com/croningp/dropfactory

- The code to analyse the experiments and reproduce the plots in the paper and SI are available at https://github.com/croningp/dropfactory_analysis

- The droplet tracking code is available at https://github.com/croningp/chemobot_tools

- Libraries developed to build and control the robotic platform are: [commanduino](https://github.com/croningp/commanduino), [pycont](https://github.com/croningp/pycont), [ModularSyringeDriver](https://github.com/croningp/ModularSyringeDriver), [Arduino-CommandTools](https://github.com/croningp/Arduino-CommandTools), and [Arduino-CommandHandler](https://github.com/croningp/Arduino-CommandHandler)

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

## Author

[Jonathan Grizou](http://jgrizou.com/) while working in the [CroninGroup](http://www.chem.gla.ac.uk/cronin/).

## License

[![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl.html)
