>This repository is associated to the paper "A soft matter discovery robot driven by child-like curiosity" by Jonathan Grizou, Laurie J. Points, Abhishek Sharma and Leroy Cronin. A draft version of the paper is [available on Chemarxiv](https://chemrxiv.org/articles/A_Closed_Loop_Discovery_Robot_Driven_by_a_Curiosity_Algorithm_Discovers_Proto-Cells_That_Show_Complex_and_Emergent_Behaviours/6958334) and a brief overview of the scientific approach can be found at https://croningp.github.io/tutorial_icdl_epirob_2017/.

# Dropfactory Exploration

Code used to run closed-loop droplet experiments using the curiosity (and other) algorithms.

[![Dropfactory_Station](https://github.com/croningp/dropfactory/raw/master/media/gif/dropfactory_stations_speedup.gif)](https://youtu.be/bY5OoRBJkf0)

## Principles

The principles are described in details in the [Supportng Information of the paper section 2.1.3 starting p83](https://ndownloader.figshare.com/files/12759725). The guiding principles are as follow:

A full experimental run of 1000 experiments require three steps: 

1. **Perform  experiments** on  the  droplet  system.  This  task  is  given  to  the  [Dropfactory platform](https://github.com/croningp/dropfactory).  Dropfactory  has  only  one  role,  it  looks  for  experiments  (in  the  form  of  a params.json file) to run in a specific folder and executes them. It then saves a video of the experiment as a video.avi file and an information file in the form of a run_info.json file with time, temperature and humidity information. This process is operated by the [realworld_experiments/dropfactory_watch_folder.py](realworld_experiments/dropfactory_watch_folder.py) script in this repository.

2. **Analyse  the  results  of  the  experiments.**  This  task  is  given  to  a specific,  standalone  and  independent  software  running  in  its  own  thread.  This  process  looks  for  droplet videos  (in  the  form  of  video.avi  files)  in  a  specific  folder  (typically  generated  by  the  platform  once  an  experiment  is  finalized)  and  process  the  file  in  three  steps.  It  first  extract frame by frame the contour of each droplets, then attempt to stitch together the droplet in each frame as time sequences and finally computes a bunch of metrics about the droplet motion in the form of a features.json file. See section 2.1.5 title “Droplet Tracking” of the SI and https://github.com/croningp/chemobot_tools. This process is operated by the [realworld_experiments/vision_watch_folder.py](realworld_experiments/vision_watch_folder.py) script in this repository.

3. **Decide on what experiment to do next.**  This task is given to a specific, standalone and independent software running in its own thread. This process looks for droplet features files  (typically  generated  by  the  video  droplet  tracking in  the  form  of  a  features.jsonfile)  and  an  experimental  parameter  files in  a  specific  folder.  It  gathers  all  this  information and, depending on the algorithm selected, output a new experimental file (params.jsonfile) for         the         platform         to         execute. This process is operated by the [explauto_watch_folder.py](explauto_watch_folder.py) script in this repository.

## Repository Organization

Top-level scripts used to start experiments on the platform:
- [create_xp.py](create_xp.py) is the script used to create a folder with a configuration file representing an exeprimental run. This configuration file will contains the random seed, the algorithm type and parameters, as well as the number and configuration of droplet experiments.
- [realworld_experiments/dropfactory_watch_folder.py](realworld_experiments/dropfactory_watch_folder.py) is the script that watch a folder for new droplet experiments (from the algorithm) and send them to the Dropfactory platform, which will output a video of the experiments.
- [realworld_experiments/vision_watch_folder.py](realworld_experiments/vision_watch_folder.py) is the script that watch a folder for new droplet videos (from the Dropfacotry platform) and send them to the droplet tracking software, which will ouput metrics about the droplet motion.
- [explauto_watch_folder.py](explauto_watch_folder.py) is the script that watch a folder for new experimental observation (from the droplet tracking) and send them to the algorithm as new data, which will output a new droplet experiment parameters to be run on the Dropfactory platform.

[An early practical guide to launch and monitor experiments](https://github.com/croningp/dropfactory_exploration/releases/download/protocol/Dropfactory_protocol.pdf) is also available in the [protocol release](https://github.com/croningp/dropfactory_exploration/releases/tag/protocol). It might be slighlty out of date but will point in the right direction with guiding principles.

Folders usage:
- [datasets](datasets) folder contains data from previous work used to develop the code architecture and for debugging. When developping or debugging, the datasets are used to train a model that is used instead of running experiments on the Dropfacotry platform.
- [explauto_tools](explauto_tools) folder holds the code interfacing our work with the [explauto library](https://github.com/flowersteam/explauto), for examples to define an environment, setup an experiment and run the selected algortihm to generate the next experiments.
- [models](models) folder holds the regression methods used to generate a model from the data stored in the [datasets](datasets) folder. The model is used to speed up developping and debugging by bypassing the robotic platform.
- [realworld_experiments](realworld_experiments) folder is where real droplet experiments performed on the platform are geenrated and stored.
- [simulated_experiments](simulated_experiments) folder is where experiments are simulated using the model for developing and debugging, it is a simple way to test the code without having access to the robot.
- [tune_explauto_parameters](tune_explauto_parameters) folder was used to select the best parameters for the various algorithms by running experiments against our model.
- [utils](utils) contains a set of python tools useful for this work. Among them is [utils/watcher.py](utils/watcher.py) that monitor folder to check for new data (e.g. a new droplet video) and the [utils/xp_utils.py](utils/xp_utils.py) that contains tools to generate, monitor and extract experimental results in the correct location.

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
Version: sklearn.__version__ is '0.19.1'

- [explauto](https://github.com/jgrizou/explauto) is the modified version of the explauto library from the Flowers Team (https://github.com/flowersteam/explauto) for the prupose of this research.

- [filetools](https://github.com/jgrizou/filetools) is a simple file management library

- [dropfactory](https://github.com/croningp/dropfactory) should be installed and placed at the same level as the repository

## Author

[Jonathan Grizou](http://jgrizou.com/) while working in the [CroninGroup](http://www.chem.gla.ac.uk/cronin/).

## License

[![GPL V3](https://www.gnu.org/graphics/gplv3-127x51.png)](https://www.gnu.org/licenses/gpl.html)
